"""
Perfil del propietario
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/perfil", tags=["Perfil Propietario"])


@router.get("")
async def get_perfil(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el perfil del propietario autenticado.
    """
    user_id, control_base_id, email, tipo = current_user
    
    # Verificar que es propietario
    query_verify = text("""
        SELECT id FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query_verify, {"user_id": user_id})
    if not result.first():
        raise HTTPException(status_code=403, detail="No eres propietario")
    
    # Obtener datos del perfil
    query = text("""
        SELECT 
            u.id,
            u.email,
            u.activo,
            p.nombre,
            p.apellido,
            p.telefono,
            p.documento,
            p.direccion,
            cb.nombre as control_base_nombre,
            cb.id as control_base_id
        FROM auth.usuario u
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN tenant.control_base cb ON cb.id = u.control_base_id
        WHERE u.id = :user_id
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": str(row[0]),
        "email": row[1],
        "activo": row[2],
        "nombre": row[3] or "",
        "apellido": row[4] or "",
        "telefono": row[5] or "",
        "documento": row[6] or "",
        "direccion": row[7] or "",
        "tenant": {
            "id": str(row[9]) if row[9] else None,
            "nombre": row[8] or ""
        }
    }


@router.put("")
async def update_perfil(
    data: dict,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza el perfil del propietario.
    """
    user_id, control_base_id, email, tipo = current_user
    
    # Verificar que es propietario
    query_verify = text("""
        SELECT id FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query_verify, {"user_id": user_id})
    if not result.first():
        raise HTTPException(status_code=403, detail="No eres propietario")
    
    # Construir UPDATE dinámico
    updates = []
    params = {"user_id": user_id}
    
    campos_permitidos = ["nombre", "apellido", "telefono", "documento", "direccion"]
    
    for campo in campos_permitidos:
        if campo in data:
            updates.append(f"{campo} = :{campo}")
            params[campo] = data[campo]
    
    if not updates:
        return {"success": True, "message": "No hay datos para actualizar"}
    
    query = text(f"""
        UPDATE auth.perfil_general
        SET {', '.join(updates)}
        WHERE usuario_id = :user_id
        RETURNING id
    """)
    
    result = await db.execute(query, params)
    await db.commit()
    
    if not result.first():
        return {"success": False, "message": "Perfil no encontrado"}
    
    return {"success": True, "message": "Perfil actualizado correctamente"}