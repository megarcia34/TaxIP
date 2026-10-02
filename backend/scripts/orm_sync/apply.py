"""
apply.py - Generador de borradores para reconciliacion ORM <-> DB.

Lee docs/orm_sync/orm_diff.json (salida de diff.py) y genera archivos
markdown con el codigo Python propuesto para alinear app/models/*.py
con la DB.

NO reescribe archivos .py del ORM. Solo genera borradores para revision
y pegado manual.

Modos:
    --stats                    Muestra estadisticas.
    --report                   Lista los items (sin generar codigo).
    --generate FILE            Genera borrador para un archivo del ORM.
    --dry-run                  No escribe nada (default true).

Filtros:
    --filter-schema SCHEMA     Solo items del schema indicado.
    --filter-tier N            Solo items de tier N.
    --filter-clasif C          Solo items de clasificacion C.

Uso:
    python apply.py --stats
    python apply.py --report --filter-schema fleet
    python apply.py --generate app/models/trip.py
    python apply.py --generate app/models/fleet.py --filter-tier 1

Reglas:
    - Codigo Python generado: ASCII puro (N10).
    - Comments (strings al usuario final): UTF-8 permitido (N10, excepcion).
    - No modifica archivos .py del ORM.
    - Los borradores van a docs/orm_sync/borradores/.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
DIFF_JSON = REPO_ROOT / "docs" / "orm_sync" / "orm_diff.json"
BORRADORES_DIR = REPO_ROOT / "docs" / "orm_sync" / "borradores"

MAPEO_TIPOS = {
    "uuid": "UUID(as_uuid=True)",
    "varchar": "String",
    "character varying": "String",
    "text": "Text",
    "integer": "Integer",
    "int4": "Integer",
    "bigint": "BigInteger",
    "int8": "BigInteger",
    "smallint": "SmallInteger",
    "int2": "SmallInteger",
    "boolean": "Boolean",
    "bool": "Boolean",
    "numeric": "Numeric",
    "decimal": "Numeric",
    "double precision": "Float",
    "float8": "Float",
    "real": "Float",
    "float4": "Float",
    "timestamp without time zone": "DateTime(timezone=False)",
    "timestamp with time zone": "DateTime(timezone=True)",
    "timestamp": "DateTime(timezone=False)",
    "timestamptz": "DateTime(timezone=True)",
    "date": "Date",
    "time": "Time",
    "jsonb": "JSONB",
    "json": "JSON",
    "bytea": "LargeBinary",
    "geometry": "Geometry",
    "geography": "Geography",
}

MAPEO_PYTHON = {
    "uuid": "uuid.UUID",
    "varchar": "str",
    "character varying": "str",
    "text": "str",
    "integer": "int",
    "int4": "int",
    "bigint": "int",
    "int8": "int",
    "smallint": "int",
    "int2": "int",
    "boolean": "bool",
    "bool": "bool",
    "numeric": "float",
    "decimal": "float",
    "double precision": "float",
    "float8": "float",
    "real": "float",
    "float4": "float",
    "timestamp without time zone": "datetime",
    "timestamp with time zone": "datetime",
    "timestamp": "datetime",
    "timestamptz": "datetime",
    "date": "date",
    "time": "time",
    "jsonb": "dict",
    "json": "dict",
    "bytea": "bytes",
    "geography": "Geography",
    "geometry": "Geometry",
}

CLASIF_AUTOMATIZABLES = {
    "columna_falta",
    "tipo_desalineado",
    "nullable_desalineado",
    "indice_falta",
    "indice_sobra",
    "indice_nombre_desalineado",
    "constraint_falta",
    "constraint_sobra",
    "constraint_nombre_desalineado",
    "comment_desalineado",
}

CLASIF_MANUALES = {
    "tabla_falta",
    "tabla_sobra",
    "schema_falta",
    "constraint_desalineada",
    "columna_sobra",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_dict(d):
    """Devuelve d si es dict, {} en cualquier otro caso (None, lista, etc)."""
    return d if isinstance(d, dict) else {}


def safe_str(s):
    """Convierte a string, preservando UTF-8. None -> ''."""
    if s is None:
        return ""
    return str(s)


def es_default_now(default):
    """True si el default de DB es now() (o equivalente)."""
    if not default:
        return False
    d = str(default).strip().lower()
    return d in ("now()", "current_timestamp", "current_timestamp()")


def es_timestamp(base_type):
    return "timestamp" in (base_type or "").lower()


def es_not_null_autogen(nombre):
    """True si el nombre del constraint es un not_null autogenerado."""
    if not nombre:
        return False
    return "_not_null" in nombre.lower() and any(ch.isdigit() for ch in nombre)


# ---------------------------------------------------------------------------
# Carga y filtros
# ---------------------------------------------------------------------------

def cargar_diff(path):
    if not path.exists():
        print(f"[ERROR] No existe {path}", file=sys.stderr)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("diferencias", [])


def filtrar_items(items, args):
    out = items
    if args.filter_schema:
        out = [x for x in out if x.get("schema") == args.filter_schema]
    if args.filter_tier is not None:
        out = [x for x in out if x.get("tier") == args.filter_tier]
    if args.filter_clasif:
        out = [x for x in out if x.get("clasificacion") == args.filter_clasif]
    return out


def archivo_orm(schema, tabla):
    mapa = {
        "trip": "app/models/trip.py",
        "fleet": "app/models/fleet.py",
        "auth": "app/models/auth.py",
        "tenant": "app/models/tenant.py",
        "payment": "app/models/payment.py",
        "public": "app/models/public.py",
        "corporate": "app/models/corporate.py",
        "audit": "app/models/audit.py",
        "geo": "app/models/geo.py",
        "notification": "app/models/notification.py",
        "comunicacion": "app/models/comunicacion.py",
        "rentabilidad": "app/models/rentabilidad.py",
    }
    return mapa.get(schema, f"app/models/{schema}.py")


def agrupar_por_archivo(items):
    grupos = defaultdict(list)
    for x in items:
        archivo = archivo_orm(x.get("schema", ""), x.get("tabla", ""))
        grupos[archivo].append(x)
    return dict(grupos)


# ---------------------------------------------------------------------------
# Mapeo de tipos
# ---------------------------------------------------------------------------

def mapear_tipo_sqlalchemy(det_db):
    det_db = safe_dict(det_db)
    base_type = (det_db.get("base_type") or "").lower()
    sqlalchemy_type = MAPEO_TIPOS.get(base_type, "String")

    if "String" in sqlalchemy_type and det_db.get("character_maximum_length"):
        return f"String({det_db['character_maximum_length']})"

    if "Numeric" in sqlalchemy_type and det_db.get("numeric_precision"):
        p = det_db["numeric_precision"]
        s = det_db.get("numeric_scale") or 0
        return f"Numeric({p}, {s})"

    return sqlalchemy_type


def mapear_tipo_python(det_db):
    det_db = safe_dict(det_db)
    base_type = (det_db.get("base_type") or "").lower()
    return MAPEO_PYTHON.get(base_type, "str")


# ---------------------------------------------------------------------------
# Generadores
# ---------------------------------------------------------------------------

def gen_columna_falta(item):
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    col = item.get("columna", "")

    tipo_sqla = mapear_tipo_sqlalchemy(det_db)
    tipo_py = mapear_tipo_python(det_db)
    nullable = det_db.get("nullable", True)
    default_db = det_db.get("default")
    comment = safe_str(det_db.get("comment"))

    if nullable:
        anotacion = f"Mapped[Optional[{tipo_py}]]"
    else:
        anotacion = f"Mapped[{tipo_py}]"

    args = [tipo_sqla]
    if not nullable:
        args.append("nullable=False")
    elif nullable is True:
        args.append("nullable=True")

    if es_default_now(default_db) and es_timestamp(det_db.get("base_type")):
        args.append("server_default=func.now()")

    if comment:
        # Comments: UTF-8 permitido (strings al usuario final, excepcion N10)
        args.append(f'comment="{comment}"')

    args_str = ",\n    ".join(args)

    return "\n".join([
        f"# Item {item.get('id', '?')}: agregar columna {col}",
        f"{col}: {anotacion} = mapped_column(",
        f"    {args_str},",
        f")",
        "",
    ])


def gen_tipo_desalineado(item):
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    det_orm = safe_dict(detalle.get("orm"))
    col = item.get("columna", "")

    tipo_orm_real = det_orm.get("type") or det_orm.get("base_type") or "?"
    tipo_db_real = det_db.get("type") or det_db.get("base_type") or "?"
    tipo_sqla_db = mapear_tipo_sqlalchemy(det_db)
    tipo_py_db = mapear_tipo_python(det_db)

    return "\n".join([
        f"# Item {item.get('id', '?')}: tipo desalineado",
        f"# {item.get('schema','')}.{item.get('tabla','')}.{col}",
        f"# ORM: {tipo_orm_real}",
        f"# DB:  {tipo_db_real}",
        f"# Objetivo SQLAlchemy: {tipo_sqla_db}",
        f"# Anotacion: Mapped[{tipo_py_db}]",
        "",
    ])


def gen_nullable_desalineado(item):
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    det_orm = safe_dict(detalle.get("orm"))
    col = item.get("columna", "")
    nullable_db = det_db.get("nullable")
    nullable_orm = det_orm.get("nullable")

    return "\n".join([
        f"# Item {item.get('id', '?')}: nullable desalineado",
        f"# {item.get('schema','')}.{item.get('tabla','')}.{col}",
        f"# ORM: nullable={nullable_orm}",
        f"# DB:  nullable={nullable_db}",
        f"# Ajustar en ORM a nullable={nullable_db}",
        "",
    ])


def gen_indice_falta(item):
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    nombre = det_db.get("name") or item.get("columna") or "indice"
    schema = item.get("schema", "")
    tabla = item.get("tabla", "")

    return "\n".join([
        f"# Item {item.get('id', '?')}: indice faltante",
        f"# {schema}.{tabla}",
        f'# Agregar en __table_args__:',
        f'Index("{nombre}", ...),',
        "",
    ])


def gen_indice_sobra(item):
    detalle = safe_dict(item.get("detalle"))
    det_orm = safe_dict(detalle.get("orm"))
    det_db = safe_dict(detalle.get("db"))
    nombre = det_orm.get("name") or det_db.get("name") or "indice"

    return "\n".join([
        f"# Item {item.get('id', '?')}: indice sobrante (eliminar del ORM)",
        f"# Nombre: {nombre}",
        f"# Quitar del __table_args__ correspondiente.",
        "",
    ])


def gen_indice_nombre(item):
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    det_orm = safe_dict(detalle.get("orm"))
    nombre_db = det_db.get("name") or "?"
    nombre_orm = det_orm.get("name") or "?"
    schema = item.get("schema", "")

    return "\n".join([
        f"# Item {item.get('id', '?')}: renombrar indice",
        f"# ALTER INDEX {schema}.{nombre_orm} RENAME TO {nombre_db};",
        "",
    ])


def gen_constraint_falta(item):
    """Genera codigo real para UNIQUE/FK, marca CHECK/NOT NULL como manual."""
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    nombre = det_db.get("name") or "?"
    definicion = safe_str(det_db.get("definition") or det_db.get("constraint_def"))
    schema = item.get("schema", "")
    tabla = item.get("tabla", "")

    # NOT NULL autogenerado: se resuelve con nullable=False en la columna.
    if es_not_null_autogen(nombre):
        return "\n".join([
            f"# Item {item.get('id', '?')}: {nombre}",
            f"# {schema}.{tabla}",
            f"# {definicion}",
            f"# NOT NULL autogenerado: se resuelve con nullable=False en la columna.",
            f"# NO declarar en __table_args__.",
            "",
        ])

    # UNIQUE
    if nombre.startswith("uq_") or "UNIQUE" in definicion.upper():
        # Extraer columnas de la definicion: UNIQUE (col1, col2)
        cols = _extraer_columnas_unique(definicion)
        return "\n".join([
            f"# Item {item.get('id', '?')}: constraint UNIQUE faltante",
            f"# {schema}.{tabla}",
            f"# Nombre: {nombre}",
            f"# Definicion DB: {definicion}",
            f"# Agregar en __table_args__:",
            f"UniqueConstraint({cols}, name=\"{nombre}\"),",
            "",
        ])

    # FOREIGN KEY
    if nombre.startswith("fk_") or "FOREIGN KEY" in definicion.upper():
        ref = _extraer_ref_fk(definicion)
        return "\n".join([
            f"# Item {item.get('id', '?')}: constraint FK faltante",
            f"# {schema}.{tabla}",
            f"# Nombre: {nombre}",
            f"# Definicion DB: {definicion}",
            f"# Declarar en la columna correspondiente:",
            f"# ForeignKey(\"{ref}\", ondelete=\"...\"),",
            "",
        ])

    # CHECK: manual (requiere expresion SQL)
    if nombre.startswith("ck_") or "CHECK" in definicion.upper():
        return "\n".join([
            f"# Item {item.get('id', '?')}: constraint CHECK faltante",
            f"# {schema}.{tabla}",
            f"# Nombre: {nombre}",
            f"# Definicion DB: {definicion}",
            f"# MANUAL: declarar en __table_args__ como CheckConstraint.",
            f"# CheckConstraint(\"...\", name=\"{nombre}\"),",
            "",
        ])

    # Desconocido
    return "\n".join([
        f"# Item {item.get('id', '?')}: constraint faltante (tipo desconocido)",
        f"# {schema}.{tabla}",
        f"# Nombre: {nombre}",
        f"# Definicion DB: {definicion}",
        f"# MANUAL: revisar y declarar en __table_args__.",
        "",
    ])


def _extraer_columnas_unique(definicion):
    """Extrae columnas de 'UNIQUE (col1, col2)' -> 'col1, col2'."""
    if not definicion:
        return "..."
    s = definicion.upper()
    if "UNIQUE" not in s:
        return "..."
    try:
        dentro = definicion.split("(", 1)[1].rsplit(")", 1)[0]
        cols = [c.strip().strip('"') for c in dentro.split(",")]
        return ", ".join(f'"{c}"' for c in cols)
    except Exception:
        return "..."


def _extraer_ref_fk(definicion):
    """Extrae 'tabla.col' de 'FOREIGN KEY (col) REFERENCES tabla(col)'."""
    if not definicion:
        return "..."
    try:
        partes = definicion.upper().split("REFERENCES")
        if len(partes) < 2:
            return "..."
        ref = partes[1].strip()
        # ref = 'tabla(col) ON DELETE ...'
        ref = ref.split("(")[0].strip()
        return ref + ".id"
    except Exception:
        return "..."


def gen_constraint_sobra(item):
    detalle = safe_dict(item.get("detalle"))
    det_orm = safe_dict(detalle.get("orm"))
    nombre = det_orm.get("name") or "?"
    columns = det_orm.get("columns")
    definition = safe_str(det_orm.get("definition"))

    lineas = [
        f"# Item {item.get('id', '?')}: constraint sobrante en ORM (eliminar)",
        f"# {item.get('schema','')}.{item.get('tabla','')}",
        f"# Nombre: {nombre}",
    ]
    if columns:
        lineas.append(f"# Columnas: {columns}")
    if definition:
        lineas.append(f"# Definicion: {definition}")
    lineas.append("# Quitar del __table_args__ de la clase correspondiente.")
    lineas.append("")

    return "\n".join(lineas)


def gen_constraint_nombre(item):
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    det_orm = safe_dict(detalle.get("orm"))
    nombre_db = det_db.get("name") or "?"
    nombre_orm = det_orm.get("name") or "?"
    tabla = item.get("tabla", "")
    schema = item.get("schema", "")

    return "\n".join([
        f"# Item {item.get('id', '?')}: renombrar constraint",
        f"# ALTER TABLE {schema}.{tabla} RENAME CONSTRAINT {nombre_orm} TO {nombre_db};",
        "",
    ])


def gen_comment_desalineado(item):
    detalle = safe_dict(item.get("detalle"))
    det_db = safe_dict(detalle.get("db"))
    comment_db = safe_str(det_db.get("comment"))
    col = item.get("columna", "")

    return "\n".join([
        f"# Item {item.get('id', '?')}: comment desalineado",
        f"# {item.get('schema','')}.{item.get('tabla','')}.{col}",
        f'# comment="{comment_db}"',
        "",
    ])


GENERADORES = {
    "columna_falta": gen_columna_falta,
    "tipo_desalineado": gen_tipo_desalineado,
    "nullable_desalineado": gen_nullable_desalineado,
    "indice_falta": gen_indice_falta,
    "indice_sobra": gen_indice_sobra,
    "indice_nombre_desalineado": gen_indice_nombre,
    "constraint_falta": gen_constraint_falta,
    "constraint_sobra": gen_constraint_sobra,
    "constraint_nombre_desalineado": gen_constraint_nombre,
    "comment_desalineado": gen_comment_desalineado,
}


# ---------------------------------------------------------------------------
# Reportes
# ---------------------------------------------------------------------------

def report_stats(items):
    print("=== apply.py stats ===")
    print()
    print(f"Total items en orm_diff.json: {len(items)}")
    print()

    por_clasif = Counter(x.get("clasificacion", "?") for x in items)
    print("Por clasificacion:")
    for k, v in por_clasif.most_common():
        marca = "[auto]" if k in CLASIF_AUTOMATIZABLES else "[manual]"
        print(f"  {v:5d}  {marca}  {k}")
    print()

    automatizables = [x for x in items if x.get("clasificacion") in CLASIF_AUTOMATIZABLES]
    manuales = [x for x in items if x.get("clasificacion") in CLASIF_MANUALES]
    otros = len(items) - len(automatizables) - len(manuales)
    print(f"Automatizables: {len(automatizables)}")
    print(f"Manuales:       {len(manuales)}")
    print(f"Otros:          {otros}")
    print()

    grupos = agrupar_por_archivo(automatizables)
    print("Automatizables por archivo ORM:")
    for archivo, its in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(its):5d}  {archivo}")
    print()


def report_listado(items):
    for x in items:
        col = x.get("columna") or ""
        print(f"{x.get('id', '?'):8s} | T{x.get('tier', '?')} | "
              f"{x.get('clasificacion', '?'):30s} | "
              f"{x.get('schema', '')}.{x.get('tabla', '')}.{col}")


# ---------------------------------------------------------------------------
# Escritura de borradores
# ---------------------------------------------------------------------------

def escribir_borrador(archivo_orm, items):
    BORRADORES_DIR.mkdir(parents=True, exist_ok=True)

    base = archivo_orm.replace("/", "_").replace(".py", "").replace("app_models_", "")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    nombre = f"{base}_{timestamp}.md"
    path = BORRADORES_DIR / nombre

    por_clasif = defaultdict(list)
    for x in items:
        if x.get("clasificacion") in CLASIF_AUTOMATIZABLES:
            por_clasif[x["clasificacion"]].append(x)

    lineas = []
    lineas.append(f"# Borrador para {archivo_orm}")
    lineas.append("")
    lineas.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lineas.append(f"**Items automatizables:** {sum(len(v) for v in por_clasif.values())}")
    lineas.append(f"**Items totales en el archivo:** {len(items)}")
    lineas.append("")
    lineas.append("**NO incluye:** items manuales (constraint_desalineada, "
                   "tablas faltantes, schemas, columna_sobra). "
                   "Ver orm_plan_aplicacion.md.")
    lineas.append("")
    lineas.append("---")
    lineas.append("")

    for clasif in sorted(por_clasif.keys()):
        its = por_clasif[clasif]
        lineas.append(f"## {clasif} ({len(its)})")
        lineas.append("")

        generador = GENERADORES.get(clasif)
        if not generador:
            lineas.append("(sin generador)")
            lineas.append("")
            continue

        for x in its:
            try:
                lineas.append("```python")
                lineas.append(generador(x).rstrip())
                lineas.append("```")
                lineas.append("")
            except Exception as e:
                lineas.append(f"(error generando {x.get('id', '?')}: {e})")
                lineas.append("")

    manuales = [x for x in items if x.get("clasificacion") in CLASIF_MANUALES]
    if manuales:
        lineas.append("## Items manuales (referencia, no automatizables)")
        lineas.append("")
        for x in manuales:
            col = x.get("columna") or ""
            lineas.append(f"- {x.get('id', '?')} | "
                          f"{x.get('schema', '')}.{x.get('tabla', '')}.{col} | "
                          f"{x.get('clasificacion', '')}")
        lineas.append("")

    contenido = "\n".join(lineas)
    # NO aplicar ascii_str al contenido completo: los comments pueden tener UTF-8.
    # Solo aseguramos que el archivo se guarde en UTF-8.

    with path.open("w", encoding="utf-8") as f:
        f.write(contenido)

    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generador de borradores para reconciliacion ORM <-> DB."
    )
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--generate", metavar="FILE")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--filter-schema", metavar="SCHEMA")
    parser.add_argument("--filter-tier", type=int, metavar="N")
    parser.add_argument("--filter-clasif", metavar="C")
    args = parser.parse_args()

    items = cargar_diff(DIFF_JSON)
    items = filtrar_items(items, args)

    if args.stats:
        report_stats(items)
        return

    if args.report:
        report_listado(items)
        return

    if args.generate:
        grupos = agrupar_por_archivo(items)
        if args.generate not in grupos:
            print(f"[ERROR] No hay items para {args.generate}", file=sys.stderr)
            print(f"Disponibles: {sorted(grupos.keys())}", file=sys.stderr)
            sys.exit(1)
        path = escribir_borrador(args.generate, grupos[args.generate])
        print(f"[OK] Borrador generado: {path}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()