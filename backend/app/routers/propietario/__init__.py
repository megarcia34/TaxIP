from fastapi import APIRouter
from .contratos import router as contratos_router
from .documentos import router as documentos_router
from .finanzas import router as finanzas_router
from .gastos import router as gastos_router
from .ingresos import router as ingresos_router
from .mantenimientos import router as mantenimientos_router
from .reportes import router as reportes_router
from .turnos import router as turnos_router
from .vehiculos import router as vehiculos_router
from .alertas import router as alertas_router
from .fotos_vehiculo import router as fotos_router
from .neumaticos import router as neumaticos_router  
from .qr import router as qr_router
from .dashboard import router as dashboard_router
from .medios_pago import router as medios_pago_router
from .perfil import router as perfil_router  # <--- NUEVO

router = APIRouter(prefix="/propietario", tags=["Propietario"])

router.include_router(contratos_router)
router.include_router(documentos_router)
router.include_router(finanzas_router)
router.include_router(gastos_router)
router.include_router(ingresos_router)
router.include_router(mantenimientos_router)
router.include_router(reportes_router)
router.include_router(turnos_router)
router.include_router(vehiculos_router)
router.include_router(qr_router)
router.include_router(alertas_router)
router.include_router(fotos_router)
router.include_router(neumaticos_router)
router.include_router(dashboard_router)
router.include_router(medios_pago_router)
router.include_router(perfil_router)  # <--- NUEVO