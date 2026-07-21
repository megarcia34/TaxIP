"""
Router para gestión de turnos de empleados
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/api/turnos", tags=["Turnos"])


@router.post("/checkin", status_code=status.HTTP_201_CREATED)
async def checkin_turno(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Iniciar un nuevo turno de trabajo.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "empleado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo empleados pueden iniciar turno"
        )
    
    # Verificar que no haya un turno activo
    query_check = text("""
        SELECT id FROM auth.turno_empleado
        WHERE empleado_id = :user_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_check, {"user_id": user_id})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes un turno activo"
        )
    
    # Obtener la empresa del empleado
    query_empresa = text("""
        SELECT e.id
        FROM auth.usuario_empresa ue
        JOIN tenant.empresa e ON e.id = ue.empresa_id
        WHERE ue.usuario_id = :user_id 
          AND ue.activo = true
          AND e.activo = true
        LIMIT 1
    """)
    result = await db.execute(query_empresa, {"user_id": user_id})
    empresa_row = result.first()
    
    if not empresa_row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empleado no vinculado a una empresa activa"
        )
    
    # Crear nuevo turno
    query_insert = text("""
        INSERT INTO auth.turno_empleado (
            id, empleado_id, empresa_id, fecha_inicio, estado, created_at
        )
        VALUES (
            gen_random_uuid(), :empleado_id, :empresa_id, NOW(), 'ACTIVO', NOW()
        )
        RETURNING id, fecha_inicio
    """)
    
    result = await db.execute(query_insert, {
        "empleado_id": user_id,
        "empresa_id": empresa_row[0]
    })
    await db.commit()
    
    row = result.first()
    return {
        "success": True,
        "message": "Turno iniciado correctamente",
        "turno_id": str(row[0]),
        "fecha_inicio": row[1].isoformat() if row[1] else None
    }


@router.post("/checkout", status_code=status.HTTP_200_OK)
async def checkout_turno(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Cerrar el turno de trabajo activo.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "empleado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo empleados pueden cerrar turno"
        )
    
    # Buscar turno activo
    query_turno = text("""
        SELECT id FROM auth.turno_empleado
        WHERE empleado_id = :user_id AND estado = 'ACTIVO'
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"user_id": user_id})
    turno_row = result.first()
    
    if not turno_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay turno activo para cerrar"
        )
    
    # Cerrar turno
    query_update = text("""
        UPDATE auth.turno_empleado
        SET estado = 'CERRADO', fecha_fin = NOW(), updated_at = NOW()
        WHERE id = :turno_id
    """)
    
    await db.execute(query_update, {"turno_id": turno_row[0]})
    await db.commit()
    
    return {
        "success": True,
        "message": "Turno cerrado correctamente",
        "turno_id": str(turno_row[0])
    }


@router.get("/estado")
async def estado_turno(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Verificar si el empleado tiene un turno activo.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "empleado":
        return {"activo": False, "message": "No es empleado"}
    
    query = text("""
        SELECT id, fecha_inicio
        FROM auth.turno_empleado
        WHERE empleado_id = :user_id AND estado = 'ACTIVO'
        ORDER BY fecha_inicio DESC
        LIMIT 1
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if row:
        return {
            "activo": True,
            "turno_id": str(row[0]),
            "fecha_inicio": row[1].isoformat() if row[1] else None
        }
    
    return {"activo": False, "message": "No hay turno activo"}