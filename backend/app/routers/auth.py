"""
Authentication routes: register, login, refresh, password recovery
Incluye validaciones de suspensión a nivel Tenant, Empresa y Usuario
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, timedelta
import uuid as uuid_lib
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_reset_token
)
from app.core.email import send_password_recovery_email
from app.core.validations import (
    validar_tenant_activo,
    validar_empresa_activa,
    validar_usuario_activo,
    validar_tenant_y_empresa_para_empleado
)
from app.schemas.auth_schemas import (
    RegistroRequest,
    RegistroResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RecuperarSolicitarRequest,
    RecuperarConfirmarRequest,
    RecuperarConfirmarResponse,
    CambiarContraseniaRequest,
    CambiarContraseniaResponse,
    UserMeResponse,
    PropietarioLoginResponse
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/registro", response_model=RegistroResponse)
async def registrar_usuario(
    request: RegistroRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user (pasajero, chofer, or propietario)
    Password is hashed with bcrypt (NO SHA512 legacy)
    """
    
    # Check if email already exists
    check_query = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(check_query, {"email": request.email})
    existing = result.first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Get tipo_usuario ID
    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = :tipo")
    tipo_result = await db.execute(tipo_query, {"tipo": request.tipo})
    tipo_row = tipo_result.first()
    
    if not tipo_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user type: {request.tipo}"
        )
    
    tipo_usuario_id = tipo_row[0]
    
    # Hash password with bcrypt
    hashed_password = get_password_hash(request.password)
    
    # Create user
    user_id = uuid_lib.uuid4()
    
    insert_user = text("""
        INSERT INTO auth.usuario (id, tipo_usuario_id, email, password_hash, activo, created_at, updated_at)
        VALUES (:id, :tipo_usuario_id, :email, :password_hash, true, NOW(), NOW())
        RETURNING id
    """)
    
    await db.execute(insert_user, {
        "id": user_id,
        "tipo_usuario_id": tipo_usuario_id,
        "email": request.email,
        "password_hash": hashed_password
    })
    
    # Create profile
    insert_perfil = text("""
        INSERT INTO auth.perfil_general (id, usuario_id, nombre, apellido, telefono, created_at)
        VALUES (gen_random_uuid(), :usuario_id, :nombre, :apellido, :telefono, NOW())
    """)
    
    await db.execute(insert_perfil, {
        "usuario_id": user_id,
        "nombre": request.nombre,
        "apellido": request.apellido,
        "telefono": request.telefono
    })
    
    # If user is pasajero, create wallet automatically
    if request.tipo == "pasajero":
        insert_wallet = text("""
            INSERT INTO payment.billetera (id, usuario_id, saldo, moneda, created_at, updated_at)
            VALUES (gen_random_uuid(), :usuario_id, 0, 'ARS', NOW(), NOW())
            ON CONFLICT (usuario_id) DO NOTHING
        """)
        await db.execute(insert_wallet, {"usuario_id": user_id})
    
    await db.commit()
    
    return RegistroResponse(
        success=True,
        user_id=user_id,
        email=request.email,
        message=f"Usuario {request.tipo} registrado exitosamente"
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens (access + refresh)
    Uses bcrypt password verification
    Incluye validaciones de suspensión:
    - Usuario no suspendido
    - Tenant activo (si aplica)
    - Empresa activa (si es empleado)
    """
    
    # Get user by email
    query = text("""
        SELECT u.id, u.email, u.password_hash, u.control_base_id, tu.nombre as tipo_usuario,
               COALESCE(p.nombre || ' ' || p.apellido, u.email) as nombre_completo
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE u.email = :email AND u.activo = true
    """)
    
    result = await db.execute(query, {"email": request.email})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user_id, email, password_hash, control_base_id, tipo_usuario, nombre_completo = row
    
    # Verify password with bcrypt
    if not verify_password(request.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # ============================================
    # VALIDACIONES DE SUSPENSIÓN
    # ============================================
    
    # 1. Validar que el usuario no esté suspendido
    await validar_usuario_activo(user_id, db)
    
    # 2. Si es empleado, validar empresa y tenant
    if tipo_usuario.lower() == "empleado":
        empresa_validacion = await validar_tenant_y_empresa_para_empleado(user_id, db)
    
    # 3. Si es admin (tenant), validar tenant
    elif tipo_usuario.lower() == "admin" and control_base_id:
        await validar_tenant_activo(control_base_id, db)
    
    # 4. Si es pasajero o chofer con tenant, validar tenant
    elif control_base_id:
        await validar_tenant_activo(control_base_id, db)
    
    # 5. Super Admin (admin sin control_base_id) no tiene tenant que validar
    
    # ============================================
    # CREACIÓN DE TOKENS
    # ============================================
    
    # Create tokens
    token_data = {"sub": str(user_id), "email": email, "tipo": tipo_usuario}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store refresh token in database
    store_refresh = text("""
        INSERT INTO auth.refresh_token (id, usuario_id, token, expiracion, created_at)
        VALUES (gen_random_uuid(), :user_id, :token, NOW() + INTERVAL '7 days', NOW())
        ON CONFLICT (usuario_id, token) DO NOTHING
    """)
    
    await db.execute(store_refresh, {
        "user_id": user_id,
        "token": refresh_token
    })
    
    await db.commit()
    
    # ✅ MODIFICADO: Agregar control_base_id en la respuesta
    return LoginResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        email=email,
        tipo_usuario=tipo_usuario,
        nombre_completo=nombre_completo,
        control_base_id=str(control_base_id) if control_base_id else None  # ✅ NUEVO
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get new access token using refresh token
    """
    
    payload = decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify refresh token exists in database
    verify_query = text("""
        SELECT id FROM auth.refresh_token
        WHERE token = :token AND expiracion > NOW()
    """)
    
    result = await db.execute(verify_query, {"token": request.refresh_token})
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid"
        )
    
    # Get user data - CORREGIDO: u.id en lugar de id
    user_query = text("""
        SELECT u.id, u.email, tu.nombre as tipo_usuario
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        WHERE u.id = :user_id AND u.activo = true
    """)
    
    user_result = await db.execute(user_query, {"user_id": UUID(user_id_str)})
    user_row = user_result.first()
    
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Validar que el usuario no esté suspendido antes de refrescar token
    await validar_usuario_activo(user_row[0], db)
    
    new_token_data = {"sub": str(user_row[0]), "email": user_row[1], "tipo": user_row[2]}
    new_access_token = create_access_token(new_token_data)
    
    return RefreshTokenResponse(access_token=new_access_token)


