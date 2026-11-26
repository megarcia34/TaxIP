"""
TaxIP 2.0 - Entry point de la aplicacion FastAPI.

FIX CRITICO (2026-09-24): en Windows, Python del sistema usa cp1252 para
stdout/stderr y rompe el StreamHandler del logging_config al escribir
tildes o caracteres no-ASCII.

Forzamos UTF-8 en stdout/stderr al inicio para que los logs salgan
limpios en consola. El archivo taxip.log ya escribe en UTF-8 explicito.
Ver deuda B3.
"""
import asyncio
from contextlib import asynccontextmanager
from io import BytesIO
import io
import logging
import os
import sys
from uuid import UUID

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import qrcode
from sqlalchemy import text

if hasattr(sys.stdout, "buffer") and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer") and sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logger = logging.getLogger(__name__)

# ============================================
# FORZAR IMPORTACION TEMPRANA DE TODOS LOS MODELOS
# ============================================
from app.models.audit import AlertaDesvio, LogGps  # noqa: E402,F401
from app.models.auth import (  # noqa: E402,F401
    DireccionFrecuente,
    PerfilGeneral,
    ResetToken,
    TaxistaFavorito,
    TipoUsuario,
    Usuario,
)
from app.models.fleet import (  # noqa: E402,F401
    ChoferVehiculo,
    ContratoVehiculo,
    GastoVehiculo,
    MantenimientoVehiculo,
    PropietarioVehiculo,
    Vehiculo,
)
from app.models.foto_viaje import FotoViaje  # noqa: E402,F401
from app.models.gasto_turno import GastoTurno  # noqa: E402,F401
from app.models.geo import Ciudad, Pais, Provincia  # noqa: E402,F401
from app.models.notification import Notificacion  # noqa: E402,F401
from app.models.payment import (  # noqa: E402,F401
    Billetera,
    ConfiguracionTarifa,
    MetodoPago,
    Transaccion,
)
from app.models.tenant import Configuracion, ControlBase  # noqa: E402,F401
from app.models.trip import (  # noqa: E402,F401
    Calificacion,
    HistorialEstadoViaje,
    ObjetoOlvidado,
    Panico,
    TipoVehiculo,
    ViajeSolicitado,
)
from app.models.turno import TurnoChofer  # noqa: E402,F401

logger.info("Modelos importados OK")

from app.database import AsyncSessionLocal, get_db  # noqa: E402
from app.dependencies import get_current_super_admin_user  # noqa: E402
from app.routers import (  # noqa: E402
    auth,
    catalogo,
    chofer_documentos,
    chofer_registro,
    choferes,
    choferes_public_router,
    comercio,
    conciliaciones_disputas,
    control_base,
    corporate,
    empresa,
    geo,
    operativo,
    optimizacion,
    pagos,
    pagos_mp,
    rentabilidad,
    reservas,
    turnos,
    usuarios,
    vehiculo,
    vehiculos,
    verificacion,
    viajes,
)
from app.routers.admin.dashboard import router as admin_dashboard_router  # noqa: E402
from app.routers.admin.empresas import router as admin_empresas_router  # noqa: E402
from app.routers.admin.propietarios import router as admin_propietarios_router  # noqa: E402
from app.routers.admin.tarifas import router as admin_tarifas_router  # noqa: E402
from app.routers.admin.tenants import router as admin_tenants_router  # noqa: E402
from app.routers.chofer_finanzas import router as chofer_finanzas_router  # noqa: E402
from app.routers.chofer_registro_progresivo import router as chofer_registro_progresivo_router  # noqa: E402
from app.routers.chofer_splash import router as chofer_splash_router  # noqa: E402
from app.routers.chofer_turnos import router as chofer_turnos_router  # noqa: E402
from app.routers.empleado_turnos import router as empleado_turnos_router  # noqa: E402
from app.routers.empresa_dashboard import router as empresa_dashboard_router  # noqa: E402
from app.routers.liquidacion import router as liquidacion_router  # noqa: E402
from app.routers.propietario import conciliaciones as propietario_conciliaciones  # noqa: E402
from app.routers.propietario import router as propietario_router  # noqa: E402
from app.routers.super_admin import dashboard_router, tenants_router  # noqa: E402
from app.routers.viajes import public_router as viajes_public_router  # noqa: E402
from app.routers.viajes import router as viajes_router  # noqa: E402
from app.websocket.handlers import handle_websocket  # noqa: E402

# Cargar variables de entorno
load_dotenv()

# R16: forzar UTF-8 para evitar UnicodeEncodeError en produccion.
# Ver deuda N10 y logs.auth_prints.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


# ============================================
# Lifespan context manager
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TaxIP API iniciando...")

    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
            logger.info("Conexion a base de datos establecida")
    except Exception as e:
        logger.warning("No se pudo verificar la base de datos: %s", e)

    from app.core.scheduler import scheduler_loop
    scheduler_task = asyncio.create_task(scheduler_loop())
    logger.info("Scheduler arrancado en background")

    yield

    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    logger.info("Scheduler detenido")

    logger.info("TaxIP API cerrando...")


# ============================================
# Crear aplicacion FastAPI
# ============================================
app = FastAPI(
    title="TaxIP API",
    description="API para plataforma de gestion de taxis",
    version="2.0.0",
    lifespan=lifespan
)


