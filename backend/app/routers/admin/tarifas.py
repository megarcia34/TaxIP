"""
Router Admin para gestión de configuraciones de tarifa por tenant
CRUD completo para payment.configuracion_tarifa
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text

from app.database import get_db
from app.dependencies import (
    ControlBaseAdminUser,
    SuperAdminUser,
    AdminTenantUser,
)
from app.models.payment import ConfiguracionTarifa
from app.schemas.tarifa_schemas import (
    ConfiguracionTarifaCreate,
    ConfiguracionTarifaUpdate,
    ConfiguracionTarifaResponse,
)
from app.core.validations import validar_tenant_activo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/tarifas", tags=["Admin - Tarifas"])


# ============================================================
# 1. PRIMERO: ENDPOINTS ESPECÍFICOS
# ============================================================

@router.get("/mi-tenant", response_model=ConfiguracionTarifaResponse)
async def get_mi_tenant_tarifa(
    current_user: AdminTenantUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene la configuración de tarifa del tenant del usuario autenticado.
    ✅ Accesible para ADMIN TENANT.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if not control_base_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene un tenant asociado"
        )
    
    query = select(ConfiguracionTarifa).where(
        and_(
            ConfiguracionTarifa.control_base_id == control_base_id,
            ConfiguracionTarifa.activo == True
        )
    )
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró configuración activa para tu tenant"
        )
    
    tenant_query = text("SELECT nombre FROM tenant.control_base WHERE id = :id")
    tenant_result = await db.execute(tenant_query, {"id": control_base_id})
    tenant_row = tenant_result.first()
    tenant_nombre = tenant_row[0] if tenant_row else None
    
    return {
        **config.__dict__,
        "tenant_nombre": tenant_nombre
    }


# ============================================================
# 2. SEGUNDO: ENDPOINTS CON PARÁMETROS DINÁMICOS
# ============================================================

@router.get("/control-base/{control_base_id}", response_model=ConfiguracionTarifaResponse)
async def get_tarifa_by_tenant(
    control_base_id: UUID,
    current_user: ControlBaseAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene la configuración de tarifa de un tenant específico.
    ✅ Accesible para SUPER ADMIN y ADMIN TENANT (solo su propio tenant).
    """
    user_id, user_control_base_id, email, tipo = current_user
    
    await validar_tenant_activo(control_base_id, db)
    
    if tipo.lower() == "admin" and user_control_base_id is not None:
        if user_control_base_id != control_base_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver configuraciones de otros tenants"
            )
    
    query = select(ConfiguracionTarifa).where(
        and_(
            ConfiguracionTarifa.control_base_id == control_base_id,
            ConfiguracionTarifa.activo == True
        )
    )
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró configuración activa para el tenant {control_base_id}"
        )
    
    tenant_query = text("SELECT nombre FROM tenant.control_base WHERE id = :id")
    tenant_result = await db.execute(tenant_query, {"id": control_base_id})
    tenant_row = tenant_result.first()
    tenant_nombre = tenant_row[0] if tenant_row else None
    
    return {
        **config.__dict__,
        "tenant_nombre": tenant_nombre
    }


# ============================================================
# 3. TERCERO: ENDPOINTS CON ID
# ============================================================

