"""
Chofer self-registration endpoints - MÓDULO 1: FUNDACIÓN Y AUTENTICACIÓN
Flujo progresivo de 5 etapas sin vehículo ni contrato inicial.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import uuid4, UUID
from datetime import date, timedelta
from typing import Optional, List
import random

from app.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.services.email_validation import email_validator
from app.dependencies import get_current_user
from pydantic import BaseModel, EmailStr, Field, field_validator

router = APIRouter(prefix="/api/chofer", tags=["Chofer Registro - Módulo 1"])

# ==========================================
# SCHEMAS ESPECÍFICOS MÓDULO 1
# ==========================================

class ChoferInicioRegistroRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class ChoferInicioRegistroResponse(BaseModel):
    success: bool
    message: str
    user_id: UUID
    requiere_validacion_email: bool = True

class ValidarEmailRequest(BaseModel):
    email: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')

class ValidarEmailResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"
    message: str
    user_id: UUID

class ActualizarDatosChoferRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido: str = Field(..., min_length=2, max_length=50)
    dni: str = Field(..., pattern=r'^\d{7,8}[A-Z]?$')
    telefono: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    prestadora_id: UUID
    direccion: str = Field(..., min_length=5)
    ciudad_id: UUID
    codigo_postal: str = Field(..., pattern=r'^[A-Za-z0-9\s-]{4,10}$')

class DatosChoferResponse(BaseModel):
    success: bool
    tenant_nombre: str
    pasos_completados: dict

class DocumentoChoferUploadRequest(BaseModel):
    tipo_documento: str = Field(..., pattern='^(dni|licencia|sanidad|buena_conducta)$')
    fecha_vencimiento: Optional[date] = None

class DocumentoChoferResponse(BaseModel):
    success: bool
    tipo_documento: str
    url: str
    documentos_pendientes: List[str]

class SelfieChoferRequest(BaseModel):
    foto_url: str = Field(..., description="URL segura de Cloudinary")

class FinalizarRegistroResponse(BaseModel):
    success: bool
    estado_aprobacion: str
    mensaje: str

class EstadoExpedienteResponse(BaseModel):
    estado_aprobacion: str
    motivo_rechazo: Optional[str] = None
    progreso_etapas: dict
    puede_operar: bool
    tenant_nombre: Optional[str] = None
    documentos_faltantes: List[str] = []

# ==========================================
# CONSTANTES DE VALIDACIÓN DOCUMENTAL
# ==========================================
TIPOS_DOC_CHOFER = ['dni', 'licencia', 'sanidad', 'buena_conducta']
DOC_BLOQUEANTES = ['licencia', 'sanidad', 'buena_conducta']

# ==========================================
# ETAPA 1: INICIO DE REGISTRO
# ==========================================
@router.post("/registro/iniciar", response_model=ChoferInicioRegistroResponse)
async def iniciar_registro_chofer(
    request: ChoferInicioRegistroRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea cuenta básica + expediente SIN vehículo.
    Valida formato/existencia de email y envía OTP.
    """
    # 1. Validar email (formato + existencia SMTP)
    val = email_validator.validate_email(request.email)
    if not val.get("valid"):
        raise HTTPException(400, detail=f"Email inválido: {val.get('reason')}")

    # 2. Verificar unicidad
    res = await db.execute(text("SELECT id FROM auth.usuario WHERE email = :e"), {"e": request.email})
    if res.first():
        raise HTTPException(400, detail="Email ya registrado")

    # 3. Obtener IDs base
    tipo_res = await db.execute(text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer'"))
    tipo_id = tipo_res.scalar_one_or_none()
    if not tipo_id: 
        raise HTTPException(500, "Tipo 'chofer' no encontrado en BD")

    # Tenant temporal (se corrige en Etapa 3 al elegir ciudad)
    cb_res = await db.execute(text("SELECT id FROM tenant.control_base LIMIT 1"))
    temp_cb_id = cb_res.scalar_one_or_none()
    if not temp_cb_id: 
        raise HTTPException(500, "No hay tenants configurados en el sistema")

    user_id = uuid4()
    
    # 4. Crear Usuario + Perfil Vacío + Expediente SIN vehículo
    await db.execute(text("""
        INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at, updated_at)
        VALUES (:id, :tipo, :cb, :email, :pass, true, NOW(), NOW())
    """), {
        "id": user_id, "tipo": tipo_id, "cb": temp_cb_id, 
        "email": request.email, "pass": get_password_hash(request.password)
    })

    await db.execute(text("""
        INSERT INTO auth.perfil_general (id, usuario_id, created_at, updated_at)
        VALUES (gen_random_uuid(), :uid, NOW(), NOW())
    """), {"uid": user_id})

    await db.execute(text("""
        INSERT INTO fleet.chofer_vehiculo (
            id, usuario_id, control_base_id, estado_laboral, estado_aprobacion, activo, created_at, updated_at
        )
        VALUES (gen_random_uuid(), :uid, :cb, 'fuera_servicio', 'pendiente', true, NOW(), NOW())
    """), {"uid": user_id, "cb": temp_cb_id})

    # 5. Generar y guardar OTP (6 dígitos, expira en 10 min)
    codigo = f"{random.randint(100000, 999999)}"
    await db.execute(text("""
      INSERT INTO auth.codigo_verificacion (usuario_id, codigo, tipo, expira_en, creado_en)
      VALUES (:uid, :cod, 'REGISTRO_CHOFER', NOW() + INTERVAL '10 minutes', NOW())
    """), {"uid": user_id, "cod": codigo})

    await db.commit()

    # 6. Enviar email (usando servicio existente o integración SMTP real)
    # NOTA: Aquí deberías llamar a tu servicio de envío de emails real.
    # Por ahora simulamos el éxito, pero en producción debe ser asíncrono y robusto.
    try:
        from app.core.email import send_verification_code_email
        await send_verification_code_email(request.email, codigo)
    except Exception as e:
        # En producción, podrías marcar el registro como "email_pendiente" 
        # o revertir la transacción si el envío es crítico.
        print(f"⚠️ Error enviando OTP a {request.email}: {str(e)}")

    return ChoferInicioRegistroResponse(
        success=True, 
        message="Cuenta creada. Revisa tu email para validar.", 
        user_id=user_id
    )


# ==========================================
# ETAPA 2: VALIDAR EMAIL Y OBTENER JWT
# ==========================================
@router.post("/registro/validar-email", response_model=ValidarEmailResponse)
async def validar_email_chofer(
    request: ValidarEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Valida código OTP. Si es correcto, emite JWT funcional.
    Solo después de esto el usuario puede acceder a las etapas 3-5.
    """
    # Buscar código válido, no usado y no expirado
    otp_res = await db.execute(text("""
        SELECT cv.id, cv.usuario_id, u.control_base_id 
        FROM auth.codigo_verificacion cv
        JOIN auth.usuario u ON u.id = cv.usuario_id
        WHERE cv.codigo = :cod 
          AND cv.usado = false 
          AND cv.expira_en > NOW()
          AND cv.tipo = 'REGISTRO_CHOFER'
        ORDER BY cv.creado_en DESC 
        LIMIT 1
    """), {"cod": request.codigo})
    
    row = otp_res.first()
    if not row:
        raise HTTPException(400, detail="Código inválido, expirado o ya utilizado")
    
    otp_id, user_id, control_base_id = row

    # Marcar como usado inmediatamente
    await db.execute(text("UPDATE auth.codigo_verificacion SET usado = true WHERE id = :oid"), {"oid": otp_id})
    await db.commit()

    # Emitir JWT funcional con claims necesarios
    token = create_access_token(data={
        "sub": str(user_id), 
        "tipo": "chofer", 
        "control_base_id": str(control_base_id)
    })
    
    return ValidarEmailResponse(
        success=True, 
        access_token=token, 
        user_id=user_id, 
        message="Email validado exitosamente"
    )


# ==========================================
# ETAPA 3: ACTUALIZAR DATOS PERSONALES + TENANT
# ==========================================
@router.put("/registro/datos-personales", response_model=DatosChoferResponse)
async def actualizar_datos_chofer(
    request: ActualizarDatosChoferRequest, 
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Completa perfil personal y asigna tenant automáticamente según ciudad.
    """
    user_id = current_user[0]

    # 1. Validar que la ciudad existe y obtener su tenant activo
    ciudad_res = await db.execute(text("""
        SELECT c.id, cb.id as tenant_id, cb.nombre as tenant_nom
        FROM geo.ciudad c 
        JOIN tenant.control_base cb ON cb.ciudad_id = c.id
        WHERE c.id = :cid AND cb.activo = true
    """), {"cid": request.ciudad_id})
    
    ciudad_row = ciudad_res.first()
    if not ciudad_row:
        raise HTTPException(400, detail="Ciudad no válida o sin tenant activo asociado")
    
    _, new_tenant_id, tenant_nombre = ciudad_row

    # 2. Actualizar perfil general (incluyendo prestadora/agencia)
    await db.execute(text("""
        UPDATE auth.perfil_general SET 
            nombre = :nom, 
            apellido = :ape, 
            documento = :dni, 
            telefono = :tel,
            agencia = (SELECT nombre FROM auth.prestadora_telefonica WHERE id = :pid),
            direccion = :dir, 
            ciudad_id = :cid, 
            codigo_postal = :cp, 
            updated_at = NOW()
        WHERE usuario_id = :uid
    """), {
        "nom": request.nombre, "ape": request.apellido, "dni": request.dni, 
        "tel": request.telefono, "pid": request.prestadora_id, 
        "dir": request.direccion, "cid": request.ciudad_id, 
        "cp": request.codigo_postal, "uid": user_id
    })

    # 3. Actualizar tenant en usuario y expediente chofer
    await db.execute(text("""
        UPDATE auth.usuario SET control_base_id = :tid, updated_at = NOW() WHERE id = :uid
    """), {"tid": new_tenant_id, "uid": user_id})
    
    await db.execute(text("""
        UPDATE fleet.chofer_vehiculo SET control_base_id = :tid, updated_at = NOW() WHERE usuario_id = :uid
    """), {"tid": new_tenant_id, "uid": user_id})
    
    await db.commit()

    return DatosChoferResponse(
        success=True, 
        tenant_nombre=tenant_nombre, 
        pasos_completados={"email": True, "datos": True}
    )


# ==========================================
# ETAPA 4: SUBIR DOCUMENTO INDIVIDUAL
# ==========================================
@router.post("/registro/documento", response_model=DocumentoChoferResponse)
async def subir_documento_chofer(
    file: UploadFile = File(...),
    tipo_documento: str = Query(..., description="dni, licencia, sanidad o buena_conducta"),
    fecha_vencimiento: Optional[date] = Query(None),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sube un documento específico. Valida tipos, obligatoriedad de fechas y vencimientos bloqueantes.
    """
    user_id = current_user[0]
    
    if tipo_documento not in TIPOS_DOC_CHOFER:
        raise HTTPException(400, detail=f"Tipo inválido. Permitidos: {TIPOS_DOC_CHOFER}")

    # Validaciones de vencimiento BLOQUEANTES (excepto DNI)
    if tipo_documento in DOC_BLOQUEANTES and not fecha_vencimiento:
        raise HTTPException(400, detail=f"Fecha de vencimiento obligatoria para {tipo_documento}")
    
    if fecha_vencimiento and fecha_vencimiento < date.today() and tipo_documento != 'dni':
        raise HTTPException(400, detail="El documento está vencido y no puede ser aceptado")

    # Subir a Cloudinary (ajusta el import según tu estructura real)
    try:
        from app.services.cloudinary_storage import cloudinary_storage
        url = await cloudinary_storage.upload_comprobante(
            file=file, 
            usuario_id=str(user_id), 
            tipo=tipo_documento
        )
    except Exception as e:
        raise HTTPException(500, detail=f"Error subiendo archivo a storage: {str(e)}")

    # Guardar/Actualizar en BD (UPSERT)
    await db.execute(text("""
        INSERT INTO fleet.documentos_chofer (usuario_id, tipo_documento, url, fecha_vencimiento, subido_en, activo)
        VALUES (:uid, :tipo, :url, :fv, NOW(), true)
        ON CONFLICT (usuario_id, tipo_documento) DO UPDATE 
        SET url = :url, fecha_vencimiento = :fv, subido_en = NOW(), activo = true
    """), {"uid": user_id, "tipo": tipo_documento, "url": url, "fv": fecha_vencimiento})

    await db.commit()

    # Calcular pendientes para feedback inmediato al frontend
    docs_existentes = await db.execute(text("""
        SELECT tipo_documento FROM fleet.documentos_chofer 
        WHERE usuario_id = :uid AND activo = true
    """), {"uid": user_id})
    existentes = {r[0] for r in docs_existentes.all()}
    pendientes = [d for d in TIPOS_DOC_CHOFER if d not in existentes]

    return DocumentoChoferResponse(
        success=True, 
        tipo_documento=tipo_documento, 
        url=url, 
        documentos_pendientes=pendientes
    )


# ==========================================
# ETAPA 5: SELFIE Y ENVÍO A REVISIÓN
# ==========================================
@router.post("/registro/selfie", response_model=FinalizarRegistroResponse)
async def registrar_selfie_chofer(
    request: SelfieChoferRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Guarda selfie dual (perfil + evidencia) y transiciona expediente a 'en_revision'.
    Valida completitud total antes de permitir este paso final.
    """
    user_id = current_user[0]

    # 1. Validar completitud total antes de permitir selfie final
    checks = await db.execute(text("""
        SELECT 
            (SELECT COUNT(*) FROM fleet.documentos_chofer WHERE usuario_id = :uid AND activo = true) as doc_count,
            (SELECT nombre FROM auth.perfil_general WHERE usuario_id = :uid) as tiene_datos
    """), {"uid": user_id})
    row = checks.first()
    
    if not row or row[1] is None or row[0] < 4:
        raise HTTPException(400, detail="Completa todos los datos personales y 4 documentos antes de la selfie")

    # 2. Guardar selfie dual (Perfil + Evidencia documental)
    await db.execute(text("""
        UPDATE auth.perfil_general SET foto_perfil_url = :url, updated_at = NOW() WHERE usuario_id = :uid
    """), {"url": request.foto_url, "uid": user_id})
    
    await db.execute(text("""
        INSERT INTO fleet.documentos_chofer (usuario_id, tipo_documento, url, subido_en, activo)
        VALUES (:uid, 'selfie', :url, NOW(), true)
        ON CONFLICT (usuario_id, tipo_documento) DO UPDATE SET url = :url, subido_en = NOW(), activo = true
    """), {"uid": user_id, "url": request.foto_url})

    # 3. Transicionar estado a EN_REVISION solo si estaba pendiente
    await db.execute(text("""
        UPDATE fleet.chofer_vehiculo 
        SET estado_aprobacion = 'en_revision', updated_at = NOW()
        WHERE usuario_id = :uid AND estado_aprobacion = 'pendiente'
    """), {"uid": user_id})

    await db.commit()

    return FinalizarRegistroResponse(
        success=True, 
        estado_aprobacion="en_revision", 
        mensaje="Expediente enviado correctamente a revisión administrativa"
    )


# ==========================================
# CONSULTA DE ESTADO / REANUDACIÓN
# ==========================================
@router.get("/registro/estado-expediente", response_model=EstadoExpedienteResponse)
async def obtener_estado_expediente(
    current_user: tuple = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve progreso completo, estado aprobación, motivos de rechazo y docs faltantes.
    Esencial para reanudación de registro tras login.
    """
    user_id = current_user[0]

    # Query consolidada de estado
    res = await db.execute(text("""
        SELECT 
            cv.estado_aprobacion, 
            cv.motivo_rechazo, 
            cv.estado_laboral,
            p.nombre IS NOT NULL as tiene_datos,
            p.foto_perfil_url IS NOT NULL as tiene_selfie,
            cb.nombre as tenant_nom,
            cv.vehiculo_id IS NOT NULL as tiene_vehiculo
        FROM fleet.chofer_vehiculo cv
        LEFT JOIN auth.perfil_general p ON p.usuario_id = cv.usuario_id
        LEFT JOIN tenant.control_base cb ON cb.id = cv.control_base_id
        WHERE cv.usuario_id = :uid
    """), {"uid": user_id})
    
    row = res.first()
    if not row: 
        raise HTTPException(404, detail="Expediente de chofer no encontrado")

    estado, motivo, lab, tiene_datos, tiene_selfie, tenant, tiene_vehiculo = row

    # Calcular progreso documental exacto
    docs_res = await db.execute(text("""
        SELECT tipo_documento FROM fleet.documentos_chofer 
        WHERE usuario_id = :uid AND activo = true
    """), {"uid": user_id})
    docs_subidos = {r[0] for r in docs_res.all()}
    
    faltantes = [d for d in TIPOS_DOC_CHOFER if d not in docs_subidos]
    if 'selfie' not in docs_subidos: 
        faltantes.append('selfie')

    # Regla de oro Módulo 2: Solo opera si está aprobado Y tiene vehículo Y turno libre
    puede_operar = (estado == 'aprobado') and tiene_vehiculo and (lab == 'libre')

    return EstadoExpedienteResponse(
        estado_aprobacion=estado,
        motivo_rechazo=motivo,
        progreso_etapas={
            "datos_personales": tiene_datos, 
            "documentos_basicos": len([d for d in TIPOS_DOC_CHOFER if d in docs_subidos]) >= 4, 
            "selfie": tiene_selfie
        },
        puede_operar=puede_operar,
        tenant_nombre=tenant,
        documentos_faltantes=faltantes
    )


# ==========================================
# ENDPOINT LEGACY (DEPRECATED)
# ==========================================
@router.post("/registro-completo", deprecated=True)
async def registrar_chofer_legacy(*args, **kwargs):
    """
    ️ DEPRECATED: Este endpoint está reservado exclusivamente para uso administrativo 
    o migraciones masivas donde ya se poseen todos los datos incluyendo vehículo.
    Para registro de choferes nuevos, usar /api/chofer/registro/iniciar
    """
    raise HTTPException(
        status_code=410, 
        detail="Endpoint obsoleto. Use el flujo progresivo /api/chofer/registro/iniciar"
    )