"""
Authentication routes: register, login, refresh, password recovery
Incluye validaciones de suspensión a nivel Tenant, Empresa y Usuario
Incluye endpoints forenses para auditoría y requerimientos judiciales
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, timedelta
import uuid as uuid_lib
from typing import Optional
import json

from app.database import get_db
from app.dependencies import get_current_user, get_current_forense_user
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
    PropietarioLoginResponse,
    RegistroPropietarioRequest,
    RegistroPropietarioResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================
# REGISTRO GENÉRICO
# ============================================

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


# ============================================
# REGISTRO DE PROPIETARIO
# ============================================

@router.post("/registro/propietario", response_model=RegistroPropietarioResponse)
async def registrar_propietario(
    request: RegistroPropietarioRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registro de un nuevo propietario con selección de ciudad.
    - Valida que la ciudad exista y tenga tenant activo
    - Asigna control_base_id = tenant asociado a la ciudad
    - Crea usuario, perfil y wallet
    - Opcionalmente: agrega capacidad CONDUCTOR si registrar_como_conductor = True
    """
    
    print("=" * 60)
    print("🔍 [REGISTRO PROPIETARIO] INICIANDO REGISTRO")
    print(f"📧 Email: {request.email}")
    print(f"🏙️ Ciudad ID: {request.ciudad_id}")
    print(f"🚗 Registrar como conductor: {request.registrar_como_conductor}")
    print("=" * 60)
    
    # 1. Validar email único
    print("📌 [PASO 1] Verificando email único...")
    check_email = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(check_email, {"email": request.email})
    if result.first():
        print("❌ [PASO 1] Email ya registrado:", request.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    print("✅ [PASO 1] Email disponible")
    
    # 2. Validar que la ciudad existe y tiene tenant activo
    print("📌 [PASO 2] Validando ciudad y tenant...")
    ciudad_query = text("""
        SELECT 
            c.id as ciudad_id,
            c.nombre as ciudad_nombre,
            cb.id as tenant_id,
            cb.nombre as tenant_nombre
        FROM geo.ciudad c
        INNER JOIN tenant.control_base cb ON cb.ciudad_id = c.id
        WHERE c.id = :ciudad_id AND cb.activo = true
    """)
    
    result = await db.execute(ciudad_query, {"ciudad_id": request.ciudad_id})
    ciudad_row = result.first()
    
    if not ciudad_row:
        print("❌ [PASO 2] Ciudad no encontrada o sin tenant activo:", request.ciudad_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La ciudad seleccionada no está disponible o no tiene un tenant activo"
        )
    
    ciudad_id = ciudad_row[0]
    ciudad_nombre = ciudad_row[1]
    tenant_id = ciudad_row[2]
    tenant_nombre = ciudad_row[3]
    print(f"✅ [PASO 2] Ciudad válida: {ciudad_nombre} (ID: {ciudad_id})")
    print(f"✅ [PASO 2] Tenant asociado: {tenant_nombre} (ID: {tenant_id})")
    
    # 3. Obtener ID del tipo 'propietario'
    print("📌 [PASO 3] Obteniendo tipo de usuario 'propietario'...")
    tipo_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'propietario'")
    result = await db.execute(tipo_query)
    tipo_row = result.first()
    
    if not tipo_row:
        print("❌ [PASO 3] Tipo 'propietario' no encontrado")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de usuario 'propietario' no encontrado"
        )
    
    tipo_propietario_id = tipo_row[0]
    print(f"✅ [PASO 3] Tipo propietario encontrado (ID: {tipo_propietario_id})")
    
    # 3b. Obtener ID del tipo 'chofer' (para capacidad adicional)
    tipo_chofer_query = text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer'")
    result = await db.execute(tipo_chofer_query)
    tipo_chofer_row = result.first()
    tipo_chofer_id = tipo_chofer_row[0] if tipo_chofer_row else None
    
    if request.registrar_como_conductor and not tipo_chofer_id:
        print("⚠️ [PASO 3b] Tipo 'chofer' no encontrado, no se puede agregar capacidad")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de usuario 'chofer' no encontrado para agregar capacidad"
        )
    
    # 4. Hash de la contraseña
    print("📌 [PASO 4] Generando hash de contraseña...")
    password_hash = get_password_hash(request.password)
    print("✅ [PASO 4] Hash generado correctamente")
    
    # 5. Crear usuario
    print("📌 [PASO 5] Creando usuario en la base de datos...")
    user_id = uuid_lib.uuid4()
    print(f"🆔 User ID generado: {user_id}")
    
    try:
        # 5a. Insertar usuario
        insert_user = text("""
            INSERT INTO auth.usuario (
                id, control_base_id, tipo_usuario_id, email, password_hash, activo, created_at, updated_at
            )
            VALUES (
                :id, :tenant_id, :tipo_usuario_id, :email, :password_hash, true, NOW(), NOW()
            )
        """)
        
        await db.execute(insert_user, {
            "id": user_id,
            "tenant_id": tenant_id,
            "tipo_usuario_id": tipo_propietario_id,
            "email": request.email,
            "password_hash": password_hash
        })
        print("✅ [PASO 5a] Usuario creado correctamente")
        
        # 5b. Crear perfil
        print("📌 [PASO 5b] Creando perfil del usuario...")
        insert_perfil = text("""
            INSERT INTO auth.perfil_general (
                id, usuario_id, nombre, apellido, telefono, ciudad_id, created_at
            )
            VALUES (
                gen_random_uuid(), :usuario_id, :nombre, :apellido, :telefono, :ciudad_id, NOW()
            )
        """)
        
        await db.execute(insert_perfil, {
            "usuario_id": user_id,
            "nombre": request.nombre,
            "apellido": request.apellido,
            "telefono": request.telefono,
            "ciudad_id": ciudad_id
        })
        print("✅ [PASO 5b] Perfil creado correctamente")
        
        # 5c. Crear wallet
        print("📌 [PASO 5c] Creando wallet (billetera)...")
        insert_wallet = text("""
            INSERT INTO payment.billetera (id, usuario_id, saldo, moneda, created_at, updated_at)
            VALUES (gen_random_uuid(), :usuario_id, 0, 'ARS', NOW(), NOW())
            ON CONFLICT (usuario_id) DO NOTHING
        """)
        
        await db.execute(insert_wallet, {"usuario_id": user_id})
        print("✅ [PASO 5c] Wallet creada correctamente")
        
        # 5d. Si checkbox activado, agregar capacidad CONDUCTOR
        if request.registrar_como_conductor and tipo_chofer_id:
            print("📌 [PASO 5d] Agregando capacidad CONDUCTOR...")
            insert_capacidad = text("""
                INSERT INTO auth.usuario_rol (
                    id, usuario_id, tipo_usuario_id, activo, fecha_inicio, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :usuario_id, :tipo_chofer_id, true, CURRENT_DATE, NOW(), NOW()
                )
                ON CONFLICT (usuario_id, tipo_usuario_id) DO NOTHING
            """)
            
            await db.execute(insert_capacidad, {
                "usuario_id": user_id,
                "tipo_chofer_id": tipo_chofer_id
            })
            print("✅ [PASO 5d] Capacidad CONDUCTOR agregada correctamente")
        
        await db.commit()
        print("💾 [COMMIT] Transacción completada exitosamente")
        
    except Exception as e:
        print(f"❌ [ERROR] Falló la transacción: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar propietario: {str(e)}"
        )
    
    print("=" * 60)
    print("✅ [REGISTRO PROPIETARIO] REGISTRO EXITOSO")
    print(f"👤 Usuario: {request.email}")
    print(f"🏙️ Ciudad: {ciudad_nombre}")
    print(f"🏢 Tenant: {tenant_nombre}")
    if request.registrar_como_conductor:
        print("🚗 Capacidad CONDUCTOR: ACTIVADA")
    print("=" * 60)
    
    return RegistroPropietarioResponse(
        success=True,
        user_id=user_id,
        email=request.email,
        ciudad_id=ciudad_id,
        ciudad_nombre=ciudad_nombre,
        tenant_id=tenant_id,
        tenant_nombre=tenant_nombre,
        message="Propietario registrado exitosamente",
        first_login=True,
        registrado_como_conductor=request.registrar_como_conductor
    )


