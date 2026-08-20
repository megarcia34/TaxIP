"""
FastAPI dependencies: authentication, database sessions, rate limiting
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Tuple, Optional, Dict, Any, Annotated
from uuid import UUID
import logging

from app.database import get_db
from app.core.security import decode_token

security = HTTPBearer()
logger = logging.getLogger(__name__)


# ============================================================
# DEPENDENCIAS BASE
# ============================================================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Tuple[UUID, UUID, str, str]:
    """
    Get current authenticated user from JWT token.
    Validates token and returns user data.
    """
    token = credentials.credentials
    logger.info(f"🔍 get_current_user - token recibido (longitud: {len(token)})")
    logger.info(f"🔍 Token preview: {token[:30]}...")
    
    payload = decode_token(token)
    logger.info(f"🔍 Payload decodificado: {payload}")
    
    # ✅ Validación mejorada: verificar que el payload NO esté vacío
    if not payload or not isinstance(payload, dict) or len(payload) == 0:
        logger.error(f"❌ Token inválido o vacío - longitud: {len(token)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Por favor, inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar tipo de token
    if payload.get("type") != "access":
        logger.error(f"❌ Tipo de token incorrecto: {payload.get('type')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.error("❌ No hay 'sub' en el payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Payload del token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"✅ user_id_str: {user_id_str}")
    
    query = text("""
        SELECT u.id, u.control_base_id, u.email, tu.nombre as tipo_usuario
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        WHERE u.id = :user_id AND u.activo = true
    """)
    
    result = await db.execute(query, {"user_id": UUID(user_id_str)})
    row = result.first()
    
    if not row:
        logger.error(f"❌ Usuario no encontrado o inactivo: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"✅ Usuario autenticado: {row[2]} (tipo: {row[3]})")
    
    return (row[0], row[1], row[2], row[3])


# ============================================================
# DEPENDENCIAS DE ROLES (NUEVA JERARQUÍA - FASES 1 y 2)
# ============================================================

async def get_super_admin_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """
    Verificar que el usuario es SUPER ADMIN (admin sin control_base_id).
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    
    if control_base_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required (control_base_id must be NULL)"
        )
    
    return current_user


async def get_admin_tenant_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """
    Verificar que el usuario es ADMIN TENANT (admin con control_base_id).
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin Tenant access required"
        )
    
    if control_base_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin Tenant access required (control_base_id required)"
        )
    
    return current_user


async def get_admin_empresa_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tuple[UUID, UUID, str, str, UUID, str]:
    """
    Verificar que el usuario es ADMIN EMPRESA.
    Retorna: (user_id, control_base_id, email, tipo, empresa_id, empresa_nombre)
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() == "admin" and control_base_id is not None:
        query = text("""
            SELECT id, nombre FROM tenant.empresa
            WHERE control_base_id = :control_base_id AND activo = true
            ORDER BY created_at ASC
            LIMIT 1
        """)
        result = await db.execute(query, {"control_base_id": control_base_id})
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No hay empresas activas en este tenant para administrar"
            )
        
        return (user_id, control_base_id, email, tipo, row[0], row[1])
    
    if tipo.lower() == "empleado":
        query = text("""
            SELECT e.id, e.nombre
            FROM auth.usuario_empresa ue
            JOIN tenant.empresa e ON e.id = ue.empresa_id
            WHERE ue.usuario_id = :user_id 
              AND ue.activo = true
              AND ue.rol IN ('admin_empresa', 'administrador_empresa')
              AND e.activo = true
            LIMIT 1
        """)
        result = await db.execute(query, {"user_id": user_id})
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin Empresa access required"
            )
        
        return (user_id, control_base_id, email, tipo, row[0], row[1])
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin Empresa access required"
    )


