"""
introspect_db.py - Introspeccion completa de la base de datos PostgreSQL.

Produce un snapshot estructurado (JSON) del estado real de la DB:
- Schemas, tablas, columnas, constraints, indices, comments, enums, extensiones.
- Tipos completos con precision (numeric(10,8), varchar(50), timestamp(6) without time zone).

Este script NO compara con el ORM. Solo describe la DB.
Este script NO escribe en la DB. Solo lee.

Uso:
    python scripts/orm_sync/introspect_db.py
    python scripts/orm_sync/introspect_db.py --output=docs/orm_sync/db_snapshot.json
    python scripts/orm_sync/introspect_db.py --schemas=auth,fleet,trip
    python scripts/orm_sync/introspect_db.py --verbose
"""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import psycopg2
from dotenv import load_dotenv


# ============================================================
# Constantes
# ============================================================

DEFAULT_OUTPUT = "docs/orm_sync/db_snapshot.json"
SYSTEM_SCHEMAS = ("information_schema", "pg_catalog", "pg_toast")


# ============================================================
# Logging
# ============================================================

VERBOSE = False


def log(msg, level="INFO"):
    """Log a stdout con prefijo."""
    print(f"[introspect_db] [{level}] {msg}")


def log_verbose(msg):
    """Log solo si VERBOSE esta activo."""
    if VERBOSE:
        log(msg, "DEBUG")


# ============================================================
# Utilidades
# ============================================================

def mask_db_url(url):
    """Oculta la password de la URL para logs."""
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            return urlunparse(parsed._replace(netloc=netloc))
        return url
    except Exception:
        return "<url no parseable>"


def normalize_db_url(url):
    """Convierte postgresql+asyncpg:// a postgresql:// para psycopg2."""
    return url.replace("postgresql+asyncpg://", "postgresql://")


# ============================================================
# Conexion
# ============================================================

def get_db_connection():
    """Conecta a la DB usando DATABASE_URL del .env."""
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        log("ERROR: DATABASE_URL no encontrada en .env", "ERROR")
        sys.exit(1)

    db_url = normalize_db_url(db_url)
    log(f"Conectando a: {mask_db_url(db_url)}")

    try:
        conn = psycopg2.connect(db_url)
        log("Conexion exitosa")
        return conn
    except Exception as e:
        log(f"ERROR de conexion: {e}", "ERROR")
        sys.exit(1)


# ============================================================
# Introspeccion: schemas
# ============================================================

def get_schemas(cur, filter_schemas=None):
    """Lista schemas no-sistema (excluye temporales de sesion)."""
    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN %s
          AND schema_name NOT LIKE 'pg_temp_%%'
          AND schema_name NOT LIKE 'pg_toast_temp_%%'
        ORDER BY schema_name;
    """, (SYSTEM_SCHEMAS,))
    schemas = [row[0] for row in cur.fetchall()]

    if filter_schemas:
        schemas = [s for s in schemas if s in filter_schemas]

    return schemas


# ============================================================
# Introspeccion: tablas
# ============================================================

def get_tables(cur, schema):
    """Lista tablas base del schema."""
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """, (schema,))
    return [row[0] for row in cur.fetchall()]


def get_views(cur, schema):
    """Lista vistas del schema."""
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'VIEW'
        ORDER BY table_name;
    """, (schema,))
    return [row[0] for row in cur.fetchall()]


def get_sequences(cur, schema):
    """Lista secuencias del schema."""
    cur.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = %s
        ORDER BY sequence_name;
    """, (schema,))
    return [row[0] for row in cur.fetchall()]


# ============================================================
# Introspeccion: columnas
# ============================================================