# ============================================
# CONFIGURACION CORS
# ============================================
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "https://taxip.com.ar",
    "http://138.36.239.48:3000",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://192.168.1.14:8081"
]

env_origins = os.getenv("FRONTEND_URL", "")
if env_origins:
    for origin in env_origins.split(","):
        if origin.strip():
            origins.append(origin.strip())

origins = list(set(origins))
logger.info("CORS Origins permitidos: %s", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================
# ROUTERS PRINCIPALES
# ============================================
logger.info("Registrando routers...")
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(choferes.router)
app.include_router(chofer_registro.router)
app.include_router(chofer_documentos.router)
app.include_router(vehiculos.router)
app.include_router(vehiculo.router)
app.include_router(viajes_router)
app.include_router(viajes_public_router)
app.include_router(control_base.router)
logger.info("Registrando router de propietario...")
app.include_router(propietario_router, prefix="/api")
logger.info("Router de propietario registrado")
app.include_router(corporate.router)
app.include_router(choferes_public_router)
app.include_router(chofer_finanzas_router)
app.include_router(liquidacion_router)
app.include_router(chofer_registro_progresivo_router)
app.include_router(chofer_turnos_router)
app.include_router(chofer_splash_router)
app.include_router(propietario_conciliaciones.router)
app.include_router(conciliaciones_disputas.router)

# ============================================
# ROUTERS DE SUPER ADMIN
# ============================================
app.include_router(dashboard_router)
app.include_router(tenants_router)

# ============================================
# ROUTER GEO
# ============================================
app.include_router(geo.router)

# ============================================
# ROUTER DE NEUMATICOS: ya incluido en propietario_router
# (eliminado include_router duplicado en R16 - deuda A5)
# ============================================

# ============================================
# ROUTERS DE EMPLEADO
# ============================================
app.include_router(empleado_turnos_router)
app.include_router(operativo.router, prefix="/api")
app.include_router(turnos.router)

# ============================================
# REGISTRAR RENTABILIDAD Y OPTIMIZACION
# ============================================
app.include_router(rentabilidad.router)
app.include_router(optimizacion.router)

# ============================================
# ROUTERS DE ADMINISTRACION
# ============================================
app.include_router(admin_dashboard_router)
app.include_router(admin_propietarios_router, prefix="/api")
app.include_router(admin_empresas_router, prefix="/api")
app.include_router(admin_tenants_router, prefix="/api")
app.include_router(admin_tarifas_router, prefix="/api")

# ============================================
# ROUTER DE RESERVAS
# ============================================
app.include_router(reservas.router, prefix="/api")

# ============================================
# EMPRESA Y DASHBOARD
# ============================================
app.include_router(empresa.router)
app.include_router(empresa_dashboard_router)

# ============================================
# PAGOS, MERCADOPAGO Y OTROS ROUTERS
# ============================================
app.include_router(pagos.router)
app.include_router(pagos_mp.router)
app.include_router(catalogo.router)
app.include_router(comercio.router)
app.include_router(verificacion.router)
app.include_router(viajes.router)

logger.info("Todos los routers registrados")


# ============================================
# QR PUBLICO
# ============================================
@app.get("/public/qr/{qr_uuid}")
async def servir_qr(
    qr_uuid: UUID,
    db=Depends(get_db)
):
    """Servir imagen QR del vehiculo"""
    query = text("""
        SELECT v.id, v.patente, v.qr_activo, v.activo
        FROM fleet.vehiculo v
        WHERE v.qr_uuid = :qr_uuid
    """)
    result = await db.execute(query, {"qr_uuid": qr_uuid})
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="QR no encontrado")

    if not row[2] or not row[3]:
        raise HTTPException(status_code=410, detail="QR inactivo o vehiculo deshabilitado")

    content = f"taxip://vincular?vehiculo={row[0]}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    return Response(
        content=buffered.getvalue(),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f'inline; filename="qr_{row[1]}.png"'
        }
    )


# ============================================
# DEBUG: Ver rutas registradas
# ============================================
@app.get("/debug-routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path if hasattr(route, "path") else str(route),
            "name": route.name if hasattr(route, "name") else None,
            "methods": list(route.methods) if hasattr(route, "methods") else None
        })
    return {"routes": routes}


# ============================================
# WebSocket
# ============================================
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(..., description="JWT de autenticacion"),
):
    from app.core.security import decode_token
    payload = decode_token(token)
    rol = payload.get("tipo", "unknown") if payload else "unknown"
    await handle_websocket(websocket, user_id, rol)


# ============================================
# Endpoints basicos
# ============================================
@app.get("/")
async def root():
    return {
        "message": "TaxIP API v2.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/health/metrics")
async def health_metrics(
    current_user: tuple = Depends(get_current_super_admin_user),
):
    """
    Metricas en memoria de la app.

    R17 - G63: alerta si el motor de precios cae a fallback.

    Devuelve contadores acumulados desde el inicio del proceso.
    Solo accesible para super_admin.

    NO reemplaza monitoreo real (Sentry, Grafana). Cuando se integre
    uno, este endpoint se puede dejar como fallback o eliminar.
    """
    from app.core.metrics import metrics
    return {
        "counters": metrics.snapshot(),
    }