async def get_empleado_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tuple[UUID, UUID, str, str, UUID, str, UUID]:
    """
    Verificar que el usuario es EMPLEADO y tiene turno activo.
    Retorna: (user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id)
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "empleado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empleado access required"
        )
    
    query_empresa = text("""
        SELECT e.id, e.nombre
        FROM auth.usuario_empresa ue
        JOIN tenant.empresa e ON e.id = ue.empresa_id
        WHERE ue.usuario_id = :user_id 
          AND ue.activo = true
          AND e.activo = true
        LIMIT 1
    """)
    result = await db.execute(query_empresa, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empleado no vinculado a una empresa activa"
        )
    
    empresa_id = row[0]
    empresa_nombre = row[1]
    
    query_turno = text("""
        SELECT id, fecha_inicio
        FROM auth.turno_empleado
        WHERE empleado_id = :user_id 
          AND estado = 'ACTIVO'
        ORDER BY fecha_inicio DESC
        LIMIT 1
    """)
    result = await db.execute(query_turno, {"user_id": user_id})
    turno_row = result.first()
    
    if not turno_row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No hay turno activo. Realice check-in para comenzar a operar."
        )
    
    turno_id = turno_row[0]
    
    return (user_id, control_base_id, email, tipo, empresa_id, empresa_nombre, turno_id)


async def get_empresa_context(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Devuelve contexto de empresa para endpoints que necesitan empresa_id.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() == "admin" and control_base_id is not None:
        query = text("""
            SELECT id, nombre FROM tenant.empresa
            WHERE control_base_id = :control_base_id AND activo = true
            ORDER BY created_at ASC
            LIMIT 1
        """)
        result = await db.execute(query, {"control_base_id": control_base_id})
        row = result.first()
        if row:
            return {
                "user_id": str(user_id),
                "control_base_id": str(control_base_id),
                "email": email,
                "tipo_usuario": tipo,
                "empresa_id": str(row[0]),
                "empresa_nombre": row[1],
                "rol": "admin"
            }
    
    query = text("""
        SELECT e.id, e.nombre, ue.rol
        FROM auth.usuario_empresa ue
        JOIN tenant.empresa e ON e.id = ue.empresa_id
        WHERE ue.usuario_id = :user_id AND ue.activo = true
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if row:
        return {
            "user_id": str(user_id),
            "control_base_id": str(control_base_id) if control_base_id else None,
            "email": email,
            "tipo_usuario": tipo,
            "empresa_id": str(row[0]),
            "empresa_nombre": row[1],
            "rol": row[2] or "recepcionista"
        }
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No se pudo determinar el contexto de empresa"
    )


# ============================================================
# FUNCIONES DE VALIDACIÓN DE SUSPENSIÓN
# ============================================================

async def validar_tenant_activo(control_base_id: UUID, db: AsyncSession) -> bool:
    """Verifica que el tenant esté activo (no suspendido)."""
    query = text("""
        SELECT activo FROM tenant.control_base
        WHERE id = :control_base_id
    """)
    result = await db.execute(query, {"control_base_id": control_base_id})
    row = result.first()
    if not row or not row[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant suspendido o inactivo"
        )
    return True


async def validar_empresa_activa(empresa_id: UUID, db: AsyncSession) -> bool:
    """Verifica que la empresa esté activa (no suspendida)."""
    query = text("""
        SELECT activo FROM tenant.empresa
        WHERE id = :empresa_id
    """)
    result = await db.execute(query, {"empresa_id": empresa_id})
    row = result.first()
    if not row or not row[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empresa suspendida o inactiva"
        )
    return True


