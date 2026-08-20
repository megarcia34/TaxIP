"""
Módulo de Neumáticos para Propietario
"""
from fastapi import APIRouter
from .configuracion import router as configuracion_router
from .vehiculo_neumaticos import router as vehiculo_neumaticos_router
from .neumatico_individual import router as neumatico_individual_router
from .operaciones import router as operaciones_router
from .sugerencias import router as sugerencias_router
from .imagenes import router as imagenes_router  # ← NUEVO

router = APIRouter()

router.include_router(configuracion_router)
router.include_router(vehiculo_neumaticos_router)
router.include_router(neumatico_individual_router)
router.include_router(operaciones_router)
router.include_router(sugerencias_router)
router.include_router(imagenes_router)  # ← NUEVO