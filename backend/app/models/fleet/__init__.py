# app/models/fleet/__init__.py
# Fachada temporal de R25.5 Fase 1.
# Re-exporta todo de _legacy.py. Se ira vaciando a medida que se
# muevan clases a los archivos de dominio en Fase 2.
from app.models.fleet._legacy import *  # noqa: F401,F403
