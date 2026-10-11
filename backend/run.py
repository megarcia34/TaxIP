#!/usr/bin/env python
"""
TaxIP 2.0 - Entry Point
Ejecucion: python run.py
"""

import os
import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno ANTES de configurar logging
load_dotenv()

# Configurar logging (archivo rotativo + consola)
from app.core.logging_config import setup_logging
setup_logging()


if __name__ == "__main__":
    # Deuda G82: reload controlado por env var (NO hardcodeado).
    # Uso: $env:RELOAD = "true" antes de python run.py
    # Por defecto: false (evita cargar versiones viejas de workers).
    reload_flag = os.getenv("RELOAD", "false").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_flag,
        reload_dirs=["app"] if reload_flag else None,
        reload_excludes=["scripts/*", "*.py.bak"] if reload_flag else None,
        log_level="info",
        log_config=None,  # <-- NUEVO: usar nuestro logging_config
    )