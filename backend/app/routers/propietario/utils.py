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
    turno: str,
    db: AsyncSession
):
    """
    Verifica que un chofer esté disponible para un turno específico.
    Retorna True si está disponible, lanza HTTPException si no.
    """
    query = text("""
        SELECT u.id FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON tu.id = u.tipo_usuario_id
        WHERE u.id = :chofer_id 
          AND u.control_base_id = :control_base_id 
          AND u.activo = true 
          AND tu.nombre = 'chofer'
          AND NOT EXISTS (
              SELECT 1 FROM fleet.contrato_vehiculo cc
              WHERE cc.chofer_id = u.id
                AND cc.turno_asignado = :turno
                AND cc.activo = true
                AND cc.fecha_fin IS NULL
          )
    """)
    result = await db.execute(query, {"chofer_id": chofer_id, "control_base_id": control_base_id, "turno": turno})
    if not result.first():
        raise HTTPException(status_code=409, detail=f"El chofer no está disponible para el turno {turno}")
    return True