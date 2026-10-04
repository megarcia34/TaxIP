"""
filtrar_check.py - Lista solo los constraint_falta que son CHECK reales
(no *_not_null autogenerados).

Lee docs/orm_sync/orm_diff.json (salida de diff.py) y filtra los items
de clasificacion constraint_falta, descartando los *_not_null autogenerados
por Alembic (que se resuelven via nullable=False en la columna, no via
__table_args__).

Clasifica los restantes por subtipo:
    - check   (nombre empieza con ck_ o definicion contiene CHECK)
    - unique  (nombre empieza con uq_ o definicion contiene UNIQUE)
    - fk      (nombre empieza con fk_ o definicion contiene FOREIGN KEY)
    - pk      (nombre empieza con pk_ o definicion contiene PRIMARY KEY)
    - other   (no matchea ninguno)

Modos:
    --stats                    Resumen por subtipo y por archivo ORM.
    --report                   Lista todos los items filtrados.
    --json                     Salida JSON estructurada (para scripts).

Filtros:
    --schema SCHEMA            Solo items del schema indicado.
    --tier N                   Solo items de tier N.
    --subtipo SUBTIPO          Solo items del subtipo indicado.
    --archivo FILE             Solo items que van a ese archivo del ORM.

Uso:
    python filtrar_check.py --stats
    python filtrar_check.py --report --subtipo check
    python filtrar_check.py --report --schema fleet --subtipo check
    python filtrar_check.py --json --subtipo check > checks.json

Reglas:
    - Solo lectura. No modifica el ORM ni la DB.
    - Codigo Python: ASCII puro (N10).
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DIFF_JSON = REPO_ROOT / "docs" / "orm_sync" / "orm_diff.json"

# Mismo mapeo que apply.py. Si cambia alla, cambiar aca.
MAPA_TABLA_A_ARCHIVO = {
    ("fleet", "turno_chofer"): "app/models/turno.py",
    ("fleet", "gasto_turno"): "app/models/gasto_turno.py",
    ("fleet", "liquidacion"): "app/models/liquidacion.py",
    ("fleet", "liquidacion_ajuste"): "app/models/liquidacion.py",
    ("fleet", "liquidacion_detalle"): "app/models/liquidacion.py",
    ("fleet", "liquidacion_estado_historial"): "app/models/liquidacion.py",
    ("trip", "foto_viaje"): "app/models/foto_viaje.py",
}

MAPA_SCHEMA_A_ARCHIVO = {
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

# Regex para *_not_null autogenerados por Alembic.
# Ejemplos: 63669_63825_1_not_null, 12345_67890_42_not_null
RE_NOT_NULL_AUTOGEN = re.compile(r"^\d+_\d+_\d+_not_null$", re.IGNORECASE)


def archivo_orm(schema, tabla):
    key = (schema, tabla)
    if key in MAPA_TABLA_A_ARCHIVO:
        return MAPA_TABLA_A_ARCHIVO[key]
    return MAPA_SCHEMA_A_ARCHIVO.get(schema, f"app/models/{schema}.py")


def es_not_null_autogen(nombre):
    if not nombre:
        return False
    return bool(RE_NOT_NULL_AUTOGEN.match(nombre))


def clasificar_subtipo(nombre, definicion):
    n = (nombre or "").lower()
    d = (definicion or "").upper()

    if n.startswith("ck_") or "CHECK" in d:
        return "check"
    if n.startswith("uq_") or "UNIQUE" in d:
        return "unique"
    if n.startswith("fk_") or "FOREIGN KEY" in d:
        return "fk"
    if n.startswith("pk_") or "PRIMARY KEY" in d:
        return "pk"
    return "other"


def cargar_items(path):
    if not path.exists():
        print(f"[ERROR] No existe {path}", file=sys.stderr)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("diferencias", [])


def extraer_nombre_definicion(item):
    """Devuelve (nombre, definicion) del detalle.db del item."""
    detalle = item.get("detalle") or {}
    if not isinstance(detalle, dict):
        detalle = {}
    det_db = detalle.get("db") or {}
    if not isinstance(det_db, dict):
        det_db = {}
    nombre = det_db.get("name") or ""
    definicion = det_db.get("definition") or det_db.get("constraint_def") or ""
    return nombre, definicion


def filtrar(items, args):
    out = []
    for x in items:
        if x.get("clasificacion") != "constraint_falta":
            continue
        nombre, definicion = extraer_nombre_definicion(x)
        if es_not_null_autogen(nombre):
            continue
        subtipo = clasificar_subtipo(nombre, definicion)
        x["_subtipo"] = subtipo
        x["_nombre"] = nombre
        x["_definicion"] = definicion
        x["_archivo_orm"] = archivo_orm(x.get("schema", ""), x.get("tabla", ""))

        if args.schema and x.get("schema") != args.schema:
            continue
        if args.tier is not None and x.get("tier") != args.tier:
            continue
        if args.subtipo and subtipo != args.subtipo:
            continue
        if args.archivo and x["_archivo_orm"] != args.archivo:
            continue

        out.append(x)
    return out


def report_stats(items):
    print("=== filtrar_check.py stats ===")
    print()
    print(f"Items filtrados (constraint_falta sin *_not_null): {len(items)}")
    print()

    por_subtipo = Counter(x["_subtipo"] for x in items)
    print("Por subtipo:")
    for k, v in por_subtipo.most_common():
        print(f"  {v:5d}  {k}")
    print()

    por_archivo = defaultdict(Counter)
    for x in items:
        por_archivo[x["_archivo_orm"]][x["_subtipo"]] += 1

    print("Por archivo ORM:")
    for archivo, cnt in sorted(por_archivo.items(),
                               key=lambda kv: -sum(kv[1].values())):
        total = sum(cnt.values())
        detalle = ", ".join(f"{k}={v}" for k, v in sorted(cnt.items()))
        print(f"  {total:5d}  {archivo}  ({detalle})")
    print()

    por_tier = Counter(x.get("tier") for x in items)
    print("Por tier:")
    for k in sorted(por_tier.keys(), key=lambda t: (t is None, t)):
        print(f"  Tier {k}: {por_tier[k]}")
    print()


def report_listado(items):
    for x in items:
        schema = x.get("schema", "")
        tabla = x.get("tabla", "")
        print(f"{x.get('id', '?'):8s} | T{x.get('tier', '?')} | "
              f"{x['_subtipo']:6s} | {schema}.{tabla:30s} | "
              f"{x['_nombre']:50s} | {x['_archivo_orm']}")


def report_json(items):
    salida = []
    for x in items:
        salida.append({
            "id": x.get("id"),
            "tier": x.get("tier"),
            "schema": x.get("schema"),
            "tabla": x.get("tabla"),
            "subtipo": x["_subtipo"],
            "nombre": x["_nombre"],
            "definicion": x["_definicion"],
            "archivo_orm": x["_archivo_orm"],
        })
    print(json.dumps(salida, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Lista constraint_falta que son CHECK/UNIQUE/FK reales "
                    "(excluye *_not_null autogenerados)."
    )
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--schema", metavar="SCHEMA")
    parser.add_argument("--tier", type=int, metavar="N")
    parser.add_argument("--subtipo",
                        choices=["check", "unique", "fk", "pk", "other"])
    parser.add_argument("--archivo", metavar="FILE")
    args = parser.parse_args()

    items = cargar_items(DIFF_JSON)
    items = filtrar(items, args)

    if args.stats:
        report_stats(items)
        return
    if args.json:
        report_json(items)
        return
    if args.report:
        report_listado(items)
        return

    parser.print_help()


if __name__ == "__main__":
    main()