# ============================================
# FORZAR IMPORTACIÓN TEMPRANA DE TODOS LOS MODELOS
# ============================================
from app.models.tenant import ControlBase, Configuracion
from app.models.auth import Usuario, TipoUsuario, PerfilGeneral, DireccionFrecuente, TaxistaFavorito, ResetToken
from app.models.fleet import Vehiculo, ChoferVehiculo, GastoVehiculo, MantenimientoVehiculo, PropietarioVehiculo, ContratoVehiculo
from app.models.trip import ViajeSolicitado, HistorialEstadoViaje, Panico, Calificacion, ObjetoOlvidado, TipoVehiculo
from app.models.payment import MetodoPago, Billetera, Transaccion, ConfiguracionTarifa
from app.models.geo import Pais, Provincia, Ciudad
from app.models.notification import Notificacion
from app.models.foto_viaje import FotoViaje
from app.models.turno import TurnoChofer
from app.models.gasto_turno import GastoTurno
from app.models.audit import LogGps, AlertaDesvio
print("✅ Todos los modelos importados")

from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
from sqlalchemy import text
from uuid import UUID
import qrcode
from io import BytesIO
import os
from app.routers import turnos
from dotenv import load_dotenv
from app.routers import operativo

from app.database import get_db, AsyncSessionLocal
from app.websocket.handlers import handle_websocket

# Importar routers principales
from app.routers import auth, choferes, chofer_registro, chofer_documentos, control_base
from app.routers import pagos, usuarios, vehiculo, vehiculos, viajes, catalogo
from app.routers import comercio, empresa
from app.routers import choferes_public_router
from app.routers.viajes import router as viajes_router
from app.routers.viajes import public_router as viajes_public_router
from app.routers.propietario import router as propietario_router

# Importar routers de admin
from app.routers.admin.propietarios import router as admin_propietarios_router
from app.routers.admin.empresas import router as admin_empresas_router
from app.routers.admin.tenants import router as admin_tenants_router
from app.routers.admin.tarifas import router as admin_tarifas_router

# NUEVOS ROUTERS
from app.routers.empleado_turnos import router as empleado_turnos_router

# ROUTER DE RESERVAS
from app.routers import reservas

# Importar dashboard de empresa
from app.routers.empresa_dashboard import router as empresa_dashboard_router

# ✅ ROUTER DE VERIFICACIÓN (agregar)
from app.routers import verificacion

# Cargar variables de entorno
load_dotenv()

# ============================================
# Lifespan context manager
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 TaxIP API iniciando...")
    
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
            print("✅ Conexión a base de datos establecida")
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudo verificar la base de datos: {e}")
    
    yield
    print("🛑 TaxIP API cerrando...")

# ============================================
# Crear aplicación FastAPI
# ============================================
app = FastAPI(
    title="TaxIP API",
    description="API para plataforma de gestión de taxis",
    version="2.0.0",
    lifespan=lifespan
)

# ============================================
# CONFIGURACIÓN CORS
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
]

env_origins = os.getenv("FRONTEND_URL", "")
if env_origins:
    for origin in env_origins.split(","):
        if origin.strip():
            origins.append(origin.strip())

origins = list(set(origins))
print(f"🔗 CORS Origins permitidos: {origins}")

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
app.include_router(propietario_router)
app.include_router(choferes_public_router)

# ============================================
# ROUTERS DE EMPLEADO
# ============================================
app.include_router(empleado_turnos_router)
app.include_router(operativo.router, prefix="/api")
app.include_router(turnos.router)

# ============================================
# ROUTERS DE ADMINISTRACIÓN
# ============================================
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
# OTROS ROUTERS
# ============================================
app.include_router(pagos.router)
app.include_router(catalogo.router)
app.include_router(comercio.router)

# ✅ ROUTER DE VERIFICACIÓN (agregar)
app.include_router(verificacion.router)

# ============================================
# QR PÚBLICO
# ============================================
@app.get("/public/qr/{qr_uuid}")
async def servir_qr(
    qr_uuid: UUID,
    db=Depends(get_db)
):
    """Servir imagen QR del vehículo"""
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
        raise HTTPException(status_code=410, detail="QR inactivo o vehículo deshabilitado")
    
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
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await handle_websocket(websocket, user_id)


# ============================================
# Endpoints básicos
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