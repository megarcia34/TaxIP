"""
Mantenimientos de vehiculos - Historial y alertas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func, text
from uuid import UUID
from typing import Optional, List
from datetime import datetime, date, timedelta

from app.database import get_db
from app.dependencies import get_propietario_id, get_current_user
from app.models.fleet import (
    MantenimientoVehiculo,
    Vehiculo,
    PropietarioVehiculo,
    ContratoVehiculo,
)
from app.models.turno import TurnoChofer
from app.schemas.propietario_schemas import (
    MantenimientoVehiculoRequest,
    MantenimientoVehiculoResponse,
    MantenimientoProximoResponse,
    MantenimientoAlertasResponse,
)

router = APIRouter()


# ============================================================
# PERIODICIDAD DE MANTENIMIENTOS
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
# LISTAR MANTENIMIENTOS
# ============================================================

@router.get("/mantenimientos", response_model=List[MantenimientoVehiculoResponse])
async def listar_mantenimientos(
    vehiculo_id: Optional[UUID] = Query(None),
    tipo_servicio: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los mantenimientos del propietario, con filtros opcionales."""
    query = (
        select(MantenimientoVehiculo)
        .join(Vehiculo, Vehiculo.id == MantenimientoVehiculo.vehiculo_id)
        .join(
            PropietarioVehiculo,
            PropietarioVehiculo.vehiculo_id == Vehiculo.id,
        )
        .where(
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True,
        )
    )

    if vehiculo_id:
        query = query.where(MantenimientoVehiculo.vehiculo_id == vehiculo_id)
    if tipo_servicio:
        query = query.where(MantenimientoVehiculo.tipo_servicio == tipo_servicio)

    query = query.order_by(desc(MantenimientoVehiculo.fecha_servicio)).limit(limit).offset(offset)

    result = await db.execute(query)
    mantenimientos = result.scalars().all()

    vehiculo_ids = list({m.vehiculo_id for m in mantenimientos})
    patentes = {}
    if vehiculo_ids:
        q_patentes = select(Vehiculo.id, Vehiculo.patente).where(Vehiculo.id.in_(vehiculo_ids))
        r_patentes = await db.execute(q_patentes)
        patentes = {row[0]: row[1] for row in r_patentes.all()}

    return [
        MantenimientoVehiculoResponse(
            id=m.id,
            vehiculo_id=m.vehiculo_id,
            vehiculo_patente=patentes.get(m.vehiculo_id, ""),
            tipo_servicio=m.tipo_servicio,
            taller_nombre=m.taller_nombre,
            taller_direccion=m.taller_direccion,
            costo=float(m.costo) if m.costo is not None else None,
            kilometraje=m.kilometraje,
            observaciones=m.observaciones,
            fecha_servicio=m.fecha_servicio,
            created_at=m.created_at,
        )
        for m in mantenimientos
    ]


# ============================================================
# CREAR MANTENIMIENTO
# ============================================================

