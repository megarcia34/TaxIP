"""
Script de refactorización FASE 2 - Versión simple sin funciones
"""
import re
import shutil
from pathlib import Path
from datetime import datetime

# Configuración
MIGRATION_FILE = Path("migrations/versions/20260721_191150_initial_migration_from_db.py")
BACKUP_FILE = MIGRATION_FILE.with_suffix('.py.bak')

print("=" * 80)
print("FASE 2: REFACTORIZACIÓN DE MIGRACIÓN INICIAL")
print("=" * 80)

# 1. Backup
print("\n[1/5] Creando backup...")
if BACKUP_FILE.exists():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_ts = MIGRATION_FILE.with_suffix(f'.py.bak_{timestamp}')
    shutil.copy(MIGRATION_FILE, backup_ts)
    print(f"   ✅ Backup adicional: {backup_ts.name}")
else:
    shutil.copy(MIGRATION_FILE, BACKUP_FILE)
    print(f"   ✅ Backup creado: {BACKUP_FILE.name}")

# 2. Leer archivo
print("[2/5] Leyendo archivo...")
with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 3. Extraer FKs
print("[3/5] Extrayendo Foreign Keys...")

# Patrón para FKs: sa.ForeignKeyConstraint(['col'], ['schema.table.col'])
fk_pattern = re.compile(r"sa\.ForeignKeyConstraint\(\s*\['([^']+)'\]\s*,\s*\['([^']+)'\]\s*\)")

# Encontrar todas las FKs
matches = list(fk_pattern.finditer(content))
print(f"   ✅ Total de FKs encontradas: {len(matches)}")

# Procesar FKs y deduplicar
fks_data = []
seen_sigs = set()
duplicates = 0

for match in matches:
    src_col = match.group(1)
    dst_target = match.group(2)
    
    # Parsear destino
    parts = dst_target.split('.')
    if len(parts) == 3:
        dst_schema, dst_table, dst_col = parts
    elif len(parts) == 2:
        dst_schema, dst_table, dst_col = 'public', parts[0], parts[1]
    else:
        print(f"   ⚠️  No se pudo parsear: {dst_target}")
        continue
    
    # Buscar tabla origen (buscar el create_table más cercano antes de esta FK)
    before_text = content[:match.start()]
    table_matches = list(re.finditer(r"op\.create_table\(\s*['\"]([^'\"]+)['\"]", before_text))
    if not table_matches:
        print(f"   ⚠️  No se encontró tabla para FK: {src_col}")
        continue
    
    full_table_name = table_matches[-1].group(1)
    if '.' in full_table_name:
        src_schema, src_table = full_table_name.split('.', 1)
    else:
        src_schema, src_table = 'public', full_table_name
    
    # Firma única
    signature = f"{src_schema}.{src_table}.{src_col} -> {dst_schema}.{dst_table}.{dst_col}"
    
    if signature in seen_sigs:
        duplicates += 1
        print(f"   🗑️  Duplicada: {signature}")
        continue
    
    seen_sigs.add(signature)
    fks_data.append({
        'src_schema': src_schema,
        'src_table': src_table,
        'src_col': src_col,
        'dst_schema': dst_schema,
        'dst_table': dst_table,
        'dst_col': dst_col,
        'signature': signature,
        'match': match
    })

print(f"   ✅ FKs únicas: {len(fks_data)}")
print(f"   ✅ FKs duplicadas eliminadas: {duplicates}")

if len(fks_data) == 0:
    print("   ❌ ERROR: No se encontraron FKs")
    exit(1)

# 4. Reemplazar FKs inline con comentarios
print("[4/5] Reemplazando FKs inline...")
new_content = content

