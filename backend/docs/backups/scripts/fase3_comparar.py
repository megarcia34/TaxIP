#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparador: BD actual vs ver_db.txt

Uso:
    1. Copiar ver_db.txt a fase3_output/ver_db.txt
    2. python fase3_comparar.py
"""

import re
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path("fase3_output")
VER_DB_PATH = OUTPUT_DIR / "ver_db.txt"


def parse_ver_db(filepath):
    """Parsea ver_db.txt y extrae tablas, columnas, constraints."""
    content = filepath.read_text(encoding='utf-8')

    # Extraer tablas (líneas que empiezan con CREATE TABLE o similares)
    tables = set()
    columns = defaultdict(list)
    fks = []
    pks = []
    indexes = []

    current_table = None
    for line in content.split('\n'):
        line = line.strip()

        # Detectar tabla
        m = re.match(r'CREATE TABLE\s+([\w.]+)', line, re.IGNORECASE)
        if m:
            current_table = m.group(1)
            tables.add(current_table)

        # Detectar columnas dentro de CREATE TABLE
        if current_table and line and not line.startswith('--') and not line.startswith('CREATE'):
            col_match = re.match(r'"?(\w+)"?\s+(\w+)', line)
            if col_match:
                col_name = col_match.group(1)
                col_type = col_match.group(2)
                if col_name.lower() not in ('primary', 'foreign', 'constraint', 'unique', 'check'):
                    columns[current_table].append((col_name, col_type))

        # Detectar FK
        fk_match = re.search(r'FOREIGN KEY.*?REFERENCES\s+([\w.]+)', line, re.IGNORECASE)
        if fk_match:
            fks.append(line)

        # Detectar PK
        pk_match = re.search(r'PRIMARY KEY', line, re.IGNORECASE)
        if pk_match and current_table:
            pks.append(current_table)

    return {
        'tables': tables,
        'columns': columns,
        'fks': fks,
        'pks': set(pks),
        'indexes': indexes,
    }


def parse_actual_tables(filepath):
    """Parsea actual_tables.txt"""
    lines = filepath.read_text(encoding='utf-8').split('\n')
    tables = set()
    for line in lines:
        if line.startswith('|') and not line.startswith('+-') and 'schema' not in line.lower():
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3 and parts[1] and parts[2]:
                tables.add(f"{parts[1]}.{parts[2]}")
    return tables


def main():
    if not VER_DB_PATH.exists():
        print(f"❌ No se encontró {VER_DB_PATH}")
        print("   Copiá ver_db.txt a fase3_output/ver_db.txt y volvé a ejecutar.")
        return

    print("📊 Parseando ver_db.txt...")
    ver_db = parse_ver_db(VER_DB_PATH)

    print("📊 Parseando actual_tables.txt...")
    actual_tables_file = OUTPUT_DIR / "actual_tables.txt"
    if not actual_tables_file.exists():
        print("❌ No se encontró actual_tables.txt. Ejecutá primero fase3_auditoria.py")
        return

    actual_tables = parse_actual_tables(actual_tables_file)

    # Comparar tablas
    only_in_ver = ver_db['tables'] - actual_tables
    only_in_actual = actual_tables - ver_db['tables']
    common = ver_db['tables'] & actual_tables

    report = []
    report.append("=" * 60)
    report.append("COMPARACIÓN: ver_db.txt vs BASE ACTUAL")
    report.append("=" * 60)
    report.append("")
    report.append(f"Tablas en ver_db.txt: {len(ver_db['tables'])}")
    report.append(f"Tablas en BD actual: {len(actual_tables)}")
    report.append(f"Tablas en común: {len(common)}")
    report.append("")

    if only_in_ver:
        report.append(f"⚠️  Tablas SOLO en ver_db.txt ({len(only_in_ver)}):")
        for t in sorted(only_in_ver):
            report.append(f"   - {t}")
        report.append("")

    if only_in_actual:
        report.append(f"⚠️  Tablas SOLO en BD actual ({len(only_in_actual)}):")
        for t in sorted(only_in_actual):
            report.append(f"   + {t}")
        report.append("")

    if not only_in_ver and not only_in_actual:
        report.append("✅ Las tablas coinciden exactamente.")
        report.append("")

    report.append("=" * 60)
    report.append("CLASIFICACIÓN DE DIFERENCIAS")
    report.append("=" * 60)
    report.append("")
    report.append("A = diferencia confirmada")
    report.append("B = diferencia probablemente histórica")
    report.append("C = diferencia causada por la refactorización")
    report.append("D = diferencia no explicada")
    report.append("")

    # Guardar reporte
    report_text = '\n'.join(report)
    out_path = OUTPUT_DIR / "comparison_ver_db.txt"
    out_path.write_text(report_text, encoding='utf-8')

    print(report_text)
    print(f"\n📄 Reporte guardado: {out_path}")


if __name__ == "__main__":
    main()