# ============================================
# LOGIN
# ============================================

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
    
    return LoginResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        email=email,
        tipo_usuario=tipo_usuario,
        nombre_completo=nombre_completo,
        control_base_id=str(control_base_id) if control_base_id else None
    )


# ============================================
# REFRESH TOKEN
# ============================================

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
    
    # Get user data
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


# ============================================
# LOGOUT
# ============================================

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


# ============================================
# RECUPERACIÓN DE CONTRASEÑA
# ============================================

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


# ============================================
# GET /me - Current user info
# ============================================

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


# ============================================
# CAMBIAR CONTRASEÑA
# ============================================

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
# HELPER: LOG FORENSE
# ============================================

async def _log_forense_attempt(
    db: AsyncSession,
    usuario_id: Optional[UUID],
    ip_address: str,
    success: bool,
    reason: str = None
):
    """Log forensic login attempts to audit.log_acciones"""
    try:
        # Obtener email del usuario si existe
        email = "unknown"
        if usuario_id:
            email_query = text("SELECT email FROM auth.usuario WHERE id = :user_id")
            email_result = await db.execute(email_query, {"user_id": usuario_id})
            email_row = email_result.first()
            if email_row:
                email = email_row[0]
        
        log_query = text("""
            INSERT INTO audit.log_acciones 
            (id, usuario_id, email, accion, tabla_afectada, datos_anteriores, datos_nuevos, ip_address, created_at)
            VALUES (
                gen_random_uuid(), 
                :usuario_id, 
                :email, 
                'LOGIN_FORENSE', 
                'auth.login.forense', 
                NULL, 
                jsonb_build_object('success', :success, 'reason', :reason, 'ip', :ip_address),
                :ip_address, 
                NOW()
            )
        """)
        await db.execute(log_query, {
            "usuario_id": usuario_id,
            "email": email,
            "success": success,
            "reason": reason,
            "ip_address": ip_address
        })
    except Exception as e:
        # Silent fail - no romper el login si falla el log
        print(f"Warning: Could not log forensic attempt: {e}")


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
        await _log_forense_attempt(db, None, client_ip, False, "User not found")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    user_id, email, password_hash, control_base_id, activo, tipo_usuario, nombre_completo = row
    
    # 3. Validate password
    if not verify_password(request.password, password_hash):
        await _log_forense_attempt(db, user_id, client_ip, False, "Invalid password")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # 4. Validate user is active
    if not activo:
        await _log_forense_attempt(db, user_id, client_ip, False, "User inactive")
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
        await _log_forense_attempt(db, user_id, client_ip, False, f"Invalid role: {tipo_usuario}")
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
        await _log_forense_attempt(db, user_id, client_ip, False, "No active vehicles", total_vehiculos)
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
    await _log_forense_attempt(db, user_id, client_ip, True, "Success", total_vehiculos)
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


