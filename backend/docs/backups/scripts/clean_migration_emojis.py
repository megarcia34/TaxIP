#!/usr/bin/env python3
"""
Script para eliminar emojis y caracteres no-ASCII problemáticos
de las migraciones de Alembic (causan UnicodeEncodeError en Windows con --sql).

Uso:
    python clean_migration_emojis.py
"""

import re
from pathlib import Path

MIGRATIONS_DIR = Path("migrations/versions")

# Patrón de emojis y caracteres fuera de BMP que causan problemas en cp1252
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251" 
    "]+",
    flags=re.UNICODE,
)


def clean_file(filepath: Path) -> int:
    """Elimina emojis de un archivo. Retorna cantidad de emojis eliminados."""
    content = filepath.read_text(encoding="utf-8")
    cleaned = EMOJI_PATTERN.sub("", content)

    emojis_found = len(EMOJI_PATTERN.findall(content))

    if cleaned != content:
        # Backup
        backup = filepath.with_suffix(filepath.suffix + ".emoji_bak")
        backup.write_text(content, encoding="utf-8")
        filepath.write_text(cleaned, encoding="utf-8")

    return emojis_found


def main():
    if not MIGRATIONS_DIR.exists():
        print(f"❌ No se encontró: {MIGRATIONS_DIR}")
        return

    total_emojis = 0
    files_changed = 0

    for py_file in sorted(MIGRATIONS_DIR.glob("*.py")):
        if py_file.name in ("__init__.py",):
            continue
        count = clean_file(py_file)
        if count > 0:
            print(f"   🧹 {py_file.name}: {count} emoji(s) eliminado(s)")
            total_emojis += count
            files_changed += 1

    print()
    if total_emojis > 0:
        print(f"✅ Listo. {total_emojis} emoji(s) eliminado(s) de {files_changed} archivo(s).")
        print("   Backups creados con extensión .emoji_bak")
    else:
        print("✅ No se encontraron emojis en las migraciones.")


if __name__ == "__main__":
    main()