@router.post("/mantenimiento", response_model=MantenimientoVehiculoResponse, status_code=201)
async def crear_mantenimiento(
    data: MantenimientoVehiculoRequest,
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra un nuevo mantenimiento para un vehiculo del propietario."""
    q_vehiculo = (
        select(Vehiculo)
        .join(PropietarioVehiculo, PropietarioVehiculo.vehiculo_id == Vehiculo.id)
        .where(
            Vehiculo.id == data.vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True,
        )
    )
    r_vehiculo = await db.execute(q_vehiculo)
    vehiculo = r_vehiculo.scalar_one_or_none()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

    if data.tipo_servicio not in TIPO_MANTENIMIENTO_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de servicio invalido. Permitidos: {TIPO_MANTENIMIENTO_VALIDOS}",
        )

    mantenimiento = MantenimientoVehiculo(
        vehiculo_id=data.vehiculo_id,
        tipo_servicio=data.tipo_servicio,
        taller_nombre=data.taller_nombre,
        taller_direccion=data.taller_direccion,
        costo=data.costo,
        kilometraje=data.kilometraje,
        observaciones=data.observaciones,
        fecha_servicio=data.fecha_servicio,
    )
    db.add(mantenimiento)
    await db.commit()
    await db.refresh(mantenimiento)

    return MantenimientoVehiculoResponse(
        id=mantenimiento.id,
        vehiculo_id=mantenimiento.vehiculo_id,
        vehiculo_patente=vehiculo.patente,
        tipo_servicio=mantenimiento.tipo_servicio,
        taller_nombre=mantenimiento.taller_nombre,
        taller_direccion=mantenimiento.taller_direccion,
        costo=float(mantenimiento.costo) if mantenimiento.costo is not None else None,
        kilometraje=mantenimiento.kilometraje,
        observaciones=mantenimiento.observaciones,
        fecha_servicio=mantenimiento.fecha_servicio,
        created_at=mantenimiento.created_at,
    )


# ============================================================
# PROXIMO MANTENIMIENTO (POR VEHICULO)
# ============================================================

@router.get("/mantenimientos/proximo", response_model=List[MantenimientoProximoResponse])
async def proximo_mantenimiento(
    vehiculo_id: UUID = Query(...),
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calcula el proximo mantenimiento para un vehiculo especifico."""
    q_vehiculo = (
        select(Vehiculo)
        .join(PropietarioVehiculo, PropietarioVehiculo.vehiculo_id == Vehiculo.id)
        .where(
            Vehiculo.id == vehiculo_id,
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True,
        )
    )
    r_vehiculo = await db.execute(q_vehiculo)
    vehiculo = r_vehiculo.scalar_one_or_none()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")

    km_actual = await _obtener_km_actual(db, vehiculo_id)
    ultimos_por_tipo = await _obtener_ultimos_mantenimientos_por_tipo(db, vehiculo_id)
    contrato_activo = await _obtener_contrato_activo(db, vehiculo_id)

    proximos = _calcular_proximos_mantenimientos(ultimos_por_tipo, km_actual, contrato_activo)

    return [
        MantenimientoProximoResponse(
            tipo_servicio=p["tipo_servicio"],
            tipo_nombre=p["tipo_nombre"],
            km_restante=p["km_restante"],
            dias_restantes=p["dias_restantes"],
            alerta_a=p["alerta_a"],
            urgencia=p["urgencia"],
        )
        for p in proximos
    ]


# ============================================================
# ALERTAS DE MANTENIMIENTO
# ============================================================

@router.get("/mantenimientos/alertas", response_model=MantenimientoAlertasResponse)
async def obtener_alertas_mantenimiento(
    propietario_id: UUID = Depends(get_propietario_id),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener todas las alertas de mantenimiento activas.
    """
    query = (
        select(Vehiculo)
        .join(PropietarioVehiculo, PropietarioVehiculo.vehiculo_id == Vehiculo.id)
        .where(
            PropietarioVehiculo.propietario_id == propietario_id,
            PropietarioVehiculo.activo == True,
            Vehiculo.activo == True,
        )
    )
    result = await db.execute(query)
    vehiculos = result.scalars().all()

    todas_alertas = []
    for vehiculo in vehiculos:
        km_actual = await _obtener_km_actual(db, vehiculo.id)
        ultimos_por_tipo = await _obtener_ultimos_mantenimientos_por_tipo(db, vehiculo.id)
        contrato_activo = await _obtener_contrato_activo(db, vehiculo.id)

        proximos = _calcular_proximos_mantenimientos(ultimos_por_tipo, km_actual, contrato_activo)

        # Filtrar solo alertas:
        # - vencidos (km_restante < 0 o dias_restantes < 0)
        # - proximos (km_restante <= 1000 o dias_restantes <= 15)
        alertas = [
            p
            for p in proximos
            if (p["km_restante"] is not None and p["km_restante"] <= 1000)
            or (p["dias_restantes"] is not None and p["dias_restantes"] <= 15)
        ]

        if alertas:
            todas_alertas.append(
                {
                    "vehiculo_id": str(vehiculo.id),
                    "patente": vehiculo.patente,
                    "km_actual": int(km_actual) if km_actual is not None else 0,
                    "mantenimientos_proximos": alertas,
                }
            )

    return MantenimientoAlertasResponse(
        total_alertas=sum(len(v["mantenimientos_proximos"]) for v in todas_alertas),
        vehiculos_con_alertas=todas_alertas,
    )


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

async def _obtener_km_actual(db: AsyncSession, vehiculo_id: UUID) -> int:
    """Obtiene el kilometraje actual del vehiculo desde el ultimo turno."""
    query = (
        select(TurnoChofer)
        .where(
            TurnoChofer.vehiculo_id == vehiculo_id,
            TurnoChofer.estado.in_(["ACTIVO", "PENDIENTE_CONFIRMACION"]),
        )
        .order_by(desc(TurnoChofer.inicio_turno))
        .limit(1)
    )

    result = await db.execute(query)
    turno = result.scalar_one_or_none()

    if turno:
        if turno.estado == "ACTIVO":
            return int(turno.km_inicial) if turno.km_inicial else 0
        else:
            return (
                int(turno.km_final)
                if turno.km_final
                else int(turno.km_inicial)
                if turno.km_inicial
                else 0
            )

    # Si no hay turno, obtener del ultimo mantenimiento
    query_mant = (
        select(MantenimientoVehiculo)
        .where(MantenimientoVehiculo.vehiculo_id == vehiculo_id)
        .order_by(desc(MantenimientoVehiculo.fecha_servicio))
        .limit(1)
    )

    result = await db.execute(query_mant)
    ultimo_mant = result.scalar_one_or_none()

    return ultimo_mant.kilometraje if ultimo_mant and ultimo_mant.kilometraje else 0


async def _obtener_ultimo_mantenimiento(db: AsyncSession, vehiculo_id: UUID):
    """Obtiene el ultimo mantenimiento registrado (cualquier tipo)."""
    query = (
        select(MantenimientoVehiculo)
        .where(MantenimientoVehiculo.vehiculo_id == vehiculo_id)
        .order_by(desc(MantenimientoVehiculo.fecha_servicio))
        .limit(1)
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def _obtener_ultimos_mantenimientos_por_tipo(
    db: AsyncSession, vehiculo_id: UUID
) -> dict:
    """
    Obtiene el ultimo mantenimiento de CADA tipo para un vehiculo.
    Retorna dict: {tipo_servicio: {"kilometraje": int, "fecha_servicio": date}}
    """
    query = text("""
        SELECT DISTINCT ON (tipo_servicio)
            tipo_servicio,
            kilometraje,
            fecha_servicio
        FROM fleet.mantenimiento_vehiculo
        WHERE vehiculo_id = :vehiculo_id
        ORDER BY tipo_servicio, fecha_servicio DESC
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id})
    rows = result.all()

    return {
        row[0]: {"kilometraje": row[1], "fecha_servicio": row[2]}
        for row in rows
    }