# ============================================
# ENDPOINTS FORENSES
# ============================================

@router.post("/forense/login", response_model=LoginResponse)
async def login_forense(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    request_fastapi: Request = None
):
    """
    Exclusive login for forensic roles (forense_tenant and forense_maestro)
    - Registra automáticamente el acceso en audit.log_acciones
    - forense_tenant: solo ve datos de su tenant
    - forense_maestro: ve datos de TODOS los tenants
    """
    
    # Get client IP
    client_ip = "unknown"
    if request_fastapi and hasattr(request_fastapi, 'client') and request_fastapi.client:
        client_ip = request_fastapi.client.host
    
    # Get user by email
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
    
    if not row:
        await _log_forense_attempt(db, None, client_ip, False, "User not found")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    user_id, email, password_hash, control_base_id, activo, tipo_usuario, nombre_completo = row
    
    # Verify password
    if not verify_password(request.password, password_hash):
        await _log_forense_attempt(db, user_id, client_ip, False, "Invalid password")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # Validate user is active
    if not activo:
        await _log_forense_attempt(db, user_id, client_ip, False, "User inactive")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    # Validar que el usuario no esté suspendido
    await validar_usuario_activo(user_id, db)
    
    # ============================================
    # VALIDAR ROL FORENSE
    # ============================================
    
    # Verificar que el usuario tiene rol forense (tenant o maestro)
    forense_query = text("""
        SELECT ur.id, ur.control_base_id, tu.nombre as rol_nombre
        FROM auth.usuario_rol ur
        JOIN auth.tipo_usuario tu ON ur.tipo_usuario_id = tu.id
        WHERE ur.usuario_id = :user_id
          AND ur.activo = true
          AND (tu.nombre = 'forense_tenant' OR tu.nombre = 'forense_maestro')
          AND (ur.fecha_fin IS NULL OR ur.fecha_fin > NOW())
        LIMIT 1
    """)
    
    forense_result = await db.execute(forense_query, {"user_id": user_id})
    forense_row = forense_result.first()
    
    if not forense_row:
        await _log_forense_attempt(db, user_id, client_ip, False, "No tiene rol forense")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo para roles forenses"
        )
    
    forense_rol_id = forense_row[0]
    forense_control_base_id = forense_row[1]
    forense_rol_nombre = forense_row[2]
    
    # Si es forense_tenant, validar que tenga control_base_id asignado
    if forense_rol_nombre == 'forense_tenant' and not forense_control_base_id:
        await _log_forense_attempt(db, user_id, client_ip, False, "forense_tenant sin tenant asignado")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol forense_tenant sin tenant asignado"
        )
    
    # Si es forense_maestro, puede tener NULL o cualquier tenant
    # Validar tenant si tiene uno asignado
    if forense_control_base_id:
        await validar_tenant_activo(forense_control_base_id, db)
    
    # ============================================
    # CREAR TOKENS CON DATOS FORENSES
    # ============================================
    
    token_data = {
        "sub": str(user_id),
        "email": email,
        "tipo": tipo_usuario,
        "rol_forense": forense_rol_nombre,
        "control_base_id": str(forense_control_base_id) if forense_control_base_id else None,
        "es_maestro": forense_rol_nombre == 'forense_maestro'
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store refresh token
    store_refresh = text("""
        INSERT INTO auth.refresh_token (id, usuario_id, token, expiracion, created_at)
        VALUES (gen_random_uuid(), :user_id, :token, NOW() + INTERVAL '7 days', NOW())
        ON CONFLICT (usuario_id, token) DO NOTHING
    """)
    
    await db.execute(store_refresh, {
        "user_id": user_id,
        "token": refresh_token
    })
    
    # ============================================
    # REGISTRAR EN AUDITORÍA
    # ============================================
    
    await _log_forense_attempt(db, user_id, client_ip, True, f"Login exitoso como {forense_rol_nombre}")
    await db.commit()
    
    return LoginResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        email=email,
        tipo_usuario=forense_rol_nombre,
        nombre_completo=nombre_completo,
        control_base_id=str(forense_control_base_id) if forense_control_base_id else None
    )


