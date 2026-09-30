#!/usr/bin/env python
"""
TaxIP 2.0 - Entry Point
Ejecución: python run.py
"""

import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno ANTES de configurar logging
load_dotenv()

# Configurar logging (archivo rotativo + consola)
from app.core.logging_config import setup_logging
setup_logging()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        reload_excludes=["scripts/*", "*.py.bak"],
        log_level="info",
        log_config=None,  # <-- NUEVO: usar nuestro logging_config
    )