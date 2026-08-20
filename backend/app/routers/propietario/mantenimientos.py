"""
Mantenimiento del propietario - Fase 6
CRUD completo con alertas, destinatario dinámico y subida de comprobantes
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timedelta, date

from app.database import get_db
from app.dependencies import get_current_user, get_propietario_id
from app.models.fleet import (
    MantenimientoVehiculo,
    Vehiculo,
    PropietarioVehiculo,
    ContratoVehiculo
)
from app.models.auth import Usuario
from app.models.turno import TurnoChofer
from app.schemas.propietario_schemas import (
    MantenimientoVehiculoRequest,
    MantenimientoVehiculoResponse,
    MantenimientoProximoResponse,
    MantenimientoAlertasResponse,
)
from app.services.cloudinary_storage import cloudinary_storage

router = APIRouter()

# ============================================================
# CONFIGURACIÓN DE MANTENIMIENTOS
# ============================================================

PERIODICIDAD_MANTENIMIENTO = {
    "SERVICE_MENOR": {"km": 5000, "dias": 90, "alerta_a": "chofer"},
    "SERVICE_MAYOR": {"km": 20000, "dias": 365, "alerta_a": "dueno"},
    "NEUMATICOS": {"km": 10000, "dias": None, "alerta_a": "chofer"},
    "FRENOS": {"km": 15000, "dias": None, "alerta_a": "chofer"},
    "DISTRIBUCION": {"km": 60000, "dias": None, "alerta_a": "dueno"},
    "ALINEACION": {"km": 10000, "dias": 180, "alerta_a": "chofer"},
    "CAMBIO_ACEITE": {"km": 5000, "dias": 180, "alerta_a": "chofer"},
    "LUBRICACION": {"km": 5000, "dias": 180, "alerta_a": "chofer"},
    "ELECTRICO": {"km": None, "dias": 365, "alerta_a": "dueno"},
    "GENERAL": {"km": 10000, "dias": 180, "alerta_a": "chofer"},
}

TIPO_MANTENIMIENTO_VALIDOS = list(PERIODICIDAD_MANTENIMIENTO.keys())


# ============================================================
# CRUD DE MANTENIMIENTOS
# ============================================================

@router.post("/mantenimiento", response_model=MantenimientoVehiculoResponse)
async def registrar_mantenimiento(
    request_data: MantenimientoVehiculoRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar un mantenimiento de vehículo.
    """
    # 1. Validar tipo de servicio
    if request_data.tipo_servicio not in TIPO_MANTENIMIENTO_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de servicio inválido. Permitidos: {TIPO_MANTENIMIENTO_VALIDOS}"
        )

    # 2. Verificar que el vehículo pertenece al propietario
    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == request_data.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Vehículo no pertenece al propietario"
        )

    # 3. Crear mantenimiento
    mantenimiento = MantenimientoVehiculo(
        vehiculo_id=request_data.vehiculo_id,
        propietario_id=propietario_id,
        tipo_servicio=request_data.tipo_servicio,
        taller_nombre=request_data.taller_nombre,
        taller_direccion=request_data.taller_direccion,
        costo=request_data.costo,
        kilometraje=request_data.kilometraje,
        observaciones=request_data.observaciones,
        fecha_servicio=request_data.fecha_servicio
    )

    db.add(mantenimiento)
    await db.commit()
    await db.refresh(mantenimiento)

    # Obtener patente del vehículo
    vehiculo = await db.get(Vehiculo, request_data.vehiculo_id)

    return MantenimientoVehiculoResponse(
        id=mantenimiento.id,
        vehiculo_id=mantenimiento.vehiculo_id,
        vehiculo_patente=vehiculo.patente if vehiculo else "",
        tipo_servicio=mantenimiento.tipo_servicio,
        taller_nombre=mantenimiento.taller_nombre,
        taller_direccion=mantenimiento.taller_direccion,
        costo=float(mantenimiento.costo) if mantenimiento.costo else None,
        kilometraje=mantenimiento.kilometraje,
        observaciones=mantenimiento.observaciones,
        fecha_servicio=mantenimiento.fecha_servicio,
        created_at=mantenimiento.created_at
    )