async def validar_usuario_activo(user_id: UUID, db: AsyncSession) -> bool:
    """Verifica que el usuario esté activo (no suspendido)."""
    query = text("""
        SELECT activo FROM auth.usuario
        WHERE id = :user_id
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    if not row or not row[0]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario suspendido o inactivo"
        )
    return True


# ============================================================
# FUNCIONES DE COMPATIBILIDAD - ROLES
# ⚠️ DEPRECADAS - Mantener solo para compatibilidad
# ============================================================

async def get_current_admin_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """⚠️ COMPATIBILIDAD - Admin genérico"""
    user_id, control_base_id, email, tipo = current_user
    if tipo.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de administrador requerido"
        )
    return current_user


async def get_current_driver_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tuple[UUID, UUID, str, str]:
    """
    Verifica que el usuario sea chofer o tenga capacidad de chofer.
    """
    user_id, control_base_id, email, tipo = current_user
    
    # 1. Verificar si es chofer directamente
    es_chofer_directo = (tipo.lower() == "chofer")
    
    # 2. Verificar si tiene capacidad chofer via usuario_rol
    query = text("""
        SELECT 1 FROM auth.usuario_rol
        WHERE usuario_id = :user_id
        AND tipo_usuario_id = (SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer')
        AND activo = true
    """)
    result = await db.execute(query, {"user_id": user_id})
    tiene_capacidad_chofer = result.first() is not None
    
    if not (es_chofer_directo or tiene_capacidad_chofer):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de chofer requerido"
        )
    
    return current_user


async def get_current_passenger_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """⚠️ COMPATIBILIDAD - Pasajero"""
    user_id, control_base_id, email, tipo = current_user
    if tipo.lower() != "pasajero":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de pasajero requerido"
        )
    return current_user


async def get_current_empleado_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """⚠️ COMPATIBILIDAD - Empleado"""
    user_id, control_base_id, email, tipo = current_user
    if tipo.lower() != "empleado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de empleado requerido"
        )
    return current_user


async def get_current_propietario_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """⚠️ COMPATIBILIDAD - Propietario"""
    user_id, control_base_id, email, tipo = current_user
    if tipo.lower() != "propietario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de propietario requerido"
        )
    return current_user


async def get_current_empresa_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """⚠️ COMPATIBILIDAD - Empresa (admin o empleado)"""
    user_id, control_base_id, email, tipo = current_user
    if tipo.lower() not in ["admin", "empleado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de empresa requerido"
        )
    return current_user


# ============================================================
# DEPENDENCIAS PARA CONTROL BASE (SOLO ADMIN TENANT Y SUPER ADMIN)
# ============================================================

async def get_control_base_admin_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> Tuple[UUID, UUID, str, str]:
    """
    Verifica que el usuario sea Super Admin o Admin Tenant para acceder a control-base.
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de administrador requerido"
        )
    
    # Super Admin (control_base_id NULL) o Admin Tenant (control_base_id NOT NULL)
    # Ambos son válidos para control-base
    return current_user


# ============================================================
# FUNCIONES DE CONTEXTO - PARA ROUTERS EXISTENTES (CORREGIDAS)
# ============================================================

async def get_propietario_context(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Contexto para routers de propietario."""
    user_id, control_base_id, email, tipo = current_user

    if tipo.lower() != "propietario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de propietario requerido"
        )

    query = text("""
        SELECT p.id, p.nombre, p.apellido, p.telefono, p.direccion,
               u.activo as usuario_activo
        FROM auth.perfil_general p
        INNER JOIN auth.usuario u ON u.id = p.usuario_id
        WHERE p.usuario_id = :user_id
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de propietario no encontrado"
        )

    # Contar vehículos del propietario
    query_vehiculos = text("""
        SELECT COUNT(*) FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
    """)
    result_vehiculos = await db.execute(query_vehiculos, {"user_id": user_id})
    total_vehiculos = result_vehiculos.scalar() or 0

    return {
        "user_id": str(user_id),
        "propietario_id": str(user_id),  # ✅ CORREGIDO: usar user_id
        "control_base_id": str(control_base_id) if control_base_id else None,
        "email": email,
        "tipo_usuario": tipo,
        "nombre": row[1],
        "apellido": row[2],
        "telefono": row[3],
        "direccion": row[4],
        "activo": row[5],
        "total_vehiculos": total_vehiculos
    }


async def get_chofer_context(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Contexto para routers de chofer."""
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "chofer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de chofer requerido"
        )
    
    # ✅ CORREGIDO: obtener activo desde usuario
    query = text("""
        SELECT p.id, p.nombre, p.apellido, p.telefono, p.direccion,
               c.licencia_numero, c.licencia_categoria, u.activo as usuario_activo
        FROM auth.perfil_general p
        JOIN fleet.chofer c ON c.usuario_id = p.usuario_id
        JOIN auth.usuario u ON u.id = p.usuario_id
        WHERE p.usuario_id = :user_id
    """)
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de chofer no encontrado"
        )
    
    # Verificar si tiene vehículo asignado
    query_vehiculo = text("""
        SELECT v.id, v.patente, v.activo
        FROM fleet.vehiculo v
        WHERE v.chofer_asignado_id = :user_id AND v.activo = true
        LIMIT 1
    """)
    result_vehiculo = await db.execute(query_vehiculo, {"user_id": user_id})
    vehiculo_row = result_vehiculo.first()
    
    return {
        "user_id": str(user_id),
        "control_base_id": str(control_base_id) if control_base_id else None,
        "email": email,
        "tipo_usuario": tipo,
        "chofer_id": str(row[0]),
        "nombre": row[1],
        "apellido": row[2],
        "telefono": row[3],
        "direccion": row[4],
        "licencia_numero": row[5],
        "licencia_categoria": row[6],
        "activo": row[7],  # ✅ Ahora viene de auth.usuario
        "vehiculo_asignado": {
            "id": str(vehiculo_row[0]) if vehiculo_row else None,
            "patente": vehiculo_row[1] if vehiculo_row else None,
            "activo": vehiculo_row[2] if vehiculo_row else None
        } if vehiculo_row else None
    }


async def get_empresa_context_compat(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """⚠️ COMPATIBILIDAD - Contexto de empresa."""
    user_id, control_base_id, email, tipo = current_user
    
    query = text("""
        SELECT e.id, e.nombre, e.tipo, e.control_base_id, ue.rol
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
            detail="Usuario no vinculado a ninguna empresa"
        )
    
    return {
        "user_id": str(user_id),
        "control_base_id": str(control_base_id) if control_base_id else None,
        "email": email,
        "tipo_usuario": tipo,
        "empresa_id": str(row[0]),
        "empresa_nombre": row[1],
        "empresa_tipo": row[2],
        "empresa_control_base_id": str(row[3]),
        "rol": row[4]
    }


# ============================================================
# FUNCIONES ADICIONALES PARA ROUTERS EXISTENTES
# ============================================================

async def get_propietario_id(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> UUID:
    """Devuelve el ID del propietario actual."""
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "propietario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de propietario requerido"
        )
    
    return user_id


async def get_chofer_id(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user)
) -> UUID:
    """Devuelve el ID del chofer actual."""
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() != "chofer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de chofer requerido"
        )
    
    return user_id


