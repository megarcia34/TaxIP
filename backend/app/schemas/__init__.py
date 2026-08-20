"""
Pydantic schemas for request/response validation
"""

from app.schemas.auth_schemas import *
from app.schemas.usuario_schemas import *
from app.schemas.payment_schemas import *
from app.schemas.propietario_schemas import *
from app.schemas.tenant import *

# NOTA: Los schemas de viajes están en app/routers/viajes/schemas.py
# y se importan directamente desde allí en los routers