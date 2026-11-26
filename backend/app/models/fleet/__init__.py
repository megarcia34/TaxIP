# app/models/fleet/__init__.py
# Fachada temporal de R25.5.
# Re-exporta todo de _legacy.py y de los archivos de dominio ya movidos.
from app.models.fleet._legacy import *  # noqa: F401,F403
from app.models.fleet.catalogo import *  # noqa: F401,F403
from app.models.fleet.contrato import *  # noqa: F401,F403
from app.models.fleet.documento import *  # noqa: F401,F403
from app.models.fleet.neumatico import *  # noqa: F401,F403
from app.models.fleet.gasto import *  # noqa: F401,F403
from app.models.fleet.encargado import *  # noqa: F401,F403
from app.models.fleet.correccion import *  # noqa: F401,F403
from app.models.fleet.vehiculo import *  # noqa: F401,F403
from app.models.fleet.chofer import *  # noqa: F401,F403
from app.models.fleet.ingreso_turno import *  # noqa: F401,F403
from app.models.fleet.mantenimiento import *  # noqa: F401,F403