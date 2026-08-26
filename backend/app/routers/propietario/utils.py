# app/routers/propietario/utils.py
# Funciones auxiliares compartidas entre módulos

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from fastapi import HTTPException, status


async def verificar_vehiculo_propietario(
    vehiculo_id: UUID,
    propietario_id: UUID,
    db: AsyncSession,
    mensaje_error: str = "Vehículo no encontrado o no pertenece al propietario"
):
    """
    Verifica que un vehículo pertenezca al propietario.
    Lanza HTTPException 404 si no es así.
    """
    query = text("""
        SELECT v.id FROM fleet.vehiculo v
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = v.id
        WHERE v.id = :vehiculo_id 
          AND pv.propietario_id = :propietario_id 
          AND pv.activo = true
    """)
    result = await db.execute(query, {"vehiculo_id": vehiculo_id, "propietario_id": propietario_id})
    if not result.first():
        raise HTTPException(status_code=404, detail=mensaje_error)
    return True


async def verificar_chofer_disponible(
    chofer_id: UUID,
    control_base_id: UUID,
    db: AsyncSession
):
    """
    Verifica que un chofer esté disponible para un nuevo contrato.
    Ya NO usa turno_asignado (campo eliminado).
    La verificación se basa en:
    1. Que el chofer exista y esté activo
    2. Que no tenga un contrato activo con otro vehículo
    3. Que no tenga un turno activo
    """
    # Verificar que el chofer existe, está activo y pertenece al tenant
    query = text("""
        SELECT u.id FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON tu.id = u.tipo_usuario_id
        WHERE u.id = :chofer_id 
          AND u.control_base_id = :control_base_id 
          AND u.activo = true 
          AND tu.nombre = 'chofer'
    """)
    result = await db.execute(query, {"chofer_id": chofer_id, "control_base_id": control_base_id})
    if not result.first():
        raise HTTPException(
            status_code=404,
            detail="Chofer no encontrado o inactivo en este tenant"
        )

    # Verificar que el chofer no tenga un contrato activo con otro vehículo
    query_contrato = text("""
        SELECT cc.id FROM fleet.contrato_vehiculo cc
        WHERE cc.chofer_id = :chofer_id
          AND cc.estado_contrato = 'ACTIVO'
          AND cc.activo = true
          AND cc.fecha_fin IS NULL
        LIMIT 1
    """)
    result = await db.execute(query_contrato, {"chofer_id": chofer_id})
    if result.first():
        raise HTTPException(
            status_code=409,
            detail="El chofer ya tiene un contrato activo con otro vehículo"
        )

    # Verificar que el chofer no tenga un turno activo
    query_turno = text("""
        SELECT t.id FROM fleet.turno_chofer t
        WHERE t.chofer_id = :chofer_id
          AND t.estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"chofer_id": chofer_id})
    if result.first():
        raise HTTPException(
            status_code=409,
            detail="El chofer tiene un turno activo en curso"
        )

    return True


# ============================================================
# HELPER PARA KILOMETRAJE DEL VEHÍCULO
# ============================================================

async def obtener_km_actual_vehiculo(
    vehiculo_id: UUID,
    db: AsyncSession
) -> int:
    """
    Obtiene el kilometraje actual del vehículo.
    Prioridad: 1. Turno activo, 2. Viajes finalizados
    """
    # Primero desde turno activo
    query_turno = text("""
        SELECT km_inicial, km_final
        FROM fleet.turno_chofer
        WHERE vehiculo_id = :vehiculo_id AND estado = 'ACTIVO'
        ORDER BY inicio_turno DESC
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"vehiculo_id": vehiculo_id})
    row = result.first()
    
    if row:
        if row[1] is not None:
            return int(row[1])
        return int(row[0] or 0)
    
    # Si no hay turno activo, calcular desde viajes
    query_viajes = text("""
        SELECT COALESCE(SUM(distancia_metros) / 1000, 0)::INTEGER
        FROM trip.viaje_solicitado
        WHERE vehiculo_id = :vehiculo_id AND estado = 'finalizado'
    """)
    result = await db.execute(query_viajes, {"vehiculo_id": vehiculo_id})
    km = result.scalar() or 0
    return int(km)


# ============================================================
# HELPER PARA NEUMÁTICOS
# ============================================================

async def verificar_neumatico_propietario(
    neumatico_id: UUID,
    propietario_id: UUID,
    db: AsyncSession,
    mensaje_error: str = "Neumático no encontrado o no pertenece a un vehículo del propietario"
):
    """
    Verifica que un neumático pertenezca a un vehículo que es propiedad del propietario.
    Lanza HTTPException 404 si no es así.
    """
    query = text("""
        SELECT 1 
        FROM fleet.neumatico_vehiculo nv
        INNER JOIN fleet.propietario_vehiculo pv ON pv.vehiculo_id = nv.vehiculo_id
        WHERE nv.id = :neumatico_id 
          AND pv.propietario_id = :propietario_id 
          AND pv.activo = true
        LIMIT 1
    """)
    result = await db.execute(query, {
        "neumatico_id": neumatico_id, 
        "propietario_id": propietario_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail=mensaje_error)
    return True