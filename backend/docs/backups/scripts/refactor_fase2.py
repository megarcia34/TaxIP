"""
FASE 2: Refactorización Controlada de la Migración Inicial TAXIP
Extrae FKs inline de op.create_table() y las convierte en op.create_foreign_key()
"""
import os
import re
import shutil
import py_compile
from pathlib import Path
from datetime import datetime

MIGRATION_FILE = Path("migrations/versions/20260721_191150_initial_migration_from_db.py")
BACKUP_FILE = MIGRATION_FILE.with_suffix('.py.bak')

# Estadísticas
stats = {
    'fk_found': 0,
    'fk_duplicates_removed': 0,
    'fk_final': 0
}

def create_backup():
    """Crea backup con timestamp si ya existe uno"""
    if BACKUP_FILE.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_ts = MIGRATION_FILE.with_suffix(f'.py.bak_{timestamp}')
        shutil.copy(MIGRATION_FILE, backup_ts)
        print(f"✅ Backup adicional creado: {backup_ts.name}")
    else:
        shutil.copy(MIGRATION_FILE, BACKUP_FILE)
        print(f"✅ Backup creado: {BACKUP_FILE.name}")

def refactor():
    print("=" * 80)
    print("FASE 2: REFACTORIZACIÓN DE MIGRACIÓN INICIAL")
    print("=" * 80)
    
    # 1. Backup
    print("\n[1/6] Creando backup...")
    create_backup()
    
    # 2. Leer archivo
    print("[2/6] Leyendo archivo original...")
    with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. Extraer FKs usando Regex robusto para bloques SQLAlchemy
    print("[3/6] Extrayendo Foreign Keys...")
    
    # Patrón para capturar sa.ForeignKeyConstraint(..., name='...')
    # Captura desde 'sa.ForeignKeyConstraint' hasta el cierre de paréntesis correspondiente
    fk_pattern = re.compile(
        r'(sa\.ForeignKeyConstraint\s*\(\s*\[([^\]]+)\]\s*,\s*\[([^\]]+)\](?:\s*,\s*name\s*=\s*[\'"]([^\'"]+)[\'"])?(?:\s*,\s*ondelete\s*=\s*[\'"]([^\'"]+)[\'"])?\s*\))',
        re.DOTALL
    )
    
    fks_found = []
    duplicates_removed = 0
    seen_signatures = set()
    
    # Necesitamos saber en qué tabla estamos. Buscamos op.create_table
    table_pattern = re.compile(r"op\.create_table\(\s*['\"]([^'\"]+)['\"]", re.DOTALL)
    
    # Dividimos el contenido en bloques para rastrear el contexto de la tabla
    # Esta es una simplificación segura para archivos de migración generados
    lines = content.split('\n')
    current_table = None
    current_schema = 'public'
    
    # Reconstrucción del contenido sin las FKs inline
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detectar inicio de create_table
        table_match = re.search(r"op\.create_table\(\s*['\"]([^'\"]+)['\"]", line)
        if table_match:
            current_table = table_match.group(1)
            # Buscar schema en las siguientes líneas
            for j in range(i, min(i+10, len(lines))):
                schema_match = re.search(r"schema\s*=\s*['\"]([^'\"]+)['\"]", lines[j])
                if schema_match:
                    current_schema = schema_match.group(1)
                    break
        
        # Detectar ForeignKeyConstraint
        fk_match = fk_pattern.search(line)
        if fk_match and current_table:
            src_cols_str = fk_match.group(2).strip().strip("'\"")
            dst_target_str = fk_match.group(3).strip().strip("'\"")
            constraint_name = fk_match.group(4) if fk_match.group(4) else f"fk_{current_table}_{src_cols_str}"
            ondelete = fk_match.group(5)
            
            # Limpiar nombres de columna
            src_col = src_cols_str.replace("'", "").replace('"', "").strip()
            
            # Parsear destino: 'schema.table.column' o 'table.column'
            dst_parts = dst_target_str.replace("'", "").replace('"', "").strip().split('.')
            if len(dst_parts) == 3:
                dst_schema, dst_table, dst_col = dst_parts
            elif len(dst_parts) == 2:
                dst_schema, dst_table, dst_col = 'public', dst_parts[0], dst_parts[1]
            else:
                dst_schema, dst_table, dst_col = current_schema, 'unknown', dst_parts[0]
            
            # Firma única para deduplicación
            signature = f"{current_schema}.{current_table}.{src_col} -> {dst_schema}.{dst_table}.{dst_col}"
            
            if signature in seen_signatures:
                duplicates_removed += 1
                print(f"   🗑️  Duplicada eliminada: {current_table}.{src_col} -> {dst_table}.{dst_col}")
                # Reemplazar la línea de la FK con nada (o comentario)
                new_lines.append(f"                # FK DUPLICADA ELIMINADA: {src_col} -> {dst_target_str}")
            else:
                seen_signatures.add(signature)
                fks_found.append({
                    'constraint_name': constraint_name,
                    'src_schema': current_schema,
                    'src_table': current_table,
                    'src_col': src_col,
                    'dst_schema': dst_schema,
                    'dst_table': dst_table,
                    'dst_col': dst_col,
                    'ondelete': ondelete,
                    'signature': signature
                })
                # Reemplazar la línea de la FK con un comentario marcador
                new_lines.append(f"                # FK EXTRAÍDA: {src_col} -> {dst_target_str}")
            
            stats['fk_found'] += 1
            i += 1
            continue
            
        new_lines.append(line)
        i += 1
    
    stats['fk_duplicates_removed'] = duplicates_removed
    stats['fk_final'] = len(fks_found)
    print(f"   ✅ FKs encontradas: {stats['fk_found']}")
    print(f"   ✅ FKs duplicadas eliminadas: {stats['fk_duplicates_removed']}")
    print(f"   ✅ FKs únicas a crear: {stats['fk_final']}")
    
    if stats['fk_found'] == 0:
        print("   ❌ ERROR: No se encontraron FKs. Abortando.")
        return False
    
    # 4. Generar código de upgrade (al final)
    print("[4/6] Generando bloque de upgrade()...")
    upgrade_fk_block = "\n    # ============================================================\n"
    upgrade_fk_block += "    # FASE B: CREACIÓN DE FOREIGN KEYS (Post-Create Tables)\n"
    upgrade_fk_block += "    # ============================================================\n"
    
    for fk in fks_found:
        name = fk['constraint_name'].replace("'", "").replace('"', "").replace(" ", "_")[:63]
        ondelete_str = f", ondelete='{fk['ondelete']}'" if fk['ondelete'] else ""
        upgrade_fk_block += f"""    op.create_foreign_key(
        '{name}',
        '{fk['src_table']}',
        '{fk['dst_table']}',
        ['{fk['src_col']}'],
        ['{fk['dst_col']}'],
        source_schema='{fk['src_schema']}',
        referent_schema='{fk['dst_schema']}'{ondelete_str}
    )\n"""
    
    # 5. Generar código de downgrade (al inicio)
    print("[5/6] Generando bloque de downgrade()...")
    downgrade_fk_block = "    # ============================================================\n"
    downgrade_fk_block += "    # ELIMINAR FOREIGN KEYS (Pre-Drop Tables)\n"
    downgrade_fk_block += "    # ============================================================\n"
    
    for fk in reversed(fks_found):
        name = fk['constraint_name'].replace("'", "").replace('"', "").replace(" ", "_")[:63]
        downgrade_fk_block += f"    op.drop_constraint('{name}', '{fk['src_table']}', schema='{fk['src_schema']}', type_='foreignkey')\n"
    
    # 6. Ensamblar archivo final
    print("[6/6] Ensamblando y guardando archivo refactorizado...")
    new_content = '\n'.join(new_lines)
    
    # Insertar bloque upgrade al final de la función upgrade (antes del def downgrade)
    # Buscamos el último 'op.create_table' o similar y agregamos después, o simplemente antes de 'def downgrade'
    upgrade_match = re.search(r'(def downgrade\(\) -> None:)', new_content)
    if upgrade_match:
        insert_pos = upgrade_match.start()
        new_content = new_content[:insert_pos] + upgrade_fk_block + "\n" + new_content[insert_pos:]
    
    # Insertar bloque downgrade al inicio de la función downgrade
    downgrade_match = re.search(r'(def downgrade\(\) -> None:\n)', new_content)
    if downgrade_match:
        insert_pos = downgrade_match.end()
        new_content = new_content[:insert_pos] + "\n" + downgrade_fk_block + new_content[insert_pos:]
    
    with open(MIGRATION_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # 7. Validación py_compile
    print("\n[7/7] Validando sintaxis con py_compile...")
    try:
        py_compile.compile(MIGRATION_FILE, doraise=True)
        print("   ✅ Sintaxis de Python válida.")
    except py_compile.PyCompileError as e:
        print(f"   ❌ ERROR DE SINTAXIS: {e}")
        print("   🔄 Restaurando backup...")
        shutil.copy(BACKUP_FILE, MIGRATION_FILE)
        return False
    
    # 8. Generar reportes
    print("\n[8/8] Generando reportes...")
    with open("migration_fk_inventory.txt", "w", encoding="utf-8") as f:
        f.write(f"Total FKs extraídas: {stats['fk_final']}\n")
        f.write(f"FKs duplicadas eliminadas: {stats['fk_duplicates_removed']}\n\n")
        for i, fk in enumerate(fks_found, 1):
            f.write(f"{i:3d}. {fk['src_schema']}.{fk['src_table']}.{fk['src_col']} -> {fk['dst_schema']}.{fk['dst_table']}.{fk['dst_col']}\n")
            f.write(f"     Constraint: {fk['constraint_name']}\n\n")
            
    with open("migration_refactor_summary.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\nRESUMEN DE REFACTORIZACIÓN FASE 2\n" + "=" * 80 + "\n\n")
        f.write(f"FKs originales detectadas: {stats['fk_found']}\n")
        f.write(f"FKs duplicadas eliminadas: {stats['fk_duplicates_removed']}\n")
        f.write(f"FKs finales en migración:  {stats['fk_final']}\n\n")
        f.write("VALIDACIONES:\n")
        f.write("✅ Backup creado\n✅ FKs movidas a op.create_foreign_key()\n✅ Drops agregados a downgrade()\n✅ py_compile exitoso\n")
        
    with open("migration_refactor_diff.txt", "w", encoding="utf-8") as f:
        f.write("Para ver el diff completo, ejecutar en terminal:\n")
        f.write(f"git diff {MIGRATION_FILE}\n\n")
        f.write("CAMBIOS CLAVE:\n")
        f.write(f"- Eliminadas {stats['fk_found']} declaraciones sa.ForeignKeyConstraint de create_table()\n")
        f.write(f"- Agregadas {stats['fk_final']} llamadas a op.create_foreign_key() al final de upgrade()\n")
        f.write(f"- Agregadas {stats['fk_final']} llamadas a op.drop_constraint() al inicio de downgrade()\n")

    print("\n" + "=" * 80)
    print("✅ REFACTORIZACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    print("\n📄 Archivos generados:")
    print("   - migration_fk_inventory.txt")
    print("   - migration_refactor_summary.txt")
    print("   - migration_refactor_diff.txt")
    print("\n⚠️  PRÓXIMO PASO: Revisar los reportes y el git diff.")
    print("   NO ejecutar 'alembic upgrade head' todavía.")
    
    return True

if __name__ == "__main__":
    if not MIGRATION_FILE.exists():
        print(f"❌ No se encontró el archivo: {MIGRATION_FILE}")
    else:
        success = refactor()
        if not success:
            print("\n❌ FASE 2 FALLIDA. El archivo original ha sido restaurado.")