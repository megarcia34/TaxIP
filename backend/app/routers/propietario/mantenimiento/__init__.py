"""
Router de mantenimiento para propietario.

Agrupa:
- Planes (CRUD + items + asignacion).
- Vencimientos (listado + resolucion).

Reemplaza al legacy propietario/mantenimientos.py (se elimina en Fase 7).
"""
from fastapi import APIRouter
from app.routers.propietario.mantenimiento import planes, vencimientos

router = APIRouter(
    prefix="/mantenimiento",
    tags=["Propietario - Mantenimiento"],
)

router.include_router(planes.router, prefix="/planes", tags=["Planes"])
router.include_router(vencimientos.router, prefix="/vencimientos", tags=["Vencimientos"])