@router.get("/{id}", response_model=ConfiguracionTarifaResponse)
async def get_tarifa_by_id(
    id: UUID,
    current_user: ControlBaseAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene una configuración de tarifa por su ID.
    ✅ Accesible para SUPER ADMIN y ADMIN TENANT (solo su propio tenant).
    """
    user_id, user_control_base_id, email, tipo = current_user
    
    query = select(ConfiguracionTarifa).where(ConfiguracionTarifa.id == id)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró configuración con ID {id}"
        )
    
    if tipo.lower() == "admin" and user_control_base_id is not None:
        if user_control_base_id != config.control_base_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver configuraciones de otros tenants"
            )
    
    tenant_query = text("SELECT nombre FROM tenant.control_base WHERE id = :id")
    tenant_result = await db.execute(tenant_query, {"id": config.control_base_id})
    tenant_row = tenant_result.first()
    tenant_nombre = tenant_row[0] if tenant_row else None
    
    return {
        **config.__dict__,
        "tenant_nombre": tenant_nombre
    }


# ============================================================
# LISTAR TODAS LAS CONFIGURACIONES (SUPER ADMIN)
# ============================================================

@router.get("", response_model=List[ConfiguracionTarifaResponse])
async def list_tarifas(
    current_user: SuperAdminUser,
    activo: Optional[bool] = Query(None, description="Filtrar por activo"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista todas las configuraciones de tarifa.
    ✅ Solo accesible para SUPER ADMIN.
    """
    query = select(ConfiguracionTarifa)
    
    if activo is not None:
        query = query.where(ConfiguracionTarifa.activo == activo)
    
    query = query.order_by(ConfiguracionTarifa.created_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    configs = result.scalars().all()
    
    response = []
    for config in configs:
        tenant_query = text("SELECT nombre FROM tenant.control_base WHERE id = :id")
        tenant_result = await db.execute(tenant_query, {"id": config.control_base_id})
        tenant_row = tenant_result.first()
        tenant_nombre = tenant_row[0] if tenant_row else None
        
        response.append({
            **config.__dict__,
            "tenant_nombre": tenant_nombre
        })
    
    return response


# ============================================================
# CREAR NUEVA CONFIGURACIÓN
# ============================================================

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ConfiguracionTarifaResponse)
async def create_tarifa(
    data: ConfiguracionTarifaCreate,
    current_user: ControlBaseAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una nueva configuración de tarifa para un tenant.
    ✅ Accesible para SUPER ADMIN y ADMIN TENANT (solo su propio tenant).
    """
    user_id, user_control_base_id, email, tipo = current_user
    
    if tipo.lower() == "admin" and user_control_base_id is not None:
        if user_control_base_id != data.control_base_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para crear configuraciones para otros tenants"
            )
    
    await validar_tenant_activo(data.control_base_id, db)
    
    if data.activo is not False:
        check_query = select(ConfiguracionTarifa).where(
            and_(
                ConfiguracionTarifa.control_base_id == data.control_base_id,
                ConfiguracionTarifa.activo == True
            )
        )
        result = await db.execute(check_query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El tenant ya tiene una configuración activa (ID: {existing.id})"
            )
    
    config = ConfiguracionTarifa(
        control_base_id=data.control_base_id,
        nombre=data.nombre,
        modo_calculo=data.modo_calculo or "por_km",
        tarifa_base=data.tarifa_base or 0,
        precio_por_km=data.precio_por_km or 0,
        precio_por_minuto=data.precio_por_minuto or 0,
        distancia_por_ficha=data.distancia_por_ficha or 100,
        precio_por_ficha=data.precio_por_ficha or 0,
        precio_por_minuto_espera=data.precio_por_minuto_espera or 0,
        recargo_nocturno=data.recargo_nocturno or 1.0,
        recargo_feriado=data.recargo_feriado or 1.0,
        recargo_domingo=data.recargo_domingo or 1.0,
        hora_inicio_nocturno=data.hora_inicio_nocturno or "22:00",
        hora_fin_nocturno=data.hora_fin_nocturno or "06:00",
        moneda=data.moneda or "ARS",
        descripcion=data.descripcion,
        activo=data.activo if data.activo is not None else True
    )
    
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    logger.info(f"✅ Configuración creada: {config.id}")
    
    return {
        **config.__dict__,
        "tenant_nombre": None
    }


# ============================================================
# ACTUALIZAR CONFIGURACIÓN
# ============================================================

@router.put("/{id}", response_model=ConfiguracionTarifaResponse)
async def update_tarifa(
    id: UUID,
    data: ConfiguracionTarifaUpdate,
    current_user: ControlBaseAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Actualiza una configuración de tarifa existente.
    """
    user_id, user_control_base_id, email, tipo = current_user
    
    query = select(ConfiguracionTarifa).where(ConfiguracionTarifa.id == id)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró configuración con ID {id}"
        )
    
    if tipo.lower() == "admin" and user_control_base_id is not None:
        if user_control_base_id != config.control_base_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar configuraciones de otros tenants"
            )
    
    if data.activo is True:
        await db.execute(
            text("""
                UPDATE payment.configuracion_tarifa
                SET activo = false
                WHERE control_base_id = :tenant_id AND id != :config_id
            """),
            {"tenant_id": config.control_base_id, "config_id": id}
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    config.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(config)
    
    logger.info(f"✅ Configuración actualizada: {config.id}")
    
    return {
        **config.__dict__,
        "tenant_nombre": None
    }


# ============================================================
# ELIMINAR (SOFT DELETE)
# ============================================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tarifa(
    id: UUID,
    current_user: ControlBaseAdminUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Elimina (soft delete) una configuración de tarifa.
    """
    user_id, user_control_base_id, email, tipo = current_user
    
    query = select(ConfiguracionTarifa).where(ConfiguracionTarifa.id == id)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró configuración con ID {id}"
        )
    
    if tipo.lower() == "admin" and user_control_base_id is not None:
        if user_control_base_id != config.control_base_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar configuraciones de otros tenants"
            )
    
    config.activo = False
    config.updated_at = datetime.now()
    
    await db.commit()
    
    logger.info(f"✅ Configuración eliminada (soft delete): {config.id}")