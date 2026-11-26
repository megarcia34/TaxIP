"""
Router de vencimientos de mantenimiento para propietario.

Endpoints:
- GET    /vencimientos                       listar vencimientos
- POST   /vencimientos/{vencimiento_id}/resolver   registrar service
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_propietario_id, get_current_user
from app.models.fleet import (
    MantenimientoVencimiento,
    MantenimientoPlanItem,
    MantenimientoCatalogoComponente,
    Vehiculo,
    PropietarioVehiculo,
)
from app.schemas.mantenimiento_schemas import (
    VencimientoResponse,
    VencimientoListResponse,
    ResolverVencimientoRequest,
)

router = APIRouter()


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("", response_model=VencimientoListResponse)
async def listar_vencimientos(
    vehiculo_id: Optional[UUID] = Query(None),
    estado: Optional[str] = Query(None, pattern="^(normal|proximo|critico|vencido)$"),
    solo_alertas: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista los vencimientos de mantenimiento de los vehiculos del propietario.
    """
    _, control_base_id, _, _ = current_user

    # Base query: vencimientos de vehiculos del propietario
    query = (
        select(MantenimientoVencimiento)
        .join(Vehiculo, Vehiculo.id == MantenimientoVencimiento.vehiculo_id)
        .join(
            PropietarioVehiculo,
            PropietarioVehiculo.vehiculo_id == Vehiculo.id,
        )
        .where(
            MantenimientoVencimiento.control_base_id == control_base_id,
            MantenimientoVencimiento.vigente == True,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True,
        )
    )

    if vehiculo_id:
        query = query.where(MantenimientoVencimiento.vehiculo_id == vehiculo_id)
    if estado:
        query = query.where(MantenimientoVencimiento.estado == estado)
    if solo_alertas:
        query = query.where(
            MantenimientoVencimiento.estado.in_(["proximo", "critico", "vencido"])
        )

    query = query.order_by(
        # Vencidos primero, despues criticos, proximos, normales
        desc(MantenimientoVencimiento.estado == "vencido"),
        desc(MantenimientoVencimiento.estado == "critico"),
        desc(MantenimientoVencimiento.estado == "proximo"),
        MantenimientoVencimiento.fecha_proximo.asc().nullslast(),
    ).limit(limit).offset(offset)

    result = await db.execute(query)
    vencimientos = result.scalars().all()

    # Enriquecer con datos del vehiculo y componente
    items = []
    for v in vencimientos:
        # Vehiculo
        vehiculo = await db.scalar(
            select(Vehiculo).where(Vehiculo.id == v.vehiculo_id)
        )
        # Plan item -> componente
        plan_item = await db.scalar(
            select(MantenimientoPlanItem).where(MantenimientoPlanItem.id == v.plan_item_id)
        )
        componente = None
        if plan_item:
            componente = await db.scalar(
                select(MantenimientoCatalogoComponente).where(
                    MantenimientoCatalogoComponente.id == plan_item.componente_id
                )
            )

        items.append(VencimientoResponse(
            id=v.id,
            vehiculo_id=v.vehiculo_id,
            vehiculo_patente=vehiculo.patente if vehiculo else "",
            plan_item_id=v.plan_item_id,
            componente_nombre=componente.nombre if componente else "",
            km_actual=float(v.km_actual) if v.km_actual else None,
            km_proximo=float(v.km_proximo) if v.km_proximo else None,
            fecha_proximo=v.fecha_proximo,
            estado=v.estado,
            vigente=v.vigente,
            calculado_en=v.calculado_en,
            advertencias=[],
        ))

    return VencimientoListResponse(total=len(items), items=items)


@router.post("/{vencimiento_id}/resolver", response_model=VencimientoResponse)
async def resolver_vencimiento(
    vencimiento_id: UUID,
    data: ResolverVencimientoRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Marca un vencimiento como resuelto (registra un service).

    En R28 se reemplaza por la creacion de una OT + intervencion.
    Por ahora: marca el vencimiento como vigente=false, crea uno nuevo con
    estado='normal', y actualiza el plan_item si aplica.
    """
    _, control_base_id, _, _ = current_user

    # Verificar vencimiento
    vencimiento = await db.scalar(
        select(MantenimientoVencimiento).where(
            MantenimientoVencimiento.id == vencimiento_id,
            MantenimientoVencimiento.control_base_id == control_base_id,
        )
    )
    if not vencimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vencimiento no encontrado",
        )

    # Verificar que el vehiculo pertenece al propietario
    vehiculo = await db.scalar(
        select(Vehiculo)
        .join(PropietarioVehiculo, PropietarioVehiculo.vehiculo_id == Vehiculo.id)
        .where(
            Vehiculo.id == vencimiento.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True,
        )
    )
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El vehiculo no pertenece al propietario",
        )

    if not vencimiento.vigente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vencimiento ya esta resuelto",
        )

    # Marcar como resuelto
    vencimiento.vigente = False
    vencimiento.estado = "normal"  # Resuelto

    # Crear nuevo vencimiento (proximo calculo)
    # En R28 se hara via MantenimientoEngine con la OT
    plan_item = await db.scalar(
        select(MantenimientoPlanItem).where(
            MantenimientoPlanItem.id == vencimiento.plan_item_id
        )
    )

    nuevo_vencimiento = None
    if plan_item:
        from datetime import timedelta
        nuevo_km_proximo = None
        nuevo_fecha_proximo = None

        if plan_item.intervalo_km:
            nuevo_km_proximo = data.km_al_resolver + plan_item.intervalo_km
        if plan_item.intervalo_dias:
            nuevo_fecha_proximo = data.fecha_resolucion + timedelta(days=plan_item.intervalo_dias)
        elif plan_item.intervalo_meses:
            # Sumar meses (aproximado)
            import calendar
            anio = data.fecha_resolucion.year
            mes = data.fecha_resolucion.month + plan_item.intervalo_meses
            while mes > 12:
                mes -= 12
                anio += 1
            dia = min(data.fecha_resolucion.day, calendar.monthrange(anio, mes)[1])
            from datetime import date as date_cls
            nuevo_fecha_proximo = date_cls(anio, mes, dia)

        nuevo_vencimiento = MantenimientoVencimiento(
            control_base_id=control_base_id,
            vehiculo_id=vencimiento.vehiculo_id,
            plan_item_id=vencimiento.plan_item_id,
            km_actual=data.km_al_resolver,
            km_proximo=nuevo_km_proximo,
            fecha_proximo=nuevo_fecha_proximo,
            estado="normal",
            vigente=True,
        )
        db.add(nuevo_vencimiento)

    await db.commit()

    return VencimientoResponse(
        id=vencimiento.id,
        vehiculo_id=vencimiento.vehiculo_id,
        vehiculo_patente=vehiculo.patente,
        plan_item_id=vencimiento.plan_item_id,
        componente_nombre="",
        km_actual=float(vencimiento.km_actual) if vencimiento.km_actual else None,
        km_proximo=float(vencimiento.km_proximo) if vencimiento.km_proximo else None,
        fecha_proximo=vencimiento.fecha_proximo,
        estado=vencimiento.estado,
        vigente=vencimiento.vigente,
        calculado_en=vencimiento.calculado_en,
        advertencias=["Vencimiento resuelto. Proximo calculado."],
    )