async def get_empresa_id_from_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UUID:
    """Devuelve el ID de la empresa del usuario actual."""
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() == "admin" and control_base_id is not None:
        query = text("""
            SELECT id FROM tenant.empresa
            WHERE control_base_id = :control_base_id AND activo = true
            ORDER BY created_at ASC
            LIMIT 1
        """)
        result = await db.execute(query, {"control_base_id": control_base_id})
        row = result.first()
        
        if row:
            return row[0]
    
    query = text("""
        SELECT e.id
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
            detail="Usuario no vinculado a ninguna empresa"
        )
    
    return row[0]


# ============================================================
# FUNCIONES PARA DASHBOARD DE EMPRESA
# ============================================================

async def get_current_empresa_admin_user(
    current_user: Tuple[UUID, UUID, str, str] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tuple[UUID, UUID, str, str, UUID, str]:
    """
    Obtiene el usuario actual verificando que es administrador de empresa.
    Retorna: (user_id, control_base_id, email, tipo, empresa_id, empresa_nombre)
    """
    user_id, control_base_id, email, tipo = current_user
    
    if tipo.lower() == "admin" and control_base_id is not None:
        query = text("""
            SELECT id, nombre FROM tenant.empresa
            WHERE control_base_id = :control_base_id AND activo = true
            ORDER BY created_at ASC
            LIMIT 1
        """)
        result = await db.execute(query, {"control_base_id": control_base_id})
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No hay empresas activas en este tenant para administrar"
            )
        
        return (user_id, control_base_id, email, tipo, row[0], row[1])
    
    if tipo.lower() == "empleado":
        query = text("""
            SELECT e.id, e.nombre
            FROM auth.usuario_empresa ue
            JOIN tenant.empresa e ON e.id = ue.empresa_id
            WHERE ue.usuario_id = :user_id 
              AND ue.activo = true
              AND ue.rol IN ('admin_empresa', 'administrador_empresa')
              AND e.activo = true
            LIMIT 1
        """)
        result = await db.execute(query, {"user_id": user_id})
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin Empresa access required"
            )
        
        return (user_id, control_base_id, email, tipo, row[0], row[1])
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso de administrador de empresa requerido"
    )


# ============================================================
# TYPE ALIASES PARA ENDPOINTS (SOLUCIÓN DEFINITIVA)
# ============================================================

CurrentUser = Annotated[Tuple[UUID, UUID, str, str], Depends(get_current_user)]
SuperAdminUser = Annotated[Tuple[UUID, UUID, str, str], Depends(get_super_admin_user)]
AdminTenantUser = Annotated[Tuple[UUID, UUID, str, str], Depends(get_admin_tenant_user)]
AdminEmpresaUser = Annotated[Tuple[UUID, UUID, str, str, UUID, str], Depends(get_admin_empresa_user)]
EmpleadoUser = Annotated[Tuple[UUID, UUID, str, str, UUID, str, UUID], Depends(get_empleado_user)]
ControlBaseAdminUser = Annotated[Tuple[UUID, UUID, str, str], Depends(get_control_base_admin_user)]


# ============================================================
# EXPORTAR TODAS LAS FUNCIONES Y TIPOS
# ============================================================

__all__ = [
    # Base
    "get_current_user",
    
    # Nuevas (Fases 1 y 2)
    "get_super_admin_user",
    "get_admin_tenant_user",
    "get_admin_empresa_user",
    "get_empleado_user",
    "get_empresa_context",
    "validar_tenant_activo",
    "validar_empresa_activa",
    "validar_usuario_activo",
    
    # Compatibilidad - Roles
    "get_current_admin_user",
    "get_current_driver_user",
    "get_current_passenger_user",
    "get_current_empleado_user",
    "get_current_propietario_user",
    "get_current_empresa_user",
    
    # Dashboard
    "get_current_empresa_admin_user",
    
    # Control Base (NUEVO)
    "get_control_base_admin_user",
    
    # Contextos (CORREGIDOS)
    "get_propietario_context",
    "get_chofer_context",
    "get_empresa_context_compat",
    
    # IDs
    "get_propietario_id",
    "get_chofer_id",
    "get_empresa_id_from_user",
    
    # Type Aliases
    "CurrentUser",
    "SuperAdminUser",
    "AdminTenantUser",
    "AdminEmpresaUser",
    "EmpleadoUser",
    "ControlBaseAdminUser",
]
# ============================================
# FILTROS PARA REPORTES POR ROL
# ============================================

async def get_filtros_reporte(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Retorna los filtros aplicables según el rol del usuario
    para usar en consultas de reportes y auditoría
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    filtros = {
        "user_id": user_id,
        "control_base_id": control_base_id,
        "tipo_usuario": tipo_usuario,
        "empresa_id": None,
        "propietario_id": None,
        "chofer_id": None,
        "is_super_admin": tipo_usuario.lower() == "super_admin",
        "is_admin_tenant": tipo_usuario.lower() in ["admin", "admin_tenant"],
        "is_admin_empresa": tipo_usuario.lower() == "admin_empresa",
        "is_empresa": tipo_usuario.lower() == "empresa",
        "is_propietario": tipo_usuario.lower() in ["propietario", "admin_propietario"],
        "is_empleado": tipo_usuario.lower() == "empleado",
        "is_chofer": tipo_usuario.lower() in ["chofer", "conductor"],
    }
    
    # Si es Super Admin, no filtrar por tenant
    if filtros["is_super_admin"]:
        filtros["control_base_id"] = None
        return filtros
    
    # Si es Admin Tenant, filtrar por su tenant
    if filtros["is_admin_tenant"] and control_base_id:
        filtros["control_base_id"] = control_base_id
        return filtros
    
    # Si es Empresa o Admin Empresa, obtener su empresa_id
    if filtros["is_empresa"] or filtros["is_admin_empresa"]:
        query = text("""
            SELECT empresa_id FROM auth.usuario_empresa
            WHERE usuario_id = :user_id AND activo = true
            LIMIT 1
        """)
        result = await db.execute(query, {"user_id": user_id})
        row = result.first()
        if row:
            filtros["empresa_id"] = row[0]
        return filtros
    
    # Si es Propietario o Admin Propietario
    if filtros["is_propietario"]:
        filtros["propietario_id"] = user_id
        return filtros
    
    # Si es Empleado, obtener su empresa_id
    if filtros["is_empleado"]:
        query = text("""
            SELECT empresa_id FROM auth.usuario_empresa
            WHERE usuario_id = :user_id AND activo = true
            LIMIT 1
        """)
        result = await db.execute(query, {"user_id": user_id})
        row = result.first()
        if row:
            filtros["empresa_id"] = row[0]
        return filtros
    
    # Si es Chofer
    if filtros["is_chofer"]:
        filtros["chofer_id"] = user_id
        return filtros
    
    return filtros


# ============================================
# OBTENER PROPIETARIO ID
# ============================================

async def get_propietario_id(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UUID:
    """
    Obtiene el ID del propietario desde el usuario actual
    Verifica que el usuario tenga rol de propietario
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    if tipo_usuario.lower() not in ["propietario", "admin_propietario"]:
        raise HTTPException(
            status_code=403,
            detail="Se requieren permisos de propietario"
        )
    
    # Verificar que tiene vehículos activos
    query = text("""
        SELECT id FROM fleet.propietario_vehiculo
        WHERE propietario_id = :user_id AND activo = true
        LIMIT 1
    """)
    result = await db.execute(query, {"user_id": user_id})
    if not result.first():
        raise HTTPException(
            status_code=403,
            detail="El propietario no tiene vehículos activos"
        )
    
    return user_id


# ============================================
# OBTENER TENANT ID ACTUAL
# ============================================

async def get_tenant_id_actual(
    current_user: tuple = Depends(get_current_user)
) -> Optional[UUID]:
    """
    Obtiene el tenant_id del usuario actual
    """
    _, control_base_id, _, tipo_usuario = current_user
    if tipo_usuario.lower() == "super_admin":
        return None  # Super Admin ve todos
    return control_base_id

# ============================================
# SUPER ADMIN DEPENDENCIES
# ============================================

async def get_current_super_admin_user(
    current_user: tuple = Depends(get_current_user)
) -> tuple:
    """
    Verifica que el usuario sea Super Admin
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    if tipo_usuario.lower() not in ["super_admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo para Super Admin"
        )
    
    return current_user