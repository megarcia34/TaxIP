"""
Router de planes de mantenimiento para propietario.

Endpoints:
- GET    /planes                       listar planes del propietario
- POST   /planes                       crear plan
- POST   /planes/{plan_id}/items       agregar item al plan
- POST   /planes/{plan_id}/asignar     asignar plan a vehiculo(s)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.dependencies import get_propietario_id, get_current_user
from app.models.fleet import (
    MantenimientoPlan,
    MantenimientoPlanItem,
    MantenimientoPlanVehiculo,
    MantenimientoCatalogoComponente,
    Vehiculo,
    PropietarioVehiculo,
)
from app.schemas.mantenimiento_schemas import (
    PlanCreate,
    PlanResponse,
    PlanItemCreate,
    PlanItemResponse,
    AsignarPlanRequest,
    AsignarPlanResponse,
)

router = APIRouter()


# ============================================================
# HELPERS
# ============================================================

async def _verificar_plan_propietario(
    db: AsyncSession, plan_id: UUID, propietario_id: UUID, control_base_id: UUID
) -> MantenimientoPlan:
    """Verifica que el plan existe y pertenece al propietario + tenant."""
    query = select(MantenimientoPlan).where(
        MantenimientoPlan.id == plan_id,
        MantenimientoPlan.propietario_id == propietario_id,
        MantenimientoPlan.control_base_id == control_base_id,
    )
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan no encontrado",
        )
    return plan


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("", response_model=dict)
async def listar_planes(
    vehiculo_id: Optional[UUID] = Query(None),
    tipo: Optional[str] = Query(None),
    activo: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los planes del propietario con filtros opcionales."""
    _, control_base_id, _, _ = current_user

    query = select(MantenimientoPlan).where(
        MantenimientoPlan.propietario_id == propietario_id,
        MantenimientoPlan.control_base_id == control_base_id,
    )

    if vehiculo_id:
        # Filtrar planes asignados a ese vehiculo
        subq = (
            select(MantenimientoPlanVehiculo.plan_id)
            .where(
                MantenimientoPlanVehiculo.vehiculo_id == vehiculo_id,
                MantenimientoPlanVehiculo.activo == True,
            )
        )
        query = query.where(MantenimientoPlan.id.in_(subq))

    if tipo:
        query = query.where(MantenimientoPlan.tipo == tipo)
    if activo is not None:
        query = query.where(MantenimientoPlan.activo == activo)

    query = query.order_by(desc(MantenimientoPlan.created_at)).limit(limit).offset(offset)
    result = await db.execute(query)
    planes = result.scalars().all()

    # Contar items y vehiculos por plan
    items = []
    for plan in planes:
        items_count = await db.scalar(
            select(func.count(MantenimientoPlanItem.id))
            .where(MantenimientoPlanItem.plan_id == plan.id)
        )
        vehiculos_count = await db.scalar(
            select(func.count(MantenimientoPlanVehiculo.id))
            .where(
                MantenimientoPlanVehiculo.plan_id == plan.id,
                MantenimientoPlanVehiculo.activo == True,
            )
        )
        items.append({
            "id": str(plan.id),
            "nombre": plan.nombre,
            "tipo": plan.tipo,
            "descripcion": plan.descripcion,
            "umbrales_override": plan.umbrales_override,
            "activo": plan.activo,
            "items_count": items_count or 0,
            "vehiculos_count": vehiculos_count or 0,
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
        })

    return {"total": len(items), "items": items}


