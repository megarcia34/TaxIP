#!/usr/bin/env python
"""
TaxIP 2.0 - Entry Point
Ejecución: python run.py
"""

import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Solo para desarrollo
        log_level="info"
    )