def get_columns(cur, schema, table):
    """Columnas con tipo completo, nullable, default, precision."""
    cur.execute("""
        SELECT
            a.attname AS column_name,
            a.attnum AS ordinal,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS full_type,
            t.typname AS base_type,
            NOT a.attnotnull AS nullable,
            pg_catalog.pg_get_expr(d.adbin, d.adrelid) AS default_value,
            ic.character_maximum_length,
            ic.numeric_precision,
            ic.numeric_scale,
            ic.datetime_precision
        FROM pg_catalog.pg_attribute a
        JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_catalog.pg_type t ON t.oid = a.atttypid
        LEFT JOIN pg_catalog.pg_attrdef d
            ON d.adrelid = a.attrelid AND d.adnum = a.attnum
        LEFT JOIN information_schema.columns ic
            ON ic.table_schema = n.nspname
            AND ic.table_name = c.relname
            AND ic.column_name = a.attname
        WHERE n.nspname = %s AND c.relname = %s
          AND a.attnum > 0 AND NOT a.attisdropped
        ORDER BY a.attnum;
    """, (schema, table))

    columns = {}
    for row in cur.fetchall():
        col_name = row[0]
        columns[col_name] = {
            "ordinal": row[1],
            "type": row[2],
            "base_type": row[3],
            "nullable": row[4],
            "default": row[5],
            "character_maximum_length": row[6],
            "numeric_precision": row[7],
            "numeric_scale": row[8],
            "datetime_precision": row[9],
            "comment": None,  # Se completa despues
        }
    return columns


# ============================================================
# Introspeccion: constraints
# ============================================================

def get_primary_key(cur, schema, table):
    """Primary key de la tabla (nombre + columnas)."""
    cur.execute("""
        SELECT
            tc.constraint_name,
            array_agg(kcu.column_name ORDER BY kcu.ordinal_position) AS columns
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %s AND tc.table_name = %s
          AND tc.constraint_type = 'PRIMARY KEY'
        GROUP BY tc.constraint_name;
    """, (schema, table))

    row = cur.fetchone()
    if not row:
        return None
    return {"name": row[0], "columns": list(row[1])}


def get_foreign_keys(cur, schema, table):
    """Foreign keys de la tabla."""
    cur.execute("""
        SELECT
            tc.constraint_name,
            kcu.column_name,
            ccu.table_schema AS foreign_schema,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column,
            rc.delete_rule AS on_delete,
            rc.update_rule AS on_update
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        JOIN information_schema.referential_constraints rc
            ON rc.constraint_name = tc.constraint_name
        WHERE tc.table_schema = %s AND tc.table_name = %s
          AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.constraint_name;
    """, (schema, table))

    fks = []
    for row in cur.fetchall():
        fks.append({
            "name": row[0],
            "columns": [row[1]],
            "references": {
                "schema": row[2],
                "table": row[3],
                "columns": [row[4]],
            },
            "on_delete": row[5],
            "on_update": row[6],
        })
    return fks


def get_unique_constraints(cur, schema, table):
    """Unique constraints de la tabla."""
    cur.execute("""
        SELECT
            tc.constraint_name,
            array_agg(kcu.column_name ORDER BY kcu.ordinal_position) AS columns
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_schema = %s AND tc.table_name = %s
          AND tc.constraint_type = 'UNIQUE'
        GROUP BY tc.constraint_name
        ORDER BY tc.constraint_name;
    """, (schema, table))

    return [{"name": row[0], "columns": list(row[1])} for row in cur.fetchall()]


def get_check_constraints(cur, schema, table):
    """Check constraints de la tabla."""
    cur.execute("""
        SELECT
            tc.constraint_name,
            cc.check_clause AS definition
        FROM information_schema.table_constraints tc
        JOIN information_schema.check_constraints cc
            ON tc.constraint_name = cc.constraint_name
        WHERE tc.table_schema = %s AND tc.table_name = %s
          AND tc.constraint_type = 'CHECK'
        ORDER BY tc.constraint_name;
    """, (schema, table))

    return [{"name": row[0], "definition": row[1]} for row in cur.fetchall()]


