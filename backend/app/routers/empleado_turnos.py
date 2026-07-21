"""
Turnos de Empleados (Recepcionistas)
Check-in / Check-out y gestión de turnos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, get_admin_empresa_user
from app.core.validations import validar_usuario_activo, validar_empresa_activa

router = APIRouter(prefix="/api/empleado/turnos", tags=["Empleado - Turnos"])


# ============================================
# Schemas
# ============================================

class CheckInRequest(BaseModel):
    """Solicitud de check-in"""
    empresa_id: UUID


class CheckInResponse(BaseModel):
    turno_id: UUID
    empleado_id: UUID
    empresa_id: UUID
    fecha_inicio: datetime
    estado: str
    mensaje: str


class CheckOutResponse(BaseModel):
    turno_id: UUID
    empleado_id: UUID
    empresa_id: UUID
    fecha_inicio: datetime
    fecha_fin: datetime
    viajes_gestionados: int
    facturado_total: float
    estado: str
    mensaje: str


class TurnoActivoResponse(BaseModel):
    tiene_turno_activo: bool
    turno_id: Optional[UUID] = None
    empresa_id: Optional[UUID] = None
    empresa_nombre: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    viajes_gestionados: Optional[int] = None
    facturado_total: Optional[float] = None
    mensaje: Optional[str] = None


# ============================================
# ENDPOINTS
# ============================================

@router.post("/check-in", response_model=CheckInResponse)
async def check_in(
    request: CheckInRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Iniciar turno (Check-in) para un empleado.
    Solo puede tener un turno activo a la vez.
    """
    user_id, control_base_id, email, tipo = current_user
    
    # Verificar que el usuario es empleado
    if tipo.lower() != "empleado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo empleados pueden realizar check-in"
        )
    
    # Validar que el usuario no esté suspendido
    await validar_usuario_activo(user_id, db)
    
    # Verificar que la empresa está activa
    await validar_empresa_activa(request.empresa_id, db)
    
    # Verificar que el empleado pertenece a la empresa
    check_empresa = text("""
        SELECT id FROM auth.usuario_empresa
        WHERE usuario_id = :user_id AND empresa_id = :empresa_id AND activo = true
    """)
    result = await db.execute(check_empresa, {
        "user_id": user_id,
        "empresa_id": request.empresa_id
    })
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empleado no pertenece a esta empresa o está inactivo"
        )
    
    # Verificar que no tenga un turno activo
    check_turno = text("""
        SELECT id FROM auth.turno_empleado
        WHERE empleado_id = :user_id AND estado = 'ACTIVO'
    """)
    result = await db.execute(check_turno, {"user_id": user_id})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes un turno activo. Cierra el turno actual antes de iniciar uno nuevo."
        )
    
    # Crear turno
    insert_turno = text("""
        INSERT INTO auth.turno_empleado (id, empleado_id, empresa_id, fecha_inicio, estado)
        VALUES (gen_random_uuid(), :user_id, :empresa_id, NOW(), 'ACTIVO')
        RETURNING id, fecha_inicio
    """)
    result = await db.execute(insert_turno, {
        "user_id": user_id,
        "empresa_id": request.empresa_id
    })
    row = result.first()
    
    await db.commit()
    
    turno_id = row[0]
    fecha_inicio = row[1]
    
    return CheckInResponse(
        turno_id=turno_id,
        empleado_id=user_id,
        empresa_id=request.empresa_id,
        fecha_inicio=fecha_inicio,
        estado="ACTIVO",
        mensaje="Check-in realizado correctamente. Turno iniciado."
    )


