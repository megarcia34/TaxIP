# app/routers/propietario/__init__.py

from fastapi import APIRouter

from app.routers.propietario.vehiculos import router as vehiculos_router
from app.routers.propietario.gastos import router as gastos_router
from app.routers.propietario.mantenimientos import router as mantenimientos_router
from app.routers.propietario.contratos import router as contratos_router
from app.routers.propietario.ingresos import router as ingresos_router
from app.routers.propietario.finanzas import router as finanzas_router
from app.routers.propietario.documentos import router as documentos_router
from app.routers.propietario.reportes import router as reportes_router
from app.routers.propietario.turnos import router as turnos_router  # 🆕 NUEVO

router = APIRouter(prefix="/api/propietario", tags=["Propietario"])

router.include_router(vehiculos_router)
router.include_router(gastos_router)
router.include_router(mantenimientos_router)
router.include_router(contratos_router)
router.include_router(ingresos_router)
router.include_router(finanzas_router)
router.include_router(documentos_router)
router.include_router(reportes_router)
router.include_router(turnos_router)  # 🆕 NUEVO