# app/routers/super_admin/__init__.py
"""
Super Admin - Módulo de administración de la plataforma
"""

from app.routers.super_admin.dashboard import router as dashboard_router
from app.routers.super_admin.tenants import router as tenants_router

# Exportar routers
__all__ = ["dashboard_router", "tenants_router"]