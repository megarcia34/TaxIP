import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener DATABASE_URL con manejo de error
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("❌ ERROR: DATABASE_URL no encontrada en el archivo .env")
    print("")
    print("Creá el archivo .env con el siguiente contenido:")
    print("DATABASE_URL=postgresql+asyncpg://postgres:TU_PASSWORD@localhost:5432/taxip_db")
    exit(1)

# Reemplazar asyncpg por psycopg2 (para conexión normal)
db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

print(f"🔌 Conectando a: {db_url.replace(db_url.split('@')[0].split(':')[2], '***')}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    print("✅ Conexión exitosa!")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)

print("=" * 80)
print("🔍 DIAGNÓSTICO COMPLETO DE BASE DE DATOS (REAL)")
print("=" * 80)

# =========================
# TABLAS
# =========================
print("\n📋 TABLAS EN SCHEMA 'public':")
cur.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema='public'
ORDER BY table_name;
""")

tablas = [t[0] for t in cur.fetchall()]

if not tablas:
    print("   (No hay tablas en public - usando schemas personalizados)")
    
    # Buscar schemas personalizados (auth, tenant, geo, fleet, trip, payment, audit, notification)
    cur.execute("""
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
    ORDER BY schema_name;
    """)
    
    schemas = [s[0] for s in cur.fetchall()]
    print(f"\n📁 SCHEMAS ENCONTRADOS: {', '.join(schemas)}")
    
    # Mostrar tablas por schema
    for schema in schemas:
        cur.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='{schema}'
        ORDER BY table_name;
        """)
        tables_in_schema = [t[0] for t in cur.fetchall()]
        if tables_in_schema:
            print(f"\n📌 Schema '{schema}':")
            for i, t in enumerate(tables_in_schema, 1):
                print(f"   {i:>2}. {t}")
else:
    for i, t in enumerate(tablas, 1):
        print(f"{i:>2}. {t}")

# =========================
# ESTRUCTURA DE TABLAS (por schema)
# =========================
print("\n" + "=" * 80)
print("📊 ESTRUCTURA DETALLADA")
print("=" * 80)

# Obtener todos los schemas con tablas
cur.execute("""
SELECT DISTINCT table_schema 
FROM information_schema.tables 
WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
ORDER BY table_schema;
""")

schemas = [s[0] for s in cur.fetchall()]

for schema in schemas:
    cur.execute(f"""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='{schema}'
    ORDER BY table_name;
    """)
    tables_in_schema = [t[0] for t in cur.fetchall()]
    
    if tables_in_schema:
        print(f"\n📌 SCHEMA: {schema}")
        print("-" * 60)
        
        for tabla in tables_in_schema:
            print(f"\n   📍 TABLA: {tabla}")
            
            cur.execute(f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{tabla}'
            ORDER BY ordinal_position;
            """)
            
            columnas = cur.fetchall()
            
            for col in columnas:
                default_info = f" DEFAULT {col[3][:30]}" if col[3] else ""
                print(f"      {col[0]:<25} | {col[1]:<20} | {'NULL' if col[2]=='YES' else 'NOT NULL'}{default_info}")

# =========================
# RELACIONES (FOREIGN KEYS)
# =========================
print("\n" + "=" * 80)
print("🔗 RELACIONES (FOREIGN KEYS)")
print("=" * 80)

cur.execute("""
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_schema,
    ccu.table_name AS foreign_table,
    ccu.column_name AS foreign_column
FROM 
    information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_schema, tc.table_name;
""")

fks = cur.fetchall()
if fks:
    for row in fks:
        print(f"   {row[0]}.{row[1]}.{row[2]} → {row[3]}.{row[4]}.{row[5]}")
else:
    print("   (No se encontraron foreign keys)")

# =========================
# ENUMS
# =========================
print("\n" + "=" * 80)
print("🏷️ ENUMS")
print("=" * 80)

cur.execute("""
SELECT t.typname, e.enumlabel
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
ORDER BY t.typname, e.enumsortorder;
""")

enums = {}
for typ, val in cur.fetchall():
    enums.setdefault(typ, []).append(val)

if enums:
    for typ, values in enums.items():
        print(f"   {typ}: {', '.join(values)}")
else:
    print("   (No se encontraron enums)")

# =========================
# POSTGIS EXTENSION
# =========================
print("\n" + "=" * 80)
print("🗺️ POSTGIS")
print("=" * 80)

cur.execute("SELECT postgis_version();")
try:
    postgis_version = cur.fetchone()
    if postgis_version:
        print(f"   ✅ PostGIS instalado: {postgis_version[0][:50]}...")
    else:
        print("   ❌ PostGIS NO está instalado")
except:
    print("   ❌ PostGIS NO está disponible")

conn.close()
print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)