@router.post("/forense/log")
async def log_forense_action(
    request: dict,
    current_user: tuple = Depends(get_current_forense_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar acción forense en audit.log_acciones
    Usado por el frontend para auditar todas las consultas forenses
    """
    user_id, control_base_id, email, rol_nombre, es_maestro = current_user
    
    accion = request.get("accion")
    tabla_afectada = request.get("tabla_afectada")
    registro_id = request.get("registro_id")
    detalles = request.get("detalles")
    
    if not accion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'accion' es obligatorio"
        )
    
    log_query = text("""
        INSERT INTO audit.log_acciones 
        (id, usuario_id, email, accion, tabla_afectada, registro_id, datos_nuevos, ip_address, created_at)
        VALUES (
            gen_random_uuid(), 
            :usuario_id, 
            :email, 
            :accion, 
            :tabla_afectada, 
            :registro_id, 
            :detalles::jsonb,
            :ip_address,
            NOW()
        )
    """)
    
    # Obtener IP del request
    ip_address = request.get("ip_address", "unknown")
    
    await db.execute(log_query, {
        "usuario_id": user_id,
        "email": email,
        "accion": accion,
        "tabla_afectada": tabla_afectada,
        "registro_id": registro_id,
        "detalles": json.dumps(detalles) if detalles else "{}",
        "ip_address": ip_address
    })
    
    await db.commit()
    
    return {"success": True, "message": "Acción registrada en auditoría"}