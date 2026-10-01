"""
introspect_orm.py - Introspeccion completa del ORM SQLAlchemy.

Produce un snapshot estructurado (JSON) del estado real del ORM:
- Tablas declaradas en Base.metadata.
- Columnas con tipo normalizado a formato PostgreSQL.
- Constraints (PK, FK, UNIQUE, CHECK).
- Indices.
- Comments (de tabla y de columnas).
- Server defaults.

El output tiene la MISMA estructura que db_snapshot.json,
para que diff.py pueda compararlos.

Uso:
    python scripts/orm_sync/introspect_orm.py
    python scripts/orm_sync/introspect_orm.py --output=docs/orm_sync/orm_snapshot.json
    python scripts/orm_sync/introspect_orm.py --schemas=auth,fleet,trip
    python scripts/orm_sync/introspect_orm.py --verbose
"""

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# Paths absolutos (independientes del cwd)
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# PROJECT_ROOT = D:\aTaxip\backend

# Agregar al sys.path para poder importar app.models
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "orm_sync" / "orm_snapshot.json"


# ============================================================
# Constantes
# ============================================================

VERBOSE = False


# ============================================================
# Logging
# ============================================================

def log(msg, level="INFO"):
    """Log a stdout con prefijo."""
    print(f"[introspect_orm] [{level}] {msg}")


def log_verbose(msg):
    """Log solo si VERBOSE esta activo."""
    if VERBOSE:
        log(msg, "DEBUG")


# ============================================================
# Carga del ORM
# ============================================================

