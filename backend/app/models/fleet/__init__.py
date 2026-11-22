# app/models/fleet/__init__.py
# Fachada temporal de R25.5.
# Re-exporta todo de _legacy.py y de los archivos de dominio ya movidos.
from app.models.fleet._legacy import *  # noqa: F401,F403
from app.models.fleet.catalogo import *  # noqa: F401,F403