async def _obtener_contrato_activo(db: AsyncSession, vehiculo_id: UUID):
    """Obtiene el contrato activo para un vehiculo."""
    query = (
        select(ContratoVehiculo)
        .where(
            ContratoVehiculo.vehiculo_id == vehiculo_id,
            ContratoVehiculo.estado_contrato == "ACTIVO",
            ContratoVehiculo.activo == True,
        )
        .order_by(desc(ContratoVehiculo.fecha_inicio))
        .limit(1)
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


def _calcular_proximos_mantenimientos(
    ultimos_por_tipo: dict, km_actual: int, contrato_activo
) -> List[dict]:
    """
    Calcula los proximos mantenimientos basados en la periodicidad.

    Args:
        ultimos_por_tipo: dict {tipo_servicio: {"kilometraje": int, "fecha_servicio": date}}
                          con el ultimo mantenimiento de CADA tipo.
        km_actual: kilometraje actual del vehiculo.
        contrato_activo: contrato activo (para determinar alerta_a).

    Returns:
        Lista de dicts con tipo_servicio, tipo_nombre, km_restante (puede ser negativo),
        dias_restantes (puede ser negativo), alerta_a, urgencia, vencido.
    """
    proximos = []

    for tipo, config in PERIODICIDAD_MANTENIMIENTO.items():
        ultimo = ultimos_por_tipo.get(tipo)

        # Base: kilometraje y fecha del ultimo mantenimiento de ESTE tipo
        # Si nunca se hizo, base = 0 km y hoy
        km_base = (
            ultimo["kilometraje"]
            if ultimo and ultimo["kilometraje"] is not None
            else 0
        )
        fecha_base = (
            ultimo["fecha_servicio"]
            if ultimo and ultimo["fecha_servicio"] is not None
            else datetime.now().date()
        )

        # Calcular km restante (puede ser NEGATIVO = vencido)
        if config.get("km"):
            km_proximo = km_base + config["km"]
            km_restante = km_proximo - km_actual
        else:
            km_restante = None

        # Calcular dias restantes (puede ser NEGATIVO = vencido)
        if config.get("dias"):
            fecha_proximo = fecha_base + timedelta(days=config["dias"])
            dias_restantes = (fecha_proximo - datetime.now().date()).days
        else:
            dias_restantes = None

        # Determinar destinatario
        alerta_a = config["alerta_a"]
        if contrato_activo and contrato_activo.tipo_contrato == "AUTO_GESTION":
            alerta_a = "dueno"
        if not contrato_activo:
            alerta_a = "dueno"

        # Determinar urgencia
        # - alta: vencido (km o dias < 0) o muy cerca (<= 500 km o <= 7 dias)
        # - media: proximo (<= 1000 km o <= 15 dias)
        vencido = (
            (km_restante is not None and km_restante < 0)
            or (dias_restantes is not None and dias_restantes < 0)
        )

        if vencido:
            urgencia = "alta"
        elif (km_restante is not None and km_restante <= 500) or (
            dias_restantes is not None and dias_restantes <= 7
        ):
            urgencia = "alta"
        else:
            urgencia = "media"

        proximos.append(
            {
                "tipo_servicio": tipo,
                "tipo_nombre": tipo.replace("_", " ").title(),
                "km_restante": km_restante,
                "dias_restantes": dias_restantes,
                "alerta_a": alerta_a,
                "urgencia": urgencia,
                "vencido": vencido,
            }
        )

    # Ordenar: vencidos primero, luego por urgencia
    proximos.sort(key=lambda x: (not x["vencido"], 0 if x["urgencia"] == "alta" else 1))

    return proximos