#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
FASE 3: AUDITORÍA FORENSE DE BASE RECONSTRUIDA
================================================================
Solo lectura. No modifica archivos, migraciones, modelos ni BD.

Genera:
  - fase3_output/actual_tables.txt
  - fase3_output/actual_columns.txt
  - fase3_output/actual_primary_keys.txt
  - fase3_output/actual_unique_constraints.txt
  - fase3_output/actual_check_constraints.txt
  - fase3_output/actual_foreign_keys.txt
  - fase3_output/actual_indexes.txt
  - fase3_output/actual_postgis.txt
  - fase3_output/actual_defaults.txt
  - fase3_output/FASE3_AUDITORIA_FINAL.md

Uso:
    cd D:\ataxip\backend
    python fase3_auditoria.py

Requiere: psycopg2-binary
    pip install psycopg2-binary
================================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ Instala psycopg2-binary:  pip install psycopg2-binary")
    sys.exit(1)

# ============================================================
# CONFIGURACIÓN
# ============================================================
OUTPUT_DIR = Path("fase3_output")
SCHEMAS_EXCLUDE = (
    'pg_catalog', 'information_schema', 'pg_toast',
    'pg_temp_1', 'pg_toast_temp_1', 'pg_temp_2', 'pg_toast_temp_2',
    'pg_temp_3', 'pg_toast_temp_3', 'pg_temp_4', 'pg_toast_temp_4'
)


def get_db_config():
    """Lee configuración de BD desde variables de entorno."""
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', os.getenv('POSTGRES_DB', 'ataxip')),
        'user': os.getenv('DB_USER', os.getenv('POSTGRES_USER', 'postgres')),
        'password': os.getenv('DB_PASSWORD', os.getenv('POSTGRES_PASSWORD', 'postgres')),
    }
    return config


def connect():
    cfg = get_db_config()
    try:
        conn = psycopg2.connect(
            host=cfg['host'],
            port=cfg['port'],
            dbname=cfg['database'],
            user=cfg['user'],
            password=cfg['password'],
        )
        print(f"✅ Conectado a PostgreSQL: {cfg['host']}:{cfg['port']}/{cfg['database']}")
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"   Config usada: host={cfg['host']}, port={cfg['port']}, db={cfg['database']}, user={cfg['user']}")
        print("   Asegurate de tener las variables DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        sys.exit(1)


def write_file(filename, content):
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding='utf-8')
    print(f"   📄 {filename}  ({len(content)} chars)")
    return path


def query_to_text(cur, sql, headers=None):
    cur.execute(sql)
    rows = cur.fetchall()
    if not rows:
        return "(sin resultados)\n"

    if headers is None:
        headers = [desc[0] for desc in cur.description]

    # Calcular anchos
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val) if val is not None else 'NULL'))

    lines = []
    sep = '+-' + '-+-'.join('-' * w for w in widths) + '-+'
    header_line = '| ' + ' | '.join(h.ljust(w) for h, w in zip(headers, widths)) + ' |'
    lines.append(sep)
    lines.append(header_line)
    lines.append(sep)
    for row in rows:
        row_line = '| ' + ' | '.join(
            (str(v) if v is not None else 'NULL').ljust(w)
            for v, w in zip(row, widths)
        ) + ' |'
        lines.append(row_line)
    lines.append(sep)
    lines.append(f"\nTotal: {len(rows)} filas\n")
    return '\n'.join(lines)