@router.post("/logout")
async def logout(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Invalidate refresh token (logout)
    """
    user_id = current_user[0]
    
    # Delete all refresh tokens for this user
    delete_query = text("DELETE FROM auth.refresh_token WHERE usuario_id = :user_id")
    await db.execute(delete_query, {"user_id": user_id})
    await db.commit()
    
    return {"success": True, "message": "Logged out successfully"}


@router.post("/recuperar-solicitar", response_model=RecuperarConfirmarResponse)
async def solicitar_recuperacion(
    request: RecuperarSolicitarRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password recovery email
    """
    
    # Check if user exists
    query = text("""
        SELECT id, email FROM auth.usuario
        WHERE email = :email AND activo = true
    """)
    
    result = await db.execute(query, {"email": request.email})
    row = result.first()
    
    if not row:
        # Don't reveal if email exists or not (security)
        return RecuperarConfirmarResponse(
            success=True,
            message="Si el email existe, recibirás un enlace de recuperación"
        )
    
    user_id = row[0]
    
    # Validar que el usuario no esté suspendido (no puede recuperar si está suspendido)
    await validar_usuario_activo(user_id, db)
    
    # Generate reset token
    reset_token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Store reset token
    insert_token = text("""
        INSERT INTO auth.reset_token (id, usuario_id, token, expiracion, usado, created_at)
        VALUES (gen_random_uuid(), :user_id, :token, :expiracion, false, NOW())
        ON CONFLICT (usuario_id, token) DO NOTHING
    """)
    
    await db.execute(insert_token, {
        "user_id": user_id,
        "token": reset_token,
        "expiracion": expires_at
    })
    
    await db.commit()
    
    # Send email
    await send_password_recovery_email(request.email, reset_token)
    
    return RecuperarConfirmarResponse(
        success=True,
        message="Email de recuperación enviado. Revisa tu bandeja de entrada."
    )


@router.post("/recuperar-confirmar", response_model=RecuperarConfirmarResponse)
async def confirmar_recuperacion(
    request: RecuperarConfirmarRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm password recovery with token and set new password
    """
    
    # Validate token
    query = text("""
        SELECT usuario_id, expiracion, usado
        FROM auth.reset_token
        WHERE token = :token
    """)
    
    result = await db.execute(query, {"token": request.token})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )
    
    user_id, expiracion, usado = row
    
    if usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token ya utilizado"
        )
    
    if datetime.utcnow() > expiracion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )
    
    # Validar que el usuario no esté suspendido (no puede cambiar contraseña si está suspendido)
    await validar_usuario_activo(user_id, db)
    
    # Hash new password with bcrypt
    new_password_hash = get_password_hash(request.new_password)
    
    # Update user password
    update_query = text("""
        UPDATE auth.usuario
        SET password_hash = :password_hash, updated_at = NOW()
        WHERE id = :user_id
    """)
    
    await db.execute(update_query, {
        "password_hash": new_password_hash,
        "user_id": user_id
    })
    
    # Mark token as used
    mark_used = text("UPDATE auth.reset_token SET usado = true WHERE token = :token")
    await db.execute(mark_used, {"token": request.token})
    
    # Delete all refresh tokens (force re-login)
    delete_refresh = text("DELETE FROM auth.refresh_token WHERE usuario_id = :user_id")
    await db.execute(delete_refresh, {"user_id": user_id})
    
    await db.commit()
    
    return RecuperarConfirmarResponse(
        success=True,
        message="Contraseña actualizada exitosamente. Ya puedes iniciar sesión."
    )


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user information
    Returns user details including profile, permissions, and tenant
    """
    user_id, control_base_id, email, tipo_usuario = current_user
    
    # Get user profile
    profile_query = text("""
        SELECT nombre, apellido, telefono, documento, foto_perfil_url
        FROM auth.perfil_general
        WHERE usuario_id = :user_id
    """)
    
    profile_result = await db.execute(profile_query, {"user_id": user_id})
    profile_row = profile_result.first()
    
    perfil = None
    if profile_row:
        nombre, apellido, telefono, documento, foto_perfil_url = profile_row
        perfil = {
            "nombre": nombre,
            "apellido": apellido,
            "telefono": telefono,
            "documento": documento,
            "foto_perfil_url": foto_perfil_url
        }
    
    # Get control_base info (tenant)
    tenant = None
    if control_base_id:
        tenant_query = text("""
            SELECT nombre, email, telefono
            FROM tenant.control_base
            WHERE id = :control_base_id
        """)
        
        tenant_result = await db.execute(tenant_query, {"control_base_id": control_base_id})
        tenant_row = tenant_result.first()
        
        if tenant_row:
            tenant = {
                "nombre": tenant_row[0],
                "email": tenant_row[1],
                "telefono": tenant_row[2]
            }
    
    return UserMeResponse(
        id=str(user_id),
        email=email,
        tipo_usuario=tipo_usuario,
        control_base_id=str(control_base_id) if control_base_id else None,
        perfil=perfil,
        tenant=tenant
    )


@router.put("/cambiar-contrasenia", response_model=CambiarContraseniaResponse)
async def cambiar_contrasenia(
    request: CambiarContraseniaRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for authenticated user
    """
    user_id = current_user[0]
    
    # Validar que el usuario no esté suspendido
    await validar_usuario_activo(user_id, db)
    
    # Get current password hash
    query = text("SELECT password_hash FROM auth.usuario WHERE id = :user_id")
    result = await db.execute(query, {"user_id": user_id})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    current_hash = row[0]
    
    # Verify current password
    if not verify_password(request.current_password, current_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Hash new password
    new_hash = get_password_hash(request.new_password)
    
    # Update password
    update_query = text("""
        UPDATE auth.usuario
        SET password_hash = :new_hash, updated_at = NOW()
        WHERE id = :user_id
    """)
    
    await db.execute(update_query, {
        "new_hash": new_hash,
        "user_id": user_id
    })
    
    # Delete all refresh tokens (force re-login)
    delete_refresh = text("DELETE FROM auth.refresh_token WHERE usuario_id = :user_id")
    await db.execute(delete_refresh, {"user_id": user_id})
    
    await db.commit()
    
    return CambiarContraseniaResponse(
        success=True,
        message="Contraseña cambiada exitosamente. Por favor inicia sesión nuevamente."
    )


# ============================================
# Helper: Log owner login attempts
# ============================================

async def _log_owner_login_attempt(
    db: AsyncSession,
    usuario_id: Optional[UUID],
    ip_address: str,
    success: bool,
    reason: str = None,
    vehiculos_count: int = 0
):
    """Log owner login attempts for audit (silent fail if table doesn't exist)"""
    try:
        # Check if audit table exists (simple way)
        check_table = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'audit' AND table_name = 'log_accesos_propietarios'
            )
        """)
        exists_result = await db.execute(check_table)
        table_exists = exists_result.scalar()
        
        if table_exists:
            log_query = text("""
                INSERT INTO audit.log_accesos_propietarios 
                (id, usuario_id, ip_address, success, reason, vehiculos_count, created_at)
                VALUES (gen_random_uuid(), :usuario_id, :ip_address, :success, :reason, :vehiculos_count, NOW())
            """)
            await db.execute(log_query, {
                "usuario_id": usuario_id,
                "ip_address": ip_address,
                "success": success,
                "reason": reason,
                "vehiculos_count": vehiculos_count
            })
    except Exception as e:
        # Silent fail - don't break login flow if logging fails
        print(f"Warning: Could not log owner login attempt: {e}")


# ============================================
# OWNER (PROPIETARIO) LOGIN
# ============================================

@router.post("/propietarios/login", response_model=PropietarioLoginResponse)
async def login_propietario(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    request_fastapi: Request = None
):
    """
    Exclusive login for owners (propietarios)
    
    Validates:
    1. Credentials (email/password)
    2. User has role 'propietario'
    3. User has at least one active vehicle in fleet.propietario_vehiculo
    4. User is active and not suspended
    5. Tenant is active (if applicable)
    
    Returns JWT tokens with owner data
    """
    
    # Get client IP for audit
    client_ip = "unknown"
    if request_fastapi and hasattr(request_fastapi, 'client') and request_fastapi.client:
        client_ip = request_fastapi.client.host
    
    # 1. Get user by email with tipo_usuario
    query = text("""
        SELECT u.id, u.email, u.password_hash, u.control_base_id, u.activo,
               tu.nombre as tipo_usuario,
               COALESCE(p.nombre || ' ' || p.apellido, u.email) as nombre_completo
        FROM auth.usuario u
        JOIN auth.tipo_usuario tu ON u.tipo_usuario_id = tu.id
        LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
        WHERE u.email = :email
    """)
    
    result = await db.execute(query, {"email": request.email})
    row = result.first()
    
    # 2. Validate user exists
    if not row:
        await _log_owner_login_attempt(db, None, client_ip, False, "User not found")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    user_id, email, password_hash, control_base_id, activo, tipo_usuario, nombre_completo = row
    
    # 3. Validate password
    if not verify_password(request.password, password_hash):
        await _log_owner_login_attempt(db, user_id, client_ip, False, "Invalid password")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # 4. Validate user is active
    if not activo:
        await _log_owner_login_attempt(db, user_id, client_ip, False, "User inactive")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    # ============================================
    # VALIDACIONES DE SUSPENSIÓN PARA PROPIETARIO
    # ============================================
    
    # 5. Validar que el usuario no esté suspendido
    await validar_usuario_activo(user_id, db)
    
    # 6. Validar tenant del propietario
    if control_base_id:
        await validar_tenant_activo(control_base_id, db)
    
    # 7. Validate role is 'propietario'
    if tipo_usuario.lower() != "propietario":
        await _log_owner_login_attempt(db, user_id, client_ip, False, f"Invalid role: {tipo_usuario}")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo para propietarios. No tienes permisos de propietario."
        )
    
    # 8. Get active vehicles for this owner (max 10)
    vehicles_query = text("""
        SELECT 
            v.id,
            v.patente,
            v.marca,
            v.modelo,
            v.anio,
            COALESCE(pv.porcentaje_participacion, 100) as porcentaje_participacion,
            pv.fecha_inicio::text as fecha_inicio
        FROM fleet.propietario_vehiculo pv
        JOIN fleet.vehiculo v ON v.id = pv.vehiculo_id
        WHERE pv.propietario_id = :owner_id
            AND pv.activo = true
            AND (pv.fecha_fin IS NULL OR pv.fecha_fin > NOW())
            AND v.activo = true
        ORDER BY pv.fecha_inicio DESC
        LIMIT 10
    """)
    
    vehicles_result = await db.execute(vehicles_query, {"owner_id": user_id})
    vehicles = vehicles_result.fetchall()
    total_vehiculos = len(vehicles)
    tiene_vehiculos_activos = total_vehiculos > 0
    
    # 9. Validate has at least one active vehicle
    if not tiene_vehiculos_activos:
        await _log_owner_login_attempt(db, user_id, client_ip, False, "No active vehicles", total_vehiculos)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes vehículos activos registrados. Contacta con el administrador."
        )
    
    # 10. Create JWT tokens with owner-specific claims
    token_data = {
        "sub": str(user_id),
        "email": email,
        "tipo": tipo_usuario,
        "control_base_id": str(control_base_id) if control_base_id else None,
        "total_vehiculos": total_vehiculos
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # 11. Store refresh token in database
    store_refresh = text("""
        INSERT INTO auth.refresh_token (id, usuario_id, token, expiracion, created_at)
        VALUES (gen_random_uuid(), :user_id, :token, NOW() + INTERVAL '7 days', NOW())
        ON CONFLICT (usuario_id, token) DO NOTHING
    """)
    
    await db.execute(store_refresh, {
        "user_id": user_id,
        "token": refresh_token
    })
    
    # 12. Log successful login
    await _log_owner_login_attempt(db, user_id, client_ip, True, "Success", total_vehiculos)
    await db.commit()
    
    # Prepare vehicles summary for response (max 10 as per LIMIT)
    vehiculos_summary = [
        {
            "id": v[0],
            "patente": v[1],
            "marca": v[2],
            "modelo": v[3],
            "anio": v[4],
            "porcentaje_participacion": float(v[5]),
            "fecha_inicio": v[6]
        }
        for v in vehicles
    ]
    
    return PropietarioLoginResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        email=email,
        tipo_usuario=tipo_usuario,
        nombre_completo=nombre_completo,
        control_base_id=control_base_id,
        tiene_vehiculos_activos=True,
        total_vehiculos=total_vehiculos,
        vehiculos=vehiculos_summary if vehiculos_summary else None
    )