def get_constraints(cur, schema, table):
    """Todos los constraints de la tabla."""
    return {
        "primary_key": get_primary_key(cur, schema, table),
        "foreign_keys": get_foreign_keys(cur, schema, table),
        "unique": get_unique_constraints(cur, schema, table),
        "check": get_check_constraints(cur, schema, table),
    }


# ============================================================
# Introspeccion: indices
# ============================================================

def get_indexes(cur, schema, table):
    """Indices de la tabla con columnas y metodo."""
    cur.execute("""
        SELECT
            i.relname AS index_name,
            ix.indisunique AS is_unique,
            ix.indisprimary AS is_primary,
            am.amname AS method,
            pg_catalog.pg_get_indexdef(ix.indexrelid) AS definition,
            array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum)) AS columns
        FROM pg_catalog.pg_index ix
        JOIN pg_catalog.pg_class i ON i.oid = ix.indexrelid
        JOIN pg_catalog.pg_class t ON t.oid = ix.indrelid
        JOIN pg_catalog.pg_namespace n ON n.oid = t.relnamespace
        JOIN pg_catalog.pg_am am ON am.oid = i.relam
        LEFT JOIN pg_catalog.pg_attribute a
            ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
        WHERE n.nspname = %s AND t.relname = %s
        GROUP BY i.relname, ix.indisunique, ix.indisprimary, am.amname, ix.indexrelid
        ORDER BY i.relname;
    """, (schema, table))

    indexes = []
    for row in cur.fetchall():
        cols = [c for c in row[5] if c is not None] if row[5] else []
        indexes.append({
            "name": row[0],
            "unique": row[1],
            "primary": row[2],
            "method": row[3],
            "definition": row[4],
            "columns": cols,
        })
    return indexes


# ============================================================
# Introspeccion: comments
# ============================================================

def get_table_comment(cur, schema, table):
    """Comment de la tabla."""
    cur.execute("""
        SELECT obj_description(c.oid, 'pg_class')
        FROM pg_catalog.pg_class c
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = %s AND c.relname = %s;
    """, (schema, table))
    row = cur.fetchone()
    return row[0] if row else None


def get_column_comments(cur, schema, table):
    """Comments de todas las columnas de la tabla."""
    cur.execute("""
        SELECT
            a.attname,
            col_description(a.attrelid, a.attnum)
        FROM pg_catalog.pg_attribute a
        JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = %s AND c.relname = %s
          AND a.attnum > 0 AND NOT a.attisdropped;
    """, (schema, table))

    return {row[0]: row[1] for row in cur.fetchall()}


# ============================================================
# Introspeccion: enums y extensiones
# ============================================================

def get_enums(cur):
    """Enums de la DB."""
    cur.execute("""
        SELECT t.typname, e.enumlabel
        FROM pg_catalog.pg_type t
        JOIN pg_catalog.pg_enum e ON t.oid = e.enumtypid
        ORDER BY t.typname, e.enumsortorder;
    """)

    enums = {}
    for typname, label in cur.fetchall():
        enums.setdefault(typname, []).append(label)
    return enums


def get_extensions(cur):
    """Extensiones instaladas."""
    cur.execute("SELECT extname FROM pg_catalog.pg_extension ORDER BY extname;")
    return [row[0] for row in cur.fetchall()]


# ============================================================
# Introspeccion: versiones
# ============================================================

def get_versions(cur):
    """Versiones de PostgreSQL y PostGIS."""
    result = {"postgres_version": None, "postgis_version": None}

    try:
        cur.execute("SELECT version();")
        result["postgres_version"] = cur.fetchone()[0]
    except Exception as e:
        log(f"No se pudo obtener version de PostgreSQL: {e}", "WARN")

    try:
        cur.execute("SELECT postgis_version();")
        result["postgis_version"] = cur.fetchone()[0]
    except Exception as e:
        log(f"PostGIS no disponible: {e}", "WARN")

    return result


def get_alembic_head(cur):
    """Head actual de Alembic."""
    try:
        cur.execute("SELECT version_num FROM public.alembic_version;")
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        log(f"No se pudo obtener alembic head: {e}", "WARN")
        return None


