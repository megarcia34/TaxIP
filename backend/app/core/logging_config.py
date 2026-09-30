"""
Configuración centralizada de logging para TaxIP.

- Escribe a consola (stdout) con formato legible.
- Escribe a logs/taxip.log con rotación automática (10 MB x 5 backups).
- Encoding UTF-8 en archivo (mata mojibake en logs).
- Nivel configurable por env var LOG_LEVEL (default INFO).
- Silencia SQLAlchemy aunque el engine tenga echo=True.
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "taxip.log"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SQLALCHEMY_LEVEL = os.getenv("SQLALCHEMY_LOG_LEVEL", "WARNING").upper()

MAX_BYTES = 10 * 1024 * 1024   # 10 MB
BACKUP_COUNT = 5

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ============================================================
# SETUP
# ============================================================

_configured = False


def setup_logging() -> None:
    """
    Configura logging para toda la app. Idempotente dentro del mismo
    proceso: llamarla varias veces no duplica handlers.
    """
    global _configured
    if _configured:
        return

    # Crear directorio de logs si no existe
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Formatter común
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Handler de archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(LOG_FILE),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(LOG_LEVEL)

    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LOG_LEVEL)

    # Root logger
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    # Limpiar handlers previos (por si uvicorn/sqlalchemy ya configuraron algo)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    # ============================================================
    # Uvicorn: que use nuestros handlers (heredando del root)
    # ============================================================
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

    # ============================================================
    # SQLAlchemy: matar handlers propios y forzar nivel
    # ============================================================
    # SQLAlchemy es verboso por default. Aunque database.py tenga echo=True,
    # esto lo silencia en runtime.
    SQLALCHEMY_LOGGERS = (
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.engine.Engine",
        "sqlalchemy.pool",
        "sqlalchemy.orm",
        "sqlalchemy.dialects",
    )
    for name in SQLALCHEMY_LOGGERS:
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
        lg.setLevel(SQLALCHEMY_LEVEL)

    # asyncio y asyncpg: silenciar ruido
    logging.getLogger("asyncio").setLevel("WARNING")
    logging.getLogger("asyncpg").setLevel("WARNING")

    _configured = True

    logging.getLogger(__name__).info(
        "Logging configurado | archivo=%s | nivel=%s | sqlalchemy=%s",
        LOG_FILE, LOG_LEVEL, SQLALCHEMY_LEVEL
    )