# Reemplazar desde el final para no afectar posiciones
for fk in reversed(fks_data):
    match = fk['match']
    # Reemplazar toda la línea de la FK con un comentario
    start = match.start()
    end = match.end()
    
    # Encontrar el inicio y fin de la línea completa
    line_start = new_content.rfind('\n', 0, start) + 1
    line_end = new_content.find('\n', end)
    if line_end == -1:
        line_end = len(new_content)
    
    # Reemplazar la línea completa
    indent = ' ' * 4  # Indentación de 4 espacios
    comment = f"{indent}# FK EXTRAÍDA: {fk['src_col']} -> {fk['dst_schema']}.{fk['dst_table']}.{fk['dst_col']}"
    new_content = new_content[:line_start] + comment + new_content[line_end:]

# 5. Generar bloques de código
print("[5/5] Generando bloques de upgrade y downgrade...")

# Bloque upgrade
upgrade_lines = ["\n    # ============================================================"]
upgrade_lines.append("    # FASE B: CREACIÓN DE FOREIGN KEYS")
upgrade_lines.append("    # ============================================================")

for fk in fks_data:
    constraint_name = f"fk_{fk['src_table']}_{fk['src_col']}"[:63]
    upgrade_lines.append(f"    op.create_foreign_key(")
    upgrade_lines.append(f"        '{constraint_name}',")
    upgrade_lines.append(f"        '{fk['src_table']}',")
    upgrade_lines.append(f"        '{fk['dst_table']}',")
    upgrade_lines.append(f"        ['{fk['src_col']}'],")
    upgrade_lines.append(f"        ['{fk['dst_col']}'],")
    upgrade_lines.append(f"        source_schema='{fk['src_schema']}',")
    upgrade_lines.append(f"        referent_schema='{fk['dst_schema']}'")
    upgrade_lines.append(f"    )")

upgrade_block = '\n'.join(upgrade_lines)

# Bloque downgrade
downgrade_lines = ["    # ============================================================"]
downgrade_lines.append("    # ELIMINAR FOREIGN KEYS")
downgrade_lines.append("    # ============================================================")

for fk in reversed(fks_data):
    constraint_name = f"fk_{fk['src_table']}_{fk['src_col']}"[:63]
    downgrade_lines.append(f"    op.drop_constraint('{constraint_name}', '{fk['src_table']}', schema='{fk['src_schema']}', type_='foreignkey')")

downgrade_block = '\n'.join(downgrade_lines)

# Insertar bloques
# Upgrade: antes de "def downgrade"
upgrade_pos = new_content.find('def downgrade()')
if upgrade_pos != -1:
    new_content = new_content[:upgrade_pos] + upgrade_block + '\n\n' + new_content[upgrade_pos:]

# Downgrade: después de "def downgrade() -> None:\n"
downgrade_pos = new_content.find('def downgrade() -> None:\n')
if downgrade_pos != -1:
    insert_pos = downgrade_pos + len('def downgrade() -> None:\n')
    new_content = new_content[:insert_pos] + '\n' + downgrade_block + '\n\n' + new_content[insert_pos:]

# Guardar archivo
with open(MIGRATION_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Validar sintaxis
print("\n[6/6] Validando sintaxis...")
import py_compile
try:
    py_compile.compile(MIGRATION_FILE, doraise=True)
    print("   ✅ Sintaxis válida")
except py_compile.PyCompileError as e:
    print(f"   ❌ ERROR: {e}")
    print("   🔄 Restaurando backup...")
    shutil.copy(BACKUP_FILE, MIGRATION_FILE)
    exit(1)

# Generar reporte
with open("refactor_report.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("REPORTE DE REFACTORIZACIÓN\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"FKs totales encontradas: {len(matches)}\n")
    f.write(f"FKs duplicadas eliminadas: {duplicates}\n")
    f.write(f"FKs únicas creadas: {len(fks_data)}\n\n")
    f.write("LISTA DE FKs:\n")
    for i, fk in enumerate(fks_data, 1):
        f.write(f"{i:3d}. {fk['signature']}\n")

print("\n" + "=" * 80)
print("✅ REFACTORIZACIÓN COMPLETADA")
print("=" * 80)
print(f"\n📄 Reporte: refactor_report.txt")
print(f"📄 Backup: {BACKUP_FILE.name}")
print("\n⚠️  PRÓXIMO PASO: Revisar git diff")