@router.get("/mantenimientos", response_model=List[MantenimientoVehiculoResponse])
async def listar_mantenimientos(
    vehiculo_id: Optional[UUID] = None,
    tipo_servicio: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar mantenimientos del propietario con filtros.
    """
    query = select(MantenimientoVehiculo).options(
        selectinload(MantenimientoVehiculo.vehiculo)
    ).where(MantenimientoVehiculo.propietario_id == propietario_id)

    if vehiculo_id:
        query = query.where(MantenimientoVehiculo.vehiculo_id == vehiculo_id)
    if tipo_servicio:
        query = query.where(MantenimientoVehiculo.tipo_servicio == tipo_servicio)
    if desde:
        query = query.where(MantenimientoVehiculo.fecha_servicio >= desde)
    if hasta:
        query = query.where(MantenimientoVehiculo.fecha_servicio <= hasta)

    query = query.order_by(desc(MantenimientoVehiculo.fecha_servicio))
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    mantenimientos = result.scalars().all()

    return [
        MantenimientoVehiculoResponse(
            id=m.id,
            vehiculo_id=m.vehiculo_id,
            vehiculo_patente=m.vehiculo.patente if m.vehiculo else "",
            tipo_servicio=m.tipo_servicio,
            taller_nombre=m.taller_nombre,
            taller_direccion=m.taller_direccion,
            costo=float(m.costo) if m.costo else None,
            kilometraje=m.kilometraje,
            observaciones=m.observaciones,
            fecha_servicio=m.fecha_servicio,
            created_at=m.created_at
        )
        for m in mantenimientos
    ]


@router.get("/mantenimiento/{mantenimiento_id}", response_model=MantenimientoVehiculoResponse)
async def obtener_mantenimiento(
    mantenimiento_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un mantenimiento específico.
    """
    mantenimiento = await db.get(MantenimientoVehiculo, mantenimiento_id)
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    if mantenimiento.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este mantenimiento")

    await db.refresh(mantenimiento, attribute_names=["vehiculo"])

    return MantenimientoVehiculoResponse(
        id=mantenimiento.id,
        vehiculo_id=mantenimiento.vehiculo_id,
        vehiculo_patente=mantenimiento.vehiculo.patente if mantenimiento.vehiculo else "",
        tipo_servicio=mantenimiento.tipo_servicio,
        taller_nombre=mantenimiento.taller_nombre,
        taller_direccion=mantenimiento.taller_direccion,
        costo=float(mantenimiento.costo) if mantenimiento.costo else None,
        kilometraje=mantenimiento.kilometraje,
        observaciones=mantenimiento.observaciones,
        fecha_servicio=mantenimiento.fecha_servicio,
        created_at=mantenimiento.created_at
    )


@router.put("/mantenimiento/{mantenimiento_id}", response_model=MantenimientoVehiculoResponse)
async def actualizar_mantenimiento(
    mantenimiento_id: UUID,
    request_data: MantenimientoVehiculoRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar un mantenimiento existente.
    """
    mantenimiento = await db.get(MantenimientoVehiculo, mantenimiento_id)
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    if mantenimiento.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este mantenimiento")

    # Validar tipo de servicio
    if request_data.tipo_servicio not in TIPO_MANTENIMIENTO_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de servicio inválido. Permitidos: {TIPO_MANTENIMIENTO_VALIDOS}"
        )

    # Actualizar campos
    mantenimiento.tipo_servicio = request_data.tipo_servicio
    mantenimiento.taller_nombre = request_data.taller_nombre
    mantenimiento.taller_direccion = request_data.taller_direccion
    mantenimiento.costo = request_data.costo
    mantenimiento.kilometraje = request_data.kilometraje
    mantenimiento.observaciones = request_data.observaciones
    mantenimiento.fecha_servicio = request_data.fecha_servicio

    await db.commit()
    await db.refresh(mantenimiento)
    await db.refresh(mantenimiento, attribute_names=["vehiculo"])

    return MantenimientoVehiculoResponse(
        id=mantenimiento.id,
        vehiculo_id=mantenimiento.vehiculo_id,
        vehiculo_patente=mantenimiento.vehiculo.patente if mantenimiento.vehiculo else "",
        tipo_servicio=mantenimiento.tipo_servicio,
        taller_nombre=mantenimiento.taller_nombre,
        taller_direccion=mantenimiento.taller_direccion,
        costo=float(mantenimiento.costo) if mantenimiento.costo else None,
        kilometraje=mantenimiento.kilometraje,
        observaciones=mantenimiento.observaciones,
        fecha_servicio=mantenimiento.fecha_servicio,
        created_at=mantenimiento.created_at
    )


@router.delete("/mantenimiento/{mantenimiento_id}")
async def eliminar_mantenimiento(
    mantenimiento_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un mantenimiento.
    """
    mantenimiento = await db.get(MantenimientoVehiculo, mantenimiento_id)
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    if mantenimiento.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este mantenimiento")

    await db.delete(mantenimiento)
    await db.commit()

    return {"success": True, "message": "Mantenimiento eliminado correctamente"}


# ============================================================
# SUBIR COMPROBANTES A CLOUDINARY
# ============================================================

@router.post("/mantenimiento/{mantenimiento_id}/comprobante")
async def subir_comprobante_mantenimiento(
    mantenimiento_id: UUID,
    file: UploadFile = File(...),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir un comprobante (PDF, imagen) a Cloudinary para un mantenimiento.
    """
    mantenimiento = await db.get(MantenimientoVehiculo, mantenimiento_id)
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    if mantenimiento.propietario_id != propietario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este mantenimiento")

    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Use JPG, PNG o PDF"
        )

    try:
        # Usar el servicio de Cloudinary (reutilizamos el mismo que para gastos)
        from app.services.cloudinary_storage import cloudinary_storage
        
        url = await cloudinary_storage.upload_comprobante(
            file=file,
            propietario_id=str(propietario_id),
            gasto_id=str(mantenimiento_id),
            tipo="mantenimiento"
        )
        
        # Nota: El modelo MantenimientoVehiculo no tiene campo comprobante_url
        # Podemos agregarlo en una migración futura o almacenarlo en observaciones
        mantenimiento.observaciones = f"{mantenimiento.observaciones or ''}\nComprobante: {url}"
        await db.commit()
        
        return {
            "success": True,
            "message": "Comprobante subido correctamente",
            "url": url
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir el comprobante: {str(e)}"
        )


# ============================================================
# CÁLCULO DE PRÓXIMO MANTENIMIENTO
# ============================================================

@router.get("/mantenimientos/proximo")
async def calcular_proximo_mantenimiento(
    vehiculo_id: UUID,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcula el próximo mantenimiento programado para un vehículo.
    Incluye destinatario dinámico (chofer o dueño según contrato activo).
    """
    # 1. Verificar que el vehículo pertenece al propietario
    prop_vehiculo = await db.execute(
        select(PropietarioVehiculo).where(
            PropietarioVehiculo.vehiculo_id == vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True
        )
    )
    if not prop_vehiculo.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Vehículo no pertenece al propietario"
        )

    # 2. Obtener vehículo y km actual (desde turno activo o último)
    vehiculo = await db.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    km_actual = await _obtener_km_actual(db, vehiculo_id)

    # 3. Obtener último mantenimiento
    ultimo = await _obtener_ultimo_mantenimiento(db, vehiculo_id)

    # 4. Obtener contrato activo para determinar destinatario
    contrato_activo = await _obtener_contrato_activo(db, vehiculo_id)

    # 5. Calcular próximos mantenimientos
    proximos = _calcular_proximos_mantenimientos(ultimo, km_actual, contrato_activo)

    return {
        "vehiculo_id": str(vehiculo_id),
        "patente": vehiculo.patente,
        "km_actual": km_actual,
        "contrato_activo": {
            "chofer_id": str(contrato_activo.chofer_id) if contrato_activo else None,
            "tipo_contrato": contrato_activo.tipo_contrato if contrato_activo else None,
            "turno_asignado": contrato_activo.turno_asignado if contrato_activo else None,
        } if contrato_activo else None,
        "mantenimientos_proximos": proximos[:5]
    }


@router.get("/mantenimientos/alertas", response_model=MantenimientoAlertasResponse)
async def obtener_alertas_mantenimiento(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener todas las alertas de mantenimiento activas.
    """
    # 1. Obtener todos los vehículos del propietario
    query = select(Vehiculo).join(
        PropietarioVehiculo,
        PropietarioVehiculo.vehiculo_id == Vehiculo.id
    ).where(
        PropietarioVehiculo.propietario_id == propietario_id,
        PropietarioVehiculo.activo == True,
        Vehiculo.activo == True
    )
    result = await db.execute(query)
    vehiculos = result.scalars().all()

    todas_alertas = []
    for vehiculo in vehiculos:
        km_actual = await _obtener_km_actual(db, vehiculo.id)
        ultimo = await _obtener_ultimo_mantenimiento(db, vehiculo.id)
        contrato_activo = await _obtener_contrato_activo(db, vehiculo.id)
        
        proximos = _calcular_proximos_mantenimientos(ultimo, km_actual, contrato_activo)
        
        # Filtrar solo alertas (km_restante <= 1000 o dias_restantes <= 15)
        alertas = [
            p for p in proximos 
            if (p["km_restante"] is not None and p["km_restante"] <= 1000) or
               (p["dias_restantes"] is not None and p["dias_restantes"] <= 15)
        ]
        
        if alertas:
            todas_alertas.append({
                "vehiculo_id": str(vehiculo.id),
                "patente": vehiculo.patente,
                "alertas": alertas
            })

    return MantenimientoAlertasResponse(
        total_alertas=sum(len(v["alertas"]) for v in todas_alertas),
        vehiculos_con_alertas=todas_alertas
    )


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

async def _obtener_km_actual(db: AsyncSession, vehiculo_id: UUID) -> int:
    """Obtiene el kilometraje actual del vehículo desde el último turno."""
    query = select(TurnoChofer).where(
        TurnoChofer.vehiculo_id == vehiculo_id,
        TurnoChofer.estado.in_(['ACTIVO', 'PENDIENTE_CONFIRMACION'])
    ).order_by(desc(TurnoChofer.inicio_turno)).limit(1)
    
    result = await db.execute(query)
    turno = result.scalar_one_or_none()
    
    if turno:
        # Si el turno está activo, usar km_inicial (no tenemos km_final aún)
        # Si está cerrado, usar km_final
        if turno.estado == 'ACTIVO':
            return int(turno.km_inicial) if turno.km_inicial else 0
        else:
            return int(turno.km_final) if turno.km_final else int(turno.km_inicial) if turno.km_inicial else 0
    
    # Si no hay turno, obtener del último mantenimiento
    query_mant = select(MantenimientoVehiculo).where(
        MantenimientoVehiculo.vehiculo_id == vehiculo_id
    ).order_by(desc(MantenimientoVehiculo.fecha_servicio)).limit(1)
    
    result = await db.execute(query_mant)
    ultimo_mant = result.scalar_one_or_none()
    
    return ultimo_mant.kilometraje if ultimo_mant and ultimo_mant.kilometraje else 0


async def _obtener_ultimo_mantenimiento(db: AsyncSession, vehiculo_id: UUID):
    """Obtiene el último mantenimiento registrado para un vehículo."""
    query = select(MantenimientoVehiculo).where(
        MantenimientoVehiculo.vehiculo_id == vehiculo_id
    ).order_by(desc(MantenimientoVehiculo.fecha_servicio)).limit(1)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def _obtener_contrato_activo(db: AsyncSession, vehiculo_id: UUID):
    """Obtiene el contrato activo para un vehículo."""
    query = select(ContratoVehiculo).where(
        ContratoVehiculo.vehiculo_id == vehiculo_id,
        ContratoVehiculo.estado_contrato == 'ACTIVO',
        ContratoVehiculo.activo == True
    ).order_by(desc(ContratoVehiculo.fecha_inicio)).limit(1)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


def _calcular_proximos_mantenimientos(ultimo, km_actual: int, contrato_activo) -> List[dict]:
    """
    Calcula los próximos mantenimientos basados en la periodicidad.
    Determina el destinatario (chofer o dueño) según el contrato activo.
    """
    proximos = []
    
    for tipo, config in PERIODICIDAD_MANTENIMIENTO.items():
        km_base = ultimo.kilometraje if ultimo else 0
        fecha_base = ultimo.fecha_servicio if ultimo else datetime.now().date()
        
        # Calcular km restante
        if config.get("km"):
            km_proximo = km_base + config["km"]
            km_restante = max(0, km_proximo - km_actual)
        else:
            km_restante = None
        
        # Calcular días restantes
        if config.get("dias"):
            fecha_proximo = fecha_base + timedelta(days=config["dias"])
            dias_restantes = max(0, (fecha_proximo - datetime.now().date()).days)
        else:
            dias_restantes = None
        
        # Determinar destinatario
        alerta_a = config["alerta_a"]
        # Si el contrato es AUTO_GESTION, el dueño es el chofer
        if contrato_activo and contrato_activo.tipo_contrato == "AUTO_GESTION":
            alerta_a = "dueno"
        
        # Si no hay contrato activo, alertar al dueño
        if not contrato_activo:
            alerta_a = "dueno"
        
        # Determinar urgencia
        urgencia = "media"
        if (km_restante is not None and km_restante <= 500) or (dias_restantes is not None and dias_restantes <= 7):
            urgencia = "alta"
        elif (km_restante is not None and km_restante <= 1000) or (dias_restantes is not None and dias_restantes <= 15):
            urgencia = "media"
        
        proximos.append({
            "tipo_servicio": tipo,
            "tipo_nombre": tipo.replace("_", " ").title(),
            "km_restante": km_restante,
            "dias_restantes": dias_restantes,
            "alerta_a": alerta_a,
            "urgencia": urgencia
        })
    
    # Ordenar por urgencia (alta primero)
    proximos.sort(key=lambda x: 0 if x["urgencia"] == "alta" else 1)
    
    return proximos


# ============================================================
# WEBHOOK PARA ALERTAS CRÍTICAS (WebSocket)
# ============================================================

@router.post("/mantenimientos/alertas/notificar")
async def notificar_alertas_criticas(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para disparar notificaciones de alertas críticas.
    Las alertas se envían por WebSocket al destinatario correspondiente.
    """
    from app.websocket.connection_manager import manager
    
    # Obtener alertas
    alertas_response = await obtener_alertas_mantenimiento(
        propietario_id=propietario_id,
        current_user=current_user,
        db=db
    )
    
    notificaciones = []
    
    for vehiculo in alertas_response.vehiculos_con_alertas:
        for alerta in vehiculo["alertas"]:
            if alerta["urgencia"] == "alta":
                # Determinar destinatario
                destinatario_id = None
                if alerta["alerta_a"] == "chofer":
                    # Obtener chofer del contrato activo
                    contrato = await _obtener_contrato_activo(db, UUID(vehiculo["vehiculo_id"]))
                    if contrato:
                        destinatario_id = contrato.chofer_id
                else:
                    destinatario_id = propietario_id
                
                if destinatario_id:
                    # Enviar notificación por WebSocket
                    await manager.send_personal_message(
                        message={
                            "tipo": "alerta_mantenimiento",
                            "vehiculo": vehiculo["patente"],
                            "tipo_servicio": alerta["tipo_servicio"],
                            "urgencia": alerta["urgencia"],
                            "km_restante": alerta["km_restante"],
                            "dias_restantes": alerta["dias_restantes"],
                        },
                        user_id=str(destinatario_id)
                    )
                    notificaciones.append({
                        "destinatario_id": str(destinatario_id),
                        "vehiculo": vehiculo["patente"],
                        "tipo_servicio": alerta["tipo_servicio"]
                    })
    
    return {
        "success": True,
        "notificaciones_enviadas": len(notificaciones),
        "detalles": notificaciones
    }