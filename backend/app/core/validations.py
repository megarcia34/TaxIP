"""
Validaciones de suspensión y estado para tenant, empresa y usuario
Reutilizables en cualquier endpoint
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID


async def validar_tenant_activo(control_base_id: UUID, db: AsyncSession):
    """
    Verifica que el tenant esté activo y no suspendido.
    Lanza HTTP 403 si está inactivo o suspendido.
    """
    if not control_base_id:
        return True  # Super Admin (sin tenant)

    query = text("""
        SELECT activo, fecha_suspension, motivo_suspension
        FROM tenant.control_base
        WHERE id = :control_base_id
    """)
    result = await db.execute(query, {"control_base_id": control_base_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant no encontrado"
        )

    activo, fecha_suspension, motivo = row

    if not activo:
        motivo_msg = motivo or "Sin motivo especificado"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tenant inactivo. Motivo: {motivo_msg}"
        )

    if fecha_suspension is not None:
        motivo_msg = motivo or "Sin motivo especificado"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tenant suspendido desde {fecha_suspension}. Motivo: {motivo_msg}"
        )

    return True


async def validar_empresa_activa(empresa_id: UUID, db: AsyncSession):
    """
    Verifica que la empresa esté activa y no suspendida.
    Lanza HTTP 403 si está inactiva o suspendida.
    """
    if not empresa_id:
        return True  # Si no tiene empresa, no validar

    query = text("""
        SELECT activo, fecha_suspension, motivo_suspension
        FROM tenant.empresa
        WHERE id = :empresa_id
    """)
    result = await db.execute(query, {"empresa_id": empresa_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    activo, fecha_suspension, motivo = row

    if not activo:
        motivo_msg = motivo or "Sin motivo especificado"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Empresa inactiva. Motivo: {motivo_msg}"
        )

    if fecha_suspension is not None:
        motivo_msg = motivo or "Sin motivo especificado"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Empresa suspendida desde {fecha_suspension}. Motivo: {motivo_msg}"
        )

    return True


async def validar_usuario_activo(user_id: UUID, db: AsyncSession):
    """
    Verifica que el usuario esté activo y no suspendido.
    Lanza HTTP 403 si está inactivo o suspendido.
    NOTA: Ya verifica `activo`, pero también `fecha_suspension`.
    """
    query = text("""
        SELECT activo, fecha_suspension, motivo_suspension
        FROM auth.usuario
        WHERE id = :user_id
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    activo, fecha_suspension, motivo = row

    if not activo:
        motivo_msg = motivo or "Sin motivo especificado"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario inactivo. Motivo: {motivo_msg}"
        )

    if fecha_suspension is not None:
        motivo_msg = motivo or "Sin motivo especificado"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario suspendido desde {fecha_suspension}. Motivo: {motivo_msg}"
        )

    return True


async def validar_tenant_y_empresa_para_empleado(
    user_id: UUID,
    db: AsyncSession
):
    """
    Validación combinada para empleados:
    1. Obtiene su empresa
    2. Valida que la empresa esté activa
    3. Valida que el tenant de la empresa esté activo
    """
    # Obtener empresa del empleado
    query = text("""
        SELECT e.id, e.control_base_id
        FROM auth.usuario_empresa ue
        JOIN tenant.empresa e ON e.id = ue.empresa_id
        WHERE ue.usuario_id = :user_id AND ue.activo = true
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empleado no vinculado a ninguna empresa activa"
        )

    empresa_id = row[0]
    control_base_id = row[1]

    # Validar empresa
    await validar_empresa_activa(empresa_id, db)

    # Validar tenant
    await validar_tenant_activo(control_base_id, db)

    return {"empresa_id": empresa_id, "control_base_id": control_base_id}