def load_orm():
    """Importa app.models y devuelve Base.metadata.

    Estrategia:
      1. from app.database import Base
      2. import app.models  (registra todos los modelos en Base.metadata)
      3. Devolver Base.metadata
    """
    log("Importando app.database...")
    try:
        from app.database import Base
    except Exception as e:
        log(f"ERROR importando app.database: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        sys.exit(1)

    log("Importando app.models (registra modelos)...")
    try:
        import app.models  # noqa: F401
    except Exception as e:
        log(f"ERROR importando app.models: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        sys.exit(1)

    log(f"Modelos cargados: {len(Base.metadata.tables)} tablas")
    return Base.metadata


# ============================================================
# Normalizacion de tipos SQLAlchemy -> PostgreSQL
# ============================================================

def extract_parens(t):
    """Extrae el contenido de parentesis. 'VARCHAR(50)' -> '50'."""
    if "(" in t and ")" in t:
        start = t.index("(") + 1
        end = t.index(")")
        return t[start:end]
    return None


def normalize_type(compiled_type):
    """Normaliza tipo SQLAlchemy compilado a formato PostgreSQL.

    Ejemplos:
      VARCHAR(50) -> character varying(50)
      NUMERIC(10, 8) -> numeric(10,8)
      TIMESTAMP -> timestamp without time zone
      TIMESTAMP WITH TIME ZONE -> timestamp with time zone
      INTEGER -> integer
      UUID -> uuid
      JSONB -> jsonb
      BOOLEAN -> boolean
    """
    if not compiled_type:
        return None

    t = compiled_type.upper().strip()

    # VARCHAR
    if t.startswith("VARCHAR") or t.startswith("CHARACTER VARYING"):
        length = extract_parens(t)
        if length:
            return f"character varying({length})"
        return "character varying"

    # NUMERIC
    if t.startswith("NUMERIC"):
        args = extract_parens(t)
        if args:
            args = args.replace(" ", "")
            return f"numeric({args})"
        return "numeric"

    # TIMESTAMP
    if "TIMESTAMP WITH TIME ZONE" in t or "TIMESTAMP WITH TIMEZONE" in t:
        return "timestamp with time zone"
    if "TIMESTAMP WITHOUT TIME ZONE" in t or t.startswith("TIMESTAMP"):
        return "timestamp without time zone"

    # TIME
    if "TIME WITH TIME ZONE" in t or "TIME WITH TIMEZONE" in t:
        return "time with time zone"
    if "TIME WITHOUT TIME ZONE" in t or t == "TIME":
        return "time without time zone"

    # INT
    if t == "INTEGER" or t == "INT":
        return "integer"
    if t == "BIGINT":
        return "bigint"
    if t == "SMALLINT":
        return "smallint"

    # Otros
    if t == "BOOLEAN" or t == "BOOL":
        return "boolean"
    if t == "TEXT":
        return "text"
    if t == "UUID":
        return "uuid"
    if t == "JSONB":
        return "jsonb"
    if t == "JSON":
        return "json"
    if t == "DATE":
        return "date"
    if t == "BYTEA":
        return "bytea"
    if t == "REAL":
        return "real"
    if t == "DOUBLE PRECISION":
        return "double precision"
    if t == "FLOAT":
        return "double precision"

    # Fallback: lowercase tal cual
    log_verbose(f"Tipo no mapeado: {compiled_type} -> {t.lower()}")
    return t.lower()


def compile_column_type(col):
    """Compila el tipo de una Column a string PostgreSQL."""
    try:
        from sqlalchemy.dialects import postgresql
        dialect = postgresql.dialect()
        compiled = col.type.compile(dialect=dialect)
        return normalize_type(compiled)
    except Exception as e:
        log_verbose(f"Error compilando tipo de {col.name}: {e}")
        return str(col.type)


# ============================================================
# Extraccion de defaults
# ============================================================

def extract_server_default(col):
    """Extrae server_default de una Column. Opcion B con fallback a A."""
    if col.server_default is None:
        return None
    sd = col.server_default

    # Intentar .arg
    try:
        if hasattr(sd, 'arg'):
            arg = sd.arg
            if hasattr(arg, 'text'):
                return arg.text
            return str(arg)
    except Exception as e:
        log_verbose(f"Error extrayendo server_default de {col.name}: {e}")

    # Fallback: str()
    return str(sd)


# ============================================================
# Introspeccion: tablas
# ============================================================

def get_table_schema(table):
    """Schema de una Table (default: public)."""
    return table.schema or "public"


def get_table_name(table):
    """Nombre de la tabla (sin schema)."""
    return table.name


# ============================================================
# Introspeccion: columnas
# ============================================================

def get_table_columns(table):
    """Columnas de la tabla con tipo normalizado."""
    columns = {}
    for idx, col in enumerate(table.columns, start=1):
        columns[col.name] = {
            "ordinal": idx,
            "type": compile_column_type(col),
            "base_type": col.type.__class__.__name__,
            "nullable": col.nullable,
            "default": str(col.default.arg) if col.default and hasattr(col.default, 'arg') else None,
            "server_default": extract_server_default(col),
            "comment": col.comment,
            "character_maximum_length": getattr(col.type, 'length', None),
            "numeric_precision": getattr(col.type, 'precision', None),
            "numeric_scale": getattr(col.type, 'scale', None),
            "datetime_precision": None,  # No aplica a nivel SQLAlchemy
        }
    return columns


# ============================================================
# Introspeccion: constraints
# ============================================================

def get_primary_key(table):
    """Primary key de la tabla."""
    from sqlalchemy import PrimaryKeyConstraint
    for c in table.constraints:
        if isinstance(c, PrimaryKeyConstraint):
            return {
                "name": c.name,
                "columns": [col.name for col in c.columns],
            }
    return None


def get_foreign_keys(table):
    """Foreign keys de la tabla."""
    from sqlalchemy import ForeignKeyConstraint
    fks = []
    for c in table.constraints:
        if isinstance(c, ForeignKeyConstraint):
            for elem in c.elements:
                target = elem.column
                fks.append({
                    "name": c.name,
                    "columns": [elem.parent.name],
                    "references": {
                        "schema": target.table.schema or "public",
                        "table": target.table.name,
                        "columns": [target.name],
                    },
                    "on_delete": c.ondelete,
                    "on_update": c.onupdate,
                })
    return fks


def get_unique_constraints(table):
    """Unique constraints de la tabla."""
    from sqlalchemy import UniqueConstraint
    uniques = []
    for c in table.constraints:
        if isinstance(c, UniqueConstraint):
            uniques.append({
                "name": c.name,
                "columns": [col.name for col in c.columns],
            })
    return uniques


def get_check_constraints(table):
    """Check constraints de la tabla."""
    from sqlalchemy import CheckConstraint
    checks = []
    for c in table.constraints:
        if isinstance(c, CheckConstraint):
            checks.append({
                "name": c.name,
                "definition": str(c.sqltext) if c.sqltext is not None else None,
            })
    return checks


def get_table_constraints(table):
    """Todos los constraints de la tabla."""
    return {
        "primary_key": get_primary_key(table),
        "foreign_keys": get_foreign_keys(table),
        "unique": get_unique_constraints(table),
        "check": get_check_constraints(table),
    }


# ============================================================
# Introspeccion: indices
# ============================================================

def get_table_indexes(table):
    """Indices de la tabla."""
    indexes = []
    for idx in table.indexes:
        # Metodo (btree, gist, etc.)
        method = "btree"  # default
        try:
            if hasattr(idx, 'dialect_options') and 'postgresql' in idx.dialect_options:
                method = idx.dialect_options['postgresql'].get('using', 'btree')
        except Exception:
            pass

        # Columnas
        try:
            cols = [col.name for col in idx.columns]
        except Exception:
            cols = []

        # Definition (no la tiene SQLAlchemy directamente, la construimos)
        unique = "UNIQUE " if idx.unique else ""
        cols_str = ", ".join(cols)
        definition = f"CREATE {unique}INDEX {idx.name} ON {table.schema or 'public'}.{table.name} USING {method} ({cols_str})"

        indexes.append({
            "name": idx.name,
            "unique": idx.unique,
            "primary": False,  # SQLAlchemy no distingue PK como indice
            "method": method,
            "definition": definition,
            "columns": cols,
        })
    return indexes


# ============================================================
# Introspeccion: comments
# ============================================================

def get_table_comment(table):
    """Comment de la tabla."""
    return table.comment


# ============================================================
# Construccion del snapshot
# ============================================================

def build_snapshot(metadata, filter_schemas=None):
    """Construye el dict completo del snapshot del ORM."""
    warnings = []

    schemas_data = {}
    total_tables = 0
    total_columns = 0
    total_indexes = 0
    total_constraints = 0

    for full_name, table in sorted(metadata.tables.items()):
        schema = get_table_schema(table)
        name = get_table_name(table)

        if filter_schemas and schema not in filter_schemas:
            continue

        log_verbose(f"Tabla: {schema}.{name}")

        try:
            columns = get_table_columns(table)
            constraints = get_table_constraints(table)
            indexes = get_table_indexes(table)
            comment = get_table_comment(table)

            if schema not in schemas_data:
                schemas_data[schema] = {
                    "comment": None,
                    "tables": {},
                    "views": {},
                    "sequences": {},
                }

            schemas_data[schema]["tables"][name] = {
                "comment": comment,
                "columns": columns,
                "constraints": constraints,
                "indexes": indexes,
            }

            total_tables += 1
            total_columns += len(columns)
            total_indexes += len(indexes)
            total_constraints += (
                (1 if constraints["primary_key"] else 0)
                + len(constraints["foreign_keys"])
                + len(constraints["unique"])
                + len(constraints["check"])
            )
        except Exception as e:
            err_msg = f"Error en {schema}.{name}: {e}"
            log(err_msg, "WARN")
            warnings.append({
                "context": f"table.{schema}.{name}",
                "error": str(e),
                "traceback": traceback.format_exc(),
            })

    schemas_list = sorted(schemas_data.keys())

    snapshot = {
        "meta": {
            "capturado_en": datetime.now(timezone.utc).isoformat(),
            "alembic_head": None,  # No aplica al ORM
            "schemas_incluidos": schemas_list,
            "warnings": warnings,
            "stats": {
                "total_schemas": len(schemas_list),
                "total_tables": total_tables,
                "total_columns": total_columns,
                "total_indexes": total_indexes,
                "total_constraints": total_constraints,
            },
        },
        "schemas": schemas_data,
        "enums": {},  # SQLAlchemy no tiene enums a nivel metadata (los maneja como VARCHAR + CHECK)
        "extensions": [],  # No aplica al ORM
    }

    return snapshot


# ============================================================
# Escritura del JSON
# ============================================================

def write_json(snapshot, output_path):
    """Escribe el snapshot a JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False, default=str)

    size_kb = path.stat().st_size / 1024
    log(f"OK. Archivo: {output_path} ({size_kb:.1f} KB)")


# ============================================================
# Resumen humano
# ============================================================

def print_summary(snapshot):
    """Imprime resumen del snapshot a stdout."""
    meta = snapshot["meta"]
    stats = meta["stats"]

    log("=" * 60)
    log("RESUMEN DEL SNAPSHOT ORM")
    log("=" * 60)
    log(f"Schemas: {stats['total_schemas']}")
    log(f"Tablas: {stats['total_tables']}")
    log(f"Columnas: {stats['total_columns']}")
    log(f"Indices: {stats['total_indexes']}")
    log(f"Constraints: {stats['total_constraints']}")
    log(f"Warnings: {len(meta['warnings'])}")
    log("=" * 60)


# ============================================================
# Main
# ============================================================

def main():
    global VERBOSE

    parser = argparse.ArgumentParser(
        description="Introspeccion completa del ORM SQLAlchemy."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Ruta del JSON de salida (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--schemas",
        default=None,
        help="Lista de schemas separada por comas (default: todos)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Imprime mas detalle",
    )

    args = parser.parse_args()
    VERBOSE = args.verbose

    filter_schemas = None
    if args.schemas:
        filter_schemas = [s.strip() for s in args.schemas.split(",")]

    log("Iniciando...")

    metadata = load_orm()
    snapshot = build_snapshot(metadata, filter_schemas)
    write_json(snapshot, args.output)
    print_summary(snapshot)

    log("Listo.")


if __name__ == "__main__":
    main()