@router.post("/check-out", response_model=CheckOutResponse)
async def check_out(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cerrar turno (Check-out) para un empleado.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "empleado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo empleados pueden realizar check-out"
        )
    
    # Validar que el usuario no esté suspendido
    await validar_usuario_activo(user_id, db)
    
    # Obtener turno activo
    query = text("""
        SELECT 
            t.id, t.empresa_id, t.fecha_inicio, 
            t.viajes_gestionados, t.facturado_total
        FROM auth.turno_empleado t
        WHERE t.empleado_id = :user_id AND t.estado = 'ACTIVO'
        ORDER BY t.fecha_inicio DESC
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay turno activo para cerrar"
        )
    
    turno_id = row[0]
    empresa_id = row[1]
    fecha_inicio = row[2]
    viajes_gestionados = row[3] or 0
    facturado_total = float(row[4] or 0)
    
    # Cerrar turno
    update_query = text("""
        UPDATE auth.turno_empleado
        SET estado = 'CERRADO', fecha_fin = NOW(), updated_at = NOW()
        WHERE id = :turno_id AND empleado_id = :user_id
        RETURNING fecha_fin
    """)
    result = await db.execute(update_query, {"turno_id": turno_id, "user_id": user_id})
    row = result.first()
    fecha_fin = row[0]
    
    await db.commit()
    
    return CheckOutResponse(
        turno_id=turno_id,
        empleado_id=user_id,
        empresa_id=empresa_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        viajes_gestionados=viajes_gestionados,
        facturado_total=facturado_total,
        estado="CERRADO",
        mensaje=f"Check-out realizado. Turno finalizado. Viajes: {viajes_gestionados}, Facturado: ${facturado_total:.2f}"
    )


@router.get("/activo", response_model=TurnoActivoResponse)
async def obtener_turno_activo(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener el turno activo del empleado actual.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "empleado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo empleados pueden consultar su turno"
        )
    
    # Obtener empresa del empleado para mostrar nombre
    empresa_query = text("""
        SELECT e.id, e.nombre
        FROM auth.usuario_empresa ue
        JOIN tenant.empresa e ON e.id = ue.empresa_id
        WHERE ue.usuario_id = :user_id AND ue.activo = true
        LIMIT 1
    """)
    empresa_result = await db.execute(empresa_query, {"user_id": user_id})
    empresa_row = empresa_result.first()
    empresa_nombre = empresa_row[1] if empresa_row else None
    
    query = text("""
        SELECT 
            t.id, t.empresa_id, t.fecha_inicio,
            t.viajes_gestionados, t.facturado_total
        FROM auth.turno_empleado t
        WHERE t.empleado_id = :user_id AND t.estado = 'ACTIVO'
        ORDER BY t.fecha_inicio DESC
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        return TurnoActivoResponse(
            tiene_turno_activo=False,
            mensaje="No hay turno activo. Realice check-in para comenzar."
        )
    
    return TurnoActivoResponse(
        tiene_turno_activo=True,
        turno_id=row[0],
        empresa_id=row[1],
        empresa_nombre=empresa_nombre,
        fecha_inicio=row[2],
        viajes_gestionados=row[3] or 0,
        facturado_total=float(row[4] or 0),
        mensaje="Turno activo"
    )


# ============================================
# ADMIN EMPRESA: Gestionar turnos de empleados
# ============================================

@router.get("/admin/empleados/{empleado_id}/turnos")
async def listar_turnos_empleado(
    empleado_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: tuple = Depends(get_admin_empresa_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin Empresa: Listar todos los turnos de un empleado.
    """
    admin_user_id, control_base_id, email, tipo, empresa_id, empresa_nombre = current_user
    
    # Verificar que el empleado pertenece a la empresa del admin
    check_query = text("""
        SELECT id FROM auth.usuario_empresa
        WHERE usuario_id = :empleado_id AND empresa_id = :empresa_id
    """)
    result = await db.execute(check_query, {
        "empleado_id": empleado_id,
        "empresa_id": empresa_id
    })
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empleado no pertenece a tu empresa"
        )
    
    query = text("""
        SELECT 
            t.id, t.fecha_inicio, t.fecha_fin, t.estado,
            t.viajes_gestionados, t.facturado_total, t.created_at
        FROM auth.turno_empleado t
        WHERE t.empleado_id = :empleado_id
        ORDER BY t.fecha_inicio DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(query, {
        "empleado_id": empleado_id,
        "limit": limit,
        "offset": offset
    })
    rows = result.all()
    
    return [
        {
            "id": str(row[0]),
            "fecha_inicio": row[1],
            "fecha_fin": row[2],
            "estado": row[3],
            "viajes_gestionados": row[4] or 0,
            "facturado_total": float(row[5] or 0),
            "created_at": row[6]
        }
        for row in rows
    ]


@router.get("/admin/resumen")
async def obtener_resumen_turnos(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    current_user: tuple = Depends(get_admin_empresa_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin Empresa: Obtener resumen de turnos de todos los empleados.
    """
    admin_user_id, control_base_id, email, tipo, empresa_id, empresa_nombre = current_user
    
    # Si no se especifican fechas, usar el mes actual
    if not fecha_desde:
        from datetime import datetime
        fecha_desde = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    if not fecha_hasta:
        from datetime import datetime, timedelta
        fecha_hasta = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    query = text("""
        SELECT 
            u.id as empleado_id,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) as empleado_nombre,
            COUNT(t.id) as total_turnos,
            SUM(t.viajes_gestionados) as total_viajes,
            SUM(t.facturado_total) as total_facturado,
            COUNT(CASE WHEN t.estado = 'ACTIVO' THEN 1 END) as turnos_activos
        FROM auth.usuario u
        JOIN auth.usuario_empresa ue ON ue.usuario_id = u.id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        LEFT JOIN auth.turno_empleado t ON t.empleado_id = u.id 
            AND DATE(t.fecha_inicio) BETWEEN :fecha_desde AND :fecha_hasta
        WHERE ue.empresa_id = :empresa_id
          AND ue.activo = true
          AND u.tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'empleado')
        GROUP BY u.id, p.nombre, p.apellido, u.email
        ORDER BY total_viajes DESC
    """)
    
    result = await db.execute(query, {
        "empresa_id": empresa_id,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta
    })
    rows = result.all()
    
    return [
        {
            "empleado_id": str(row[0]),
            "empleado_nombre": row[1],
            "total_turnos": row[2] or 0,
            "total_viajes": row[3] or 0,
            "total_facturado": float(row[4] or 0),
            "turnos_activos": row[5] or 0
        }
        for row in rows
    ]