# ============================================================
# Construccion del snapshot
# ============================================================

def build_snapshot(cur, filter_schemas=None):
    """Construye el dict completo del snapshot."""
    warnings = []

    # Meta
    versions = get_versions(cur)
    alembic_head = get_alembic_head(cur)

    schemas_list = get_schemas(cur, filter_schemas)
    log(f"Schemas a procesar: {', '.join(schemas_list)}")

    # Schemas y tablas
    schemas_data = {}
    total_tables = 0
    total_columns = 0
    total_indexes = 0
    total_constraints = 0

    for schema in schemas_list:
        log(f"Procesando schema: {schema}")
        tables = get_tables(cur, schema)
        views = get_views(cur, schema)
        sequences = get_sequences(cur, schema)

        tables_data = {}
        for table in tables:
            try:
                log_verbose(f"  Tabla: {schema}.{table}")
                columns = get_columns(cur, schema, table)

                # Completar comments de columnas
                col_comments = get_column_comments(cur, schema, table)
                for col_name, comment in col_comments.items():
                    if col_name in columns:
                        columns[col_name]["comment"] = comment

                constraints = get_constraints(cur, schema, table)
                indexes = get_indexes(cur, schema, table)
                table_comment = get_table_comment(cur, schema, table)

                tables_data[table] = {
                    "comment": table_comment,
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
                err_msg = f"Error en {schema}.{table}: {e}"
                log(err_msg, "WARN")
                warnings.append({
                    "context": f"table.{schema}.{table}",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })

        schemas_data[schema] = {
            "comment": None,  # comments de schema no son comunes, skip
            "tables": tables_data,
            "views": {v: {} for v in views},
            "sequences": {s: {} for s in sequences},
        }

    # Enums y extensiones
    try:
        enums = get_enums(cur)
    except Exception as e:
        log(f"Error obteniendo enums: {e}", "WARN")
        warnings.append({"context": "enums", "error": str(e)})
        enums = {}

    try:
        extensions = get_extensions(cur)
    except Exception as e:
        log(f"Error obteniendo extensiones: {e}", "WARN")
        warnings.append({"context": "extensions", "error": str(e)})
        extensions = []

    # Construir snapshot final
    snapshot = {
        "meta": {
            "capturado_en": datetime.now(timezone.utc).isoformat(),
            "postgres_version": versions["postgres_version"],
            "postgis_version": versions["postgis_version"],
            "alembic_head": alembic_head,
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
        "enums": enums,
        "extensions": extensions,
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
    log("RESUMEN DEL SNAPSHOT")
    log("=" * 60)
    log(f"PostgreSQL: {meta['postgres_version']}")
    log(f"PostGIS: {meta['postgis_version']}")
    log(f"Alembic head: {meta['alembic_head']}")
    log(f"Schemas: {stats['total_schemas']}")
    log(f"Tablas: {stats['total_tables']}")
    log(f"Columnas: {stats['total_columns']}")
    log(f"Indices: {stats['total_indexes']}")
    log(f"Constraints: {stats['total_constraints']}")
    log(f"Warnings: {len(meta['warnings'])}")
    log(f"Enums: {len(snapshot['enums'])}")
    log(f"Extensiones: {', '.join(snapshot['extensions'])}")
    log("=" * 60)


# ============================================================
# Main
# ============================================================

def main():
    global VERBOSE

    parser = argparse.ArgumentParser(
        description="Introspeccion completa de la DB PostgreSQL."
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Ruta del JSON de salida (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--schemas",
        default=None,
        help="Lista de schemas separada por comas (default: todos los no-sistema)",
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

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        snapshot = build_snapshot(cur, filter_schemas)
        write_json(snapshot, args.output)
        print_summary(snapshot)
    finally:
        conn.close()

    log("Listo.")


if __name__ == "__main__":
    main()