def run_audit():
    OUTPUT_DIR.mkdir(exist_ok=True)
    conn = connect()
    cur = conn.cursor()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_sections = []

    # ============================================================
    # 1. SCHEMAS
    # ============================================================
    print("\n📊 1/12 - Schemas...")
    sql_schemas = f"""
    SELECT schema_name,
           (SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = s.schema_name AND table_type = 'BASE TABLE') AS table_count
    FROM information_schema.schemata s
    WHERE schema_name NOT IN {SCHEMAS_EXCLUDE}
    ORDER BY schema_name;
    """
    schemas_text = query_to_text(cur, sql_schemas, ['schema_name', 'table_count'])
    write_file("actual_schemas.txt", schemas_text)

    schemas_list = []
    cur.execute(sql_schemas)
    for row in cur.fetchall():
        schemas_list.append(row[0])

    # ============================================================
    # 2. TABLAS
    # ============================================================
    print("📊 2/12 - Tablas...")
    sql_tables = f"""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema NOT IN {SCHEMAS_EXCLUDE}
      AND table_type = 'BASE TABLE'
    ORDER BY table_schema, table_name;
    """
    tables_text = query_to_text(cur, sql_tables, ['schema', 'table'])
    write_file("actual_tables.txt", tables_text)

    tables_list = []
    cur.execute(sql_tables)
    for row in cur.fetchall():
        tables_list.append(f"{row[0]}.{row[1]}")

    # ============================================================
    # 3. COLUMNAS
    # ============================================================
    print("📊 3/12 - Columnas...")
    sql_columns = f"""
    SELECT table_schema, table_name, column_name, ordinal_position,
           data_type, udt_name, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_schema NOT IN {SCHEMAS_EXCLUDE}
    ORDER BY table_schema, table_name, ordinal_position;
    """
    columns_text = query_to_text(cur, sql_columns, 
        ['schema', 'table', 'column', 'pos', 'data_type', 'udt_name', 'nullable', 'default'])
    write_file("actual_columns.txt", columns_text)

    # ============================================================
    # 4. PRIMARY KEYS
    # ============================================================
    print("📊 4/12 - Primary Keys...")
    sql_pk = f"""
    SELECT tc.table_schema, tc.table_name, tc.constraint_name,
           kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema = kcu.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
      AND tc.table_schema NOT IN {SCHEMAS_EXCLUDE}
    ORDER BY tc.table_schema, tc.table_name, kcu.ordinal_position;
    """
    pk_text = query_to_text(cur, sql_pk, ['schema', 'table', 'constraint_name', 'column'])
    write_file("actual_primary_keys.txt", pk_text)

    # ============================================================
    # 5. UNIQUE CONSTRAINTS
    # ============================================================
    print("📊 5/12 - Unique Constraints...")
    sql_unique = f"""
    SELECT tc.table_schema, tc.table_name, tc.constraint_name,
           kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema = kcu.table_schema
    WHERE tc.constraint_type = 'UNIQUE'
      AND tc.table_schema NOT IN {SCHEMAS_EXCLUDE}
    ORDER BY tc.table_schema, tc.table_name, tc.constraint_name, kcu.ordinal_position;
    """
    unique_text = query_to_text(cur, sql_unique, ['schema', 'table', 'constraint_name', 'column'])
    write_file("actual_unique_constraints.txt", unique_text)

    # ============================================================
    # 6. CHECK CONSTRAINTS
    # ============================================================
    print("📊 6/12 - Check Constraints...")
    sql_check = f"""
    SELECT n.nspname AS schema_name,
           cl.relname AS table_name,
           con.conname AS constraint_name,
           pg_get_constraintdef(con.oid) AS definition
    FROM pg_constraint con
    JOIN pg_class cl ON con.conrelid = cl.oid
    JOIN pg_namespace n ON cl.relnamespace = n.oid
    WHERE con.contype = 'c'
      AND n.nspname NOT IN {SCHEMAS_EXCLUDE}
      AND con.conname NOT LIKE 'pg_%'
      AND con.conname NOT LIKE '2200_%'
    ORDER BY n.nspname, cl.relname, con.conname;
    """
    check_text = query_to_text(cur, sql_check, ['schema', 'table', 'constraint_name', 'definition'])
    write_file("actual_check_constraints.txt", check_text)

    # ============================================================
    # 7. FOREIGN KEYS (CRÍTICO)
    # ============================================================
    print("📊 7/12 - Foreign Keys (crítico)...")
    sql_fk = f"""
    SELECT
        tc.constraint_name,
        tc.table_schema AS schema_origen,
        tc.table_name AS tabla_origen,
        string_agg(kcu.column_name, ',' ORDER BY kcu.ordinal_position) AS columnas_origen,
        ccu.table_schema AS schema_destino,
        ccu.table_name AS tabla_destino,
        string_agg(ccu.column_name, ',' ORDER BY kcu.ordinal_position) AS columnas_destino
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
      ON tc.constraint_name = ccu.constraint_name
     AND tc.table_schema = ccu.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
      AND tc.table_schema NOT IN {SCHEMAS_EXCLUDE}
    GROUP BY tc.constraint_name, tc.table_schema, tc.table_name,
             ccu.table_schema, ccu.table_name
    ORDER BY tc.table_schema, tc.table_name, tc.constraint_name;
    """
    fk_text = query_to_text(cur, sql_fk, 
        ['constraint_name', 'schema_origen', 'tabla_origen', 'columnas_origen',
         'schema_destino', 'tabla_destino', 'columnas_destino'])
    write_file("actual_foreign_keys.txt", fk_text)

    # Conteo total desde pg_constraint (fuente de verdad)
    cur.execute("SELECT count(*) FROM pg_constraint WHERE contype = 'f';")
    total_fks = cur.fetchone()[0]

    # ============================================================
    # 8. DETECCIÓN DE DUPLICADOS
    # ============================================================
    print("📊 8/12 - Detección de FKs duplicadas...")
    cur.execute(sql_fk)
    fk_rows = cur.fetchall()

    fk_by_signature = defaultdict(list)
    for row in fk_rows:
        signature = (row[1], row[2], row[3], row[4], row[5], row[6])  # schema, tabla, cols, schema_dest, tabla_dest, cols_dest
        fk_by_signature[signature].append(row[0])

    duplicates = {sig: names for sig, names in fk_by_signature.items() if len(names) > 1}

    dup_lines = ["=" * 60, "DETECCIÓN DE FKs DUPLICADAS", "=" * 60, ""]
    if duplicates:
        dup_lines.append(f"⚠️  Se encontraron {len(duplicates)} grupos de FKs duplicadas:\n")
        for sig, names in sorted(duplicates.items()):
            dup_lines.append(f"Relación: {sig[0]}.{sig[1]}({sig[2]}) -> {sig[3]}.{sig[4]}({sig[5]})")
            dup_lines.append(f"   Constraints: {', '.join(names)}")
            dup_lines.append("")
    else:
        dup_lines.append("✅ No se encontraron FKs duplicadas por relación lógica.\n")

    dup_lines.append(f"Total FKs en BD (pg_constraint): {total_fks}")
    dup_lines.append(f"Total FKs únicas por relación: {len(fk_by_signature)}")
    dup_lines.append("")

    # Especial atención a trip.reserva
    dup_lines.append("=" * 60)
    dup_lines.append("ESPECIAL ATENCIÓN: trip.reserva")
    dup_lines.append("=" * 60)
    reserva_fks = [row for row in fk_rows if row[1] == 'trip' and row[2] == 'reserva']
    for row in reserva_fks:
        dup_lines.append(f"   {row[0]}: {row[3]} -> {row[4]}.{row[5]}({row[6]})")
    dup_lines.append("")

    dup_text = '\n'.join(dup_lines)
    write_file("actual_fk_duplicates.txt", dup_text)

    # ============================================================
    # 9. ÍNDICES
    # ============================================================
    print("📊 9/12 - Índices...")
    sql_indexes = f"""
    SELECT schemaname, tablename, indexname, indexdef
    FROM pg_indexes
    WHERE schemaname NOT IN {SCHEMAS_EXCLUDE}
    ORDER BY schemaname, tablename, indexname;
    """
    idx_text = query_to_text(cur, sql_indexes, ['schema', 'table', 'index_name', 'definition'])
    write_file("actual_indexes.txt", idx_text)

    # ============================================================
    # 10. POSTGIS
    # ============================================================
    print("📊 10/12 - PostGIS...")
    postgis_lines = ["=" * 60, "POSTGIS AUDITORÍA", "=" * 60, ""]

    try:
        cur.execute("SELECT PostGIS_Version();")
        version = cur.fetchone()[0]
        postgis_lines.append(f"PostGIS Version: {version}")
    except Exception as e:
        postgis_lines.append(f"PostGIS Version: No disponible ({e})")

    postgis_lines.append("")

    # Columnas geometry
    try:
        cur.execute("""
            SELECT f_table_schema, f_table_name, f_geometry_column, type, srid
            FROM geometry_columns
            WHERE f_table_schema NOT IN {SCHEMAS_EXCLUDE}
            ORDER BY f_table_schema, f_table_name;
        """.format(SCHEMAS_EXCLUDE=SCHEMAS_EXCLUDE))
        geom_rows = cur.fetchall()
        if geom_rows:
            postgis_lines.append("--- GEOMETRY COLUMNS ---")
            for row in geom_rows:
                postgis_lines.append(f"   {row[0]}.{row[1]}.{row[2]}  type={row[3]}  srid={row[4]}")
            postgis_lines.append("")
    except Exception as e:
        postgis_lines.append(f"geometry_columns: {e}")

    # Columnas geography
    try:
        cur.execute("""
            SELECT f_table_schema, f_table_name, f_geography_column, type, srid
            FROM geography_columns
            WHERE f_table_schema NOT IN {SCHEMAS_EXCLUDE}
            ORDER BY f_table_schema, f_table_name;
        """.format(SCHEMAS_EXCLUDE=SCHEMAS_EXCLUDE))
        geog_rows = cur.fetchall()
        if geog_rows:
            postgis_lines.append("--- GEOGRAPHY COLUMNS ---")
            for row in geog_rows:
                postgis_lines.append(f"   {row[0]}.{row[1]}.{row[2]}  type={row[3]}  srid={row[4]}")
            postgis_lines.append("")
    except Exception as e:
        postgis_lines.append(f"geography_columns: {e}")

    # Columnas con tipo geometry/geography desde information_schema
    cur.execute(f"""
        SELECT table_schema, table_name, column_name, udt_name, data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN {SCHEMAS_EXCLUDE}
          AND (udt_name ILIKE 'geometry' OR udt_name ILIKE 'geography' 
               OR data_type ILIKE 'geometry' OR data_type ILIKE 'geography'
               OR udt_name ILIKE 'geography%%' OR udt_name ILIKE 'geometry%%')
        ORDER BY table_schema, table_name, ordinal_position;
    """)
    geo_cols = cur.fetchall()
    if geo_cols:
        postgis_lines.append("--- COLUMNAS CON TIPO GEOMETRY/GEOGRAPHY (information_schema) ---")
        for row in geo_cols:
            postgis_lines.append(f"   {row[0]}.{row[1]}.{row[2]}  udt={row[3]}  data_type={row[4]}")
        postgis_lines.append("")

    postgis_text = '\n'.join(postgis_lines)
    write_file("actual_postgis.txt", postgis_text)

    # ============================================================
    # 11. DEFAULTS
    # ============================================================
    print("📊 11/12 - Defaults...")
    sql_defaults = f"""
    SELECT table_schema, table_name, column_name, column_default
    FROM information_schema.columns
    WHERE column_default IS NOT NULL
      AND table_schema NOT IN {SCHEMAS_EXCLUDE}
    ORDER BY table_schema, table_name, ordinal_position;
    """
    defaults_text = query_to_text(cur, sql_defaults, ['schema', 'table', 'column', 'default'])
    write_file("actual_defaults.txt", defaults_text)

    # Defaults especiales
    special_defaults = []
    cur.execute(sql_defaults)
    for row in cur.fetchall():
        default = str(row[3]).lower()
        if any(k in default for k in ['gen_random_uuid', 'now()', 'current_date', "'[]'::jsonb", 'jsonb']):
            special_defaults.append(f"{row[0]}.{row[1]}.{row[2]}: {row[3]}")

    special_text = "DEFAULTS ESPECIALES DETECTADOS\n" + "=" * 60 + "\n\n"
    special_text += '\n'.join(special_defaults) if special_defaults else "(ninguno detectado)"
    special_text += "\n"
    write_file("actual_special_defaults.txt", special_text)

    # ============================================================
    # 12. GENERAR INFORME FINAL MD
    # ============================================================
    print("📊 12/12 - Generando FASE3_AUDITORIA_FINAL.md...")

    md = f"""# FASE 3: AUDITORÍA FORENSE DE BASE RECONSTRUIDA

**Fecha:** {timestamp}  
**Base de datos:** {get_db_config()['database']}  
**Regla:** Solo lectura. Sin modificaciones.

---

## 1. ESTADO ALEMBIC

Ejecutar manualmente:
```bash
alembic current
alembic heads
alembic history
```

**HEAD esperado:** `9cde8795c601`

---

## 2. SCHEMAS

Total de schemas de aplicación: **{len(schemas_list)}**

| Schema | Tablas |
|--------|--------|
"""
    cur.execute(sql_schemas)
    for row in cur.fetchall():
        md += f"| {row[0]} | {row[1]} |\n"

    md += f"""
---

## 3. TABLAS

Total de tablas de aplicación: **{len(tables_list)}**

Archivo generado: `actual_tables.txt`

---

## 4. COLUMNAS

Total de columnas inventariadas en `actual_columns.txt`.

---

## 5. PRIMARY KEYS

Archivo: `actual_primary_keys.txt`

---

## 6. UNIQUE CONSTRAINTS

Archivo: `actual_unique_constraints.txt`

---

## 7. CHECK CONSTRAINTS

Archivo: `actual_check_constraints.txt`

---

## 8. FOREIGN KEYS (CRÍTICO)

**Total real de FKs (pg_constraint):** `{total_fks}`

**Total FKs únicas por relación:** `{len(fk_by_signature)}`

Archivo detallado: `actual_foreign_keys.txt`

### 8.1 Detección de Duplicados

"""
    if duplicates:
        md += f"⚠️  **{len(duplicates)} grupos de FKs duplicadas detectadas**\n\n"
        for sig, names in sorted(duplicates.items()):
            md += f"- `{sig[0]}.{sig[1]}({sig[2]}) -> {sig[3]}.{sig[4]}({sig[5]})`\n"
            md += f"  - Constraints: `{', '.join(names)}`\n"
    else:
        md += "✅ **No se encontraron FKs duplicadas por relación lógica.**\n"

    md += "\n### 8.2 Especial atención: trip.reserva\n\n"
    for row in reserva_fks:
        md += f"- `{row[0]}`: `{row[3]}` → `{row[4]}.{row[5]}({row[6]})`\n"

    md += f"""
---

## 9. ÍNDICES

Archivo: `actual_indexes.txt`

---

## 10. POSTGIS

Archivo: `actual_postgis.txt`

---

## 11. DEFAULTS

Archivo: `actual_defaults.txt`

Defaults especiales: `actual_special_defaults.txt`

---

## 12. COMPARACIÓN CON ver_db.txt

> ⚠️  **PENDIENTE:** Se requiere el archivo `ver_db.txt` para comparación automática.
>
> Si disponés del archivo, copialo a `fase3_output/ver_db.txt` y ejecutá:
> ```bash
> python fase3_comparar.py
> ```

---

## 13. MODELOS VS BASE DE DATOS

> ⚠️  **PENDIENTE:** Se requiere análisis manual de modelos SQLAlchemy.
>
> Archivos a revisar:
> - `app/models/payment.py` (especial atención a `Transaccion`)
> - Todos los modelos en `app/models/`
>
> Comparar con `actual_columns.txt`.

---

## 14. RIESGOS IDENTIFICADOS

| # | Riesgo | Severidad | Notas |
|---|--------|-----------|-------|
"""

    risk_count = 0
    if duplicates:
        risk_count += 1
        md += f"| {risk_count} | FKs duplicadas detectadas | 🔴 Alta | {len(duplicates)} grupos |\n"

    # Verificar si hay tablas sin PK
    cur.execute(f"""
        SELECT t.table_schema, t.table_name
        FROM information_schema.tables t
        WHERE t.table_schema NOT IN {SCHEMAS_EXCLUDE}
          AND t.table_type = 'BASE TABLE'
          AND NOT EXISTS (
              SELECT 1 FROM information_schema.table_constraints tc
              WHERE tc.table_schema = t.table_schema
                AND tc.table_name = t.table_name
                AND tc.constraint_type = 'PRIMARY KEY'
          )
        ORDER BY t.table_schema, t.table_name;
    """)
    no_pk = cur.fetchall()
    if no_pk:
        risk_count += 1
        md += f"| {risk_count} | Tablas sin Primary Key | 🟡 Media | {len(no_pk)} tablas |\n"

    if not risk_count:
        md += "| - | Ninguno detectado en esta auditoría | 🟢 Baja | - |\n"

    md += f"""
---

## 15. RECOMENDACIONES

1. **Comparar con `ver_db.txt`:** Subir el archivo para análisis automático.
2. **Revisar `payment.py`:** Verificar columnas `provider_id`, `provider_data`, `external_reference`.
3. **Revisar modelos SQLAlchemy:** Comparar todos los modelos contra `actual_columns.txt`.
4. **Si hay duplicadas:** Evaluar si son intencionales o errores históricos.

---

## 16. ARCHIVOS GENERADOS

| Archivo | Descripción |
|---------|-------------|
| `actual_schemas.txt` | Schemas y cantidad de tablas |
| `actual_tables.txt` | Inventario de tablas |
| `actual_columns.txt` | Todas las columnas |
| `actual_primary_keys.txt` | Primary Keys |
| `actual_unique_constraints.txt` | Unique constraints |
| `actual_check_constraints.txt` | Check constraints |
| `actual_foreign_keys.txt` | Foreign Keys detalladas |
| `actual_fk_duplicates.txt` | Detección de FKs duplicadas |
| `actual_indexes.txt` | Índices |
| `actual_postgis.txt` | PostGIS |
| `actual_defaults.txt` | Todos los defaults |
| `actual_special_defaults.txt` | Defaults especiales (UUID, JSONB, etc.) |
| `FASE3_AUDITORIA_FINAL.md` | Este informe |

---

*Fin de la Fase 3. Solo lectura. Sin modificaciones.*
"""

    write_file("FASE3_AUDITORIA_FINAL.md", md)

    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print("✅ FASE 3 COMPLETADA")
    print(f"{'='*60}")
    print(f"📁 Directorio: {OUTPUT_DIR.absolute()}")
    print(f"📄 Archivos generados: {len(list(OUTPUT_DIR.glob('*')))}")
    print(f"🔗 FKs totales en BD: {total_fks}")
    print(f"🔗 FKs únicas: {len(fk_by_signature)}")
    if duplicates:
        print(f"⚠️  FKs duplicadas: {len(duplicates)} grupos")
    else:
        print(f"✅ Sin FKs duplicadas")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_audit()