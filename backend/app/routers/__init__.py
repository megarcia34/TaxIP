"""
Routers package
"""
from app.routers import auth
from app.routers import choferes
from app.routers import chofer_registro
from app.routers import chofer_documentos
from app.routers import control_base
from app.routers import pagos
from app.routers import usuarios
from app.routers import vehiculo
from app.routers import vehiculos
from app.routers import viajes
from app.routers import catalogo
from app.routers import comercio
from app.routers import empresa
from app.routers.propietario import router as propietario_router
from app.routers.public import qr as public_qr_router
from .choferes_public import router as choferes_public_router

# ✅ Importar public_router de viajes
from app.routers.viajes import public_router as public_viajes_router

# Importar routers de admin
from .admin import propietarios_router, empresas_router

# Importar router de empresa dashboard
from .empresa_dashboard import router as empresa_dashboard_router

# ============================================
# LISTA DE ROUTERS A EXPORTAR Y REGISTRAR
# ============================================
__all__ = [
    "auth",
    "choferes",
    "chofer_registro",
    "chofer_documentos",
    "control_base",
    "pagos",
    "usuarios",
    "vehiculo",
    "vehiculos",
    "viajes",
    "catalogo",
    "comercio",
    "empresa",
    "propietario_router",
    "public_qr_router",
    "propietarios_router",
    "empresas_router",
    "empresa_dashboard_router",
    "choferes_public_router",
    "public_viajes_router",  # ✅ AGREGADO
]

# ============================================
# LISTA DE ROUTERS PARA REGISTRAR EN main.py
# ============================================
routers = [
    auth.router,
    usuarios.router,
    choferes.router,
    chofer_registro.router,
    chofer_documentos.router,
    viajes.router,              # /api/viajes
    public_viajes_router,       # ✅ AGREGADO - /api/public/viajes
    control_base.router,
    pagos.router,
    vehiculo.router,
    vehiculos.router,
    empresa.router,
    comercio.router,
    catalogo.router,
    propietario_router,
    public_qr_router,
    propietarios_router,
    empresas_router,
    empresa_dashboard_router,
    choferes_public_router,
]