@router.post("", response_model=PlanResponse, status_code=201)
async def crear_plan(
    data: PlanCreate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crea un nuevo plan de mantenimiento."""
    _, control_base_id, _, _ = current_user

    # Verificar nombre unico
    existente = await db.scalar(
        select(MantenimientoPlan.id).where(
            MantenimientoPlan.control_base_id == control_base_id,
            MantenimientoPlan.propietario_id == propietario_id,
            MantenimientoPlan.nombre == data.nombre,
        )
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un plan con nombre '{data.nombre}'",
        )

    plan = MantenimientoPlan(
        control_base_id=control_base_id,
        propietario_id=propietario_id,
        nombre=data.nombre,
        tipo=data.tipo,
        descripcion=data.descripcion,
        umbrales_override=data.umbrales_override,
        activo=True,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    return PlanResponse(
        id=plan.id,
        nombre=plan.nombre,
        tipo=plan.tipo,
        descripcion=plan.descripcion,
        umbrales_override=plan.umbrales_override,
        activo=plan.activo,
        items_count=0,
        vehiculos_count=0,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.post("/{plan_id}/items", response_model=PlanItemResponse, status_code=201)
async def agregar_item(
    plan_id: UUID,
    data: PlanItemCreate,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Agrega un item a un plan existente."""
    _, control_base_id, _, _ = current_user

    # Verificar plan
    await _verificar_plan_propietario(db, plan_id, propietario_id, control_base_id)

    # Verificar componente
    componente = await db.scalar(
        select(MantenimientoCatalogoComponente).where(
            MantenimientoCatalogoComponente.id == data.componente_id,
            MantenimientoCatalogoComponente.activo == True,
        )
    )
    if not componente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Componente no encontrado en el catalogo",
        )

    # Crear item
    item = MantenimientoPlanItem(
        control_base_id=control_base_id,
        plan_id=plan_id,
        componente_id=data.componente_id,
        control_id=data.control_id,
        intervalo_km=data.intervalo_km,
        intervalo_dias=data.intervalo_dias,
        intervalo_meses=data.intervalo_meses,
        prioridad=data.prioridad,
        criticidad=data.criticidad,
        obligatorio=data.obligatorio,
        instrucciones=data.instrucciones,
        umbrales_override=data.umbrales_override,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    return PlanItemResponse(
        id=item.id,
        plan_id=item.plan_id,
        componente_id=item.componente_id,
        componente_nombre=componente.nombre,
        control_id=item.control_id,
        intervalo_km=item.intervalo_km,
        intervalo_dias=item.intervalo_dias,
        intervalo_meses=item.intervalo_meses,
        prioridad=item.prioridad,
        criticidad=item.criticidad,
        obligatorio=item.obligatorio,
        instrucciones=item.instrucciones,
        created_at=item.created_at,
    )


@router.post("/{plan_id}/asignar", response_model=AsignarPlanResponse)
async def asignar_plan(
    plan_id: UUID,
    data: AsignarPlanRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Asigna un plan a uno o mas vehiculos del propietario."""
    _, control_base_id, _, _ = current_user

    # Verificar plan
    await _verificar_plan_propietario(db, plan_id, propietario_id, control_base_id)

    asignados = 0
    fallidos = 0
    errores = []

    for vehiculo_id in data.vehiculo_ids:
        try:
            # Verificar que el vehiculo pertenece al propietario
            vehiculo = await db.scalar(
                select(Vehiculo)
                .join(PropietarioVehiculo, PropietarioVehiculo.vehiculo_id == Vehiculo.id)
                .where(
                    Vehiculo.id == vehiculo_id,
                    PropietarioVehiculo.propietario_id == propietario_id,
                    PropietarioVehiculo.activo == True,
                )
            )
            if not vehiculo:
                fallidos += 1
                errores.append({
                    "vehiculo_id": str(vehiculo_id),
                    "error": "Vehiculo no encontrado o no pertenece al propietario",
                })
                continue

            # Verificar si ya esta asignado
            existente = await db.scalar(
                select(MantenimientoPlanVehiculo).where(
                    MantenimientoPlanVehiculo.control_base_id == control_base_id,
                    MantenimientoPlanVehiculo.plan_id == plan_id,
                    MantenimientoPlanVehiculo.vehiculo_id == vehiculo_id,
                )
            )
            if existente:
                if not existente.activo:
                    existente.activo = True
                    asignados += 1
                continue

            # Crear asignacion
            asignacion = MantenimientoPlanVehiculo(
                control_base_id=control_base_id,
                plan_id=plan_id,
                vehiculo_id=vehiculo_id,
                compatibilidad_override=data.compatibilidad_override,
                compatibilidad_override_motivo=data.compatibilidad_override_motivo,
                compatibilidad_override_autor_id=propietario_id if data.compatibilidad_override else None,
                compatibilidad_override_en=(
                    func.now() if data.compatibilidad_override else None
                ),
                activo=True,
            )
            db.add(asignacion)
            asignados += 1
        except Exception as e:
            fallidos += 1
            errores.append({"vehiculo_id": str(vehiculo_id), "error": str(e)})

    await db.commit()

    return AsignarPlanResponse(
        asignados=asignados,
        fallidos=fallidos,
        errores=errores,
    )