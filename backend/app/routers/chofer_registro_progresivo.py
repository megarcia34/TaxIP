"""
Router para el registro progresivo de choferes (Módulo 1).
Flujo: Inicio → Validar Email → Datos → Documentos → Selfie → En Revisión
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import uuid4, UUID
from datetime import date
from typing import Optional, List
import random
import logging

from app.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.services.email_validation import email_validator
from app.core.email_sender import email_sender
from app.dependencies import get_current_user
from app.schemas.chofer_registro_schemas import *

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chofer/registro-progresivo", tags=["Módulo 1 - Registro Progresivo"])

# Constantes de validación documental según Módulo 1
TIPOS_DOC_CHOFER = ['dni', 'licencia', 'sanidad', 'buena_conducta']
DOC_BLOQUEANTES = ['licencia', 'sanidad', 'buena_conducta']


# ==========================================
# ETAPA 1: INICIO DE REGISTRO
# ==========================================
@router.post("/iniciar", response_model=ChoferInicioRegistroResponse)
async def iniciar_registro_chofer(
    request: ChoferInicioRegistroRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crea cuenta básica + expediente SIN vehículo. Valida email y envía OTP."""
    logger.info(f"📝 Iniciando registro para email: {request.email}")
    
    # 1. Validar formato/existencia email con EmailValidator existente
    val = email_validator.validate_email(request.email)
    if not val.get("valid"):
        logger.warning(f"❌ Email inválido: {request.email} - {val.get('reason')}")
        raise HTTPException(400, detail=f"Email inválido: {val.get('reason')}")



       # 2. Verificar si el email ya existe
    res = await db.execute(text("""
        SELECT u.id, cv.estado_aprobacion
        FROM auth.usuario u
        LEFT JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id
        WHERE u.email = :e
    """), {"e": request.email})
    row = res.first()

    if row:
        user_id_existente, estado_aprobacion = row

        # Si el estado es 'pendiente' → REANUDAR registro
        if estado_aprobacion == 'pendiente':
            logger.info(f"🔄 Reanudando registro para email: {request.email}")
            
            # Generar nuevo OTP para reenviar
            codigo = f"{random.randint(100000, 999999)}"
            await db.execute(text("""
                INSERT INTO auth.codigo_verificacion (usuario_id, codigo, tipo, expira_en, creado_en)
                VALUES (:uid, :cod, 'REGISTRO_CHOFER', NOW() + INTERVAL '10 minutes', NOW())
            """), {"uid": user_id_existente, "cod": codigo})
            await db.commit()
            
            # Enviar email con nuevo código
            try:
                await email_sender.send_verification_code(request.email, codigo)
            except Exception as e:
                logger.error(f"❌ Error enviando email: {str(e)}")
            
            return ChoferInicioRegistroResponse(
                success=True,
                message="Ya tenías un registro en curso. Te enviamos un nuevo código.",
                user_id=user_id_existente,
                es_reanudacion=True
            )

        # Si está 'en_revision' → no permitir
        elif estado_aprobacion == 'en_revision':
            logger.warning(f"⚠️ Registro ya en revisión: {request.email}")
            raise HTTPException(
                400,
                detail="Ya tenés un registro en revisión. Esperá la aprobación del administrador."
            )

        # Si está 'aprobado' → ya es chofer
        elif estado_aprobacion == 'aprobado':
            logger.warning(f"⚠️ Chofer ya aprobado: {request.email}")
            raise HTTPException(
                400,
                detail="Ya estás registrado como chofer. Iniciá sesión."
            )

        # Si está 'rechazado' → permitir reintentar (crear nuevo registro)
        elif estado_aprobacion == 'rechazado':
            logger.info(f"🔄 Permitiendo reintentar registro para: {request.email}")
            # Eliminar el registro anterior para crear uno nuevo
            await db.execute(text("""
                DELETE FROM fleet.documentos_chofer WHERE usuario_id = :uid
            """), {"uid": user_id_existente})
            await db.execute(text("""
                DELETE FROM fleet.chofer_vehiculo WHERE usuario_id = :uid
            """), {"uid": user_id_existente})
            await db.execute(text("""
                DELETE FROM auth.perfil_general WHERE usuario_id = :uid
            """), {"uid": user_id_existente})
            await db.execute(text("""
                DELETE FROM auth.codigo_verificacion WHERE usuario_id = :uid
            """), {"uid": user_id_existente})
            await db.execute(text("""
                DELETE FROM auth.usuario WHERE id = :uid
            """), {"uid": user_id_existente})
            await db.commit()
            logger.info(f"🗑️ Registro anterior eliminado, creando nuevo...")

        # Si no tiene estado (perfil incompleto) → reanudar
        else:
            logger.info(f"🔄 Reanudando registro sin estado para: {request.email}")
            codigo = f"{random.randint(100000, 999999)}"
            await db.execute(text("""
                INSERT INTO auth.codigo_verificacion (usuario_id, codigo, tipo, expira_en, creado_en)
                VALUES (:uid, :cod, 'REGISTRO_CHOFER', NOW() + INTERVAL '10 minutes', NOW())
            """), {"uid": user_id_existente, "cod": codigo})
            await db.commit()

            try:
                await email_sender.send_verification_code(request.email, codigo)
            except Exception as e:
                logger.error(f"❌ Error enviando email: {str(e)}")

            return ChoferInicioRegistroResponse(
                success=True,
                message="Ya tenías un registro en curso. Te enviamos un nuevo código.",
                user_id=user_id_existente,
                es_reanudacion=True
            )


    

    # 3. Obtener IDs base
    tipo_res = await db.execute(text("SELECT id FROM auth.tipo_usuario WHERE nombre = 'chofer'"))
    tipo_id = tipo_res.scalar_one_or_none()
    if not tipo_id:
        logger.error("❌ Tipo 'chofer' no encontrado en BD")
        raise HTTPException(500, "Tipo 'chofer' no encontrado en BD")

    # Tenant temporal (se corrige en Etapa 3 al elegir ciudad)
    cb_res = await db.execute(text("SELECT id FROM tenant.control_base LIMIT 1"))
    temp_cb_id = cb_res.scalar_one_or_none()
    if not temp_cb_id:
        logger.error("❌ No hay tenants configurados en el sistema")
        raise HTTPException(500, "No hay tenants configurados en el sistema")

    user_id = uuid4()
    logger.info(f"✅ ID de usuario generado: {user_id}")
    
    # 4. Crear Usuario + Perfil Vacío + Expediente SIN vehículo
    logger.info("📝 Creando usuario en auth.usuario...")
    await db.execute(text("""
        INSERT INTO auth.usuario (id, tipo_usuario_id, control_base_id, email, password_hash, activo, created_at, updated_at)
        VALUES (:id, :tipo, :cb, :email, :pass, true, NOW(), NOW())
    """), {
        "id": user_id, "tipo": tipo_id, "cb": temp_cb_id, 
        "email": request.email, "pass": get_password_hash(request.password)
    })

    logger.info("📝 Creando perfil en auth.perfil_general...")
    await db.execute(text("""
        INSERT INTO auth.perfil_general (id, usuario_id, created_at, updated_at)
        VALUES (gen_random_uuid(), :uid, NOW(), NOW())
    """), {"uid": user_id})

    logger.info("📝 Creando expediente en fleet.chofer_vehiculo...")
    await db.execute(text("""
        INSERT INTO fleet.chofer_vehiculo (
            id, usuario_id, control_base_id, estado_laboral, estado_aprobacion, activo, created_at, updated_at
        )
        VALUES (gen_random_uuid(), :uid, :cb, 'fuera_servicio', 'pendiente', true, NOW(), NOW())
    """), {"uid": user_id, "cb": temp_cb_id})

    # 5. Generar y guardar OTP (6 dígitos, expira en 10 min)
    codigo = f"{random.randint(100000, 999999)}"
    logger.info(f"🔑 Código OTP generado: {codigo}")
    
    await db.execute(text("""
        INSERT INTO auth.codigo_verificacion (usuario_id, codigo, tipo, expira_en, creado_en)
        VALUES (:uid, :cod, 'REGISTRO_CHOFER', NOW() + INTERVAL '10 minutes', NOW())
    """), {"uid": user_id, "cod": codigo})

    await db.commit()
    logger.info("✅ Transacción completada exitosamente")

    # 6. Enviar email (no bloqueante, pero logueamos error)
    try:
        logger.info(f"📧 Enviando OTP por email a {request.email}...")
        enviado = await email_sender.send_verification_code(request.email, codigo)
        if enviado:
            logger.info(f"✅ Email enviado exitosamente a {request.email}")
        else:
            logger.warning(f"⚠️ No se pudo enviar email a {request.email}")
    except Exception as e:
        logger.error(f"❌ Error enviando email: {str(e)}")

    return ChoferInicioRegistroResponse(
        success=True, 
        message="Cuenta creada. Revisa tu email para validar.", 
        user_id=user_id
    )


# ==========================================
# ETAPA 2: VALIDAR EMAIL Y OBTENER JWT
# ==========================================
@router.post("/validar-email", response_model=ValidarEmailResponse)
async def validar_email_chofer(
    request: ValidarEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Valida código OTP. Si es correcto, emite JWT funcional."""
    logger.info(f"🔐 Validando OTP para email: {request.email}")
    
    # Buscar código válido, no usado y no expirado
    otp_res = await db.execute(text("""
        SELECT cv.id, cv.usuario_id, u.control_base_id 
        FROM auth.codigo_verificacion cv
        JOIN auth.usuario u ON u.id = cv.usuario_id
        WHERE cv.codigo = :cod 
          AND cv.usado = false 
          AND cv.expira_en > NOW()
          AND cv.tipo = 'REGISTRO_CHOFER'
          AND u.email = :email
        ORDER BY cv.creado_en DESC 
        LIMIT 1
    """), {"cod": request.codigo, "email": request.email})
    
    row = otp_res.first()
    if not row:
        logger.warning(f"❌ Código inválido o expirado: {request.codigo}")
        raise HTTPException(400, detail="Código inválido, expirado o ya utilizado")
    
    otp_id, user_id, control_base_id = row
    logger.info(f"✅ OTP válido para usuario: {user_id}")

    # Marcar como usado inmediatamente
    await db.execute(text("UPDATE auth.codigo_verificacion SET usado = true WHERE id = :oid"), {"oid": otp_id})
    await db.commit()

    # Emitir JWT funcional con claims necesarios
    token = create_access_token(data={
        "sub": str(user_id), 
        "tipo": "chofer", 
        "control_base_id": str(control_base_id)
    })
    logger.info("✅ JWT generado exitosamente")
    
    return ValidarEmailResponse(
        success=True, 
        access_token=token, 
        user_id=user_id, 
        message="Email validado exitosamente"
    )


# ==========================================
# ETAPA 3: ACTUALIZAR DATOS PERSONALES + TENANT
# ==========================================
@router.put("/datos-personales", response_model=DatosChoferResponse)
async def actualizar_datos_chofer(
    request: ActualizarDatosChoferRequest, 
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Completa perfil personal y asigna tenant automáticamente según ciudad."""
    user_id = current_user[0]
    logger.info(f"📝 Actualizando datos personales para usuario: {user_id}")

    # 1. Validar que la ciudad existe y obtener su tenant activo
    ciudad_res = await db.execute(text("""
        SELECT c.id, cb.id as tenant_id, cb.nombre as tenant_nom
        FROM geo.ciudad c 
        JOIN tenant.control_base cb ON cb.ciudad_id = c.id
        WHERE c.id = :cid AND cb.activo = true
    """), {"cid": request.ciudad_id})
    
    ciudad_row = ciudad_res.first()
    if not ciudad_row:
        logger.warning(f"❌ Ciudad inválida: {request.ciudad_id}")
        raise HTTPException(400, detail="Ciudad no válida o sin tenant activo asociado")
    
    _, new_tenant_id, tenant_nombre = ciudad_row
    logger.info(f"✅ Tenant asignado: {tenant_nombre}")

    # 2. Actualizar perfil general
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
    logger.info("✅ Datos personales actualizados correctamente")

    return DatosChoferResponse(
        success=True, 
        tenant_nombre=tenant_nombre, 
        pasos_completados={"email": True, "datos": True}
    )


# ==========================================
# ETAPA 4: SUBIR DOCUMENTO INDIVIDUAL
# ==========================================
@router.post("/documento", response_model=DocumentoChoferResponse)
async def subir_documento_chofer(
    file: UploadFile = File(...),
    tipo_documento: str = Query(..., description="dni, licencia, sanidad o buena_conducta"),
    fecha_vencimiento: Optional[date] = Query(None),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sube un documento específico. Valida tipos, obligatoriedad de fechas y vencimientos bloqueantes."""
    user_id = current_user[0]
    logger.info(f"📄 Subiendo documento: {tipo_documento} para usuario {user_id}")
    logger.info(f"📎 Archivo: {file.filename}, Content-Type: {file.content_type}")
    
    if tipo_documento not in TIPOS_DOC_CHOFER:
        logger.warning(f"❌ Tipo de documento inválido: {tipo_documento}")
        raise HTTPException(400, detail=f"Tipo inválido. Permitidos: {TIPOS_DOC_CHOFER}")

    # Validaciones de vencimiento BLOQUEANTES (excepto DNI)
    if tipo_documento in DOC_BLOQUEANTES and not fecha_vencimiento:
        logger.warning(f"❌ Fecha de vencimiento obligatoria para {tipo_documento}")
        raise HTTPException(400, detail=f"Fecha de vencimiento obligatoria para {tipo_documento}")
    
    if fecha_vencimiento and fecha_vencimiento < date.today() and tipo_documento != 'dni':
        logger.warning(f"❌ Documento vencido: {tipo_documento} - {fecha_vencimiento}")
        raise HTTPException(400, detail="El documento está vencido y no puede ser aceptado")

    # Subir a Cloudinary
    try:
        logger.info("📤 Subiendo a Cloudinary...")
        from app.services.cloudinary_storage import cloudinary_storage
        url = await cloudinary_storage.upload_documento_chofer(
            file=file,
            usuario_id=str(user_id),
            tipo_documento=tipo_documento
        )
        logger.info(f"✅ Cloudinary OK: {url}")
    except Exception as e:
        logger.error(f"❌ Error en Cloudinary: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=f"Error subiendo archivo a storage: {str(e)}")

    # Guardar/Actualizar en BD (UPSERT)
    try:
        logger.info("💾 Guardando en BD...")
        await db.execute(text("""
            INSERT INTO fleet.documentos_chofer (usuario_id, tipo_documento, url, fecha_vencimiento, subido_en, activo)
            VALUES (:uid, :tipo, :url, :fv, NOW(), true)
            ON CONFLICT (usuario_id, tipo_documento) DO UPDATE 
            SET url = :url, fecha_vencimiento = :fv, subido_en = NOW(), activo = true
        """), {"uid": user_id, "tipo": tipo_documento, "url": url, "fv": fecha_vencimiento})
        await db.commit()
        logger.info("✅ BD actualizada correctamente")
    except Exception as e:
        logger.error(f"❌ Error en BD: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=f"Error guardando documento: {str(e)}")

    # Calcular pendientes para feedback inmediato al frontend
    docs_existentes = await db.execute(text("""
        SELECT tipo_documento FROM fleet.documentos_chofer 
        WHERE usuario_id = :uid AND activo = true
    """), {"uid": user_id})
    existentes = {r[0] for r in docs_existentes.all()}
    pendientes = [d for d in TIPOS_DOC_CHOFER if d not in existentes]
    logger.info(f"📋 Documentos pendientes: {pendientes}")

    return DocumentoChoferResponse(
        success=True, 
        tipo_documento=tipo_documento, 
        url=url, 
        documentos_pendientes=pendientes
    )


# ==========================================
# ETAPA 5: SELFIE Y ENVÍO A REVISIÓN
# ==========================================
@router.post("/selfie", response_model=FinalizarRegistroResponse)
async def registrar_selfie_chofer(
    request: SelfieChoferRequest,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Guarda selfie dual (perfil + evidencia) y transiciona expediente a 'en_revision'."""
    user_id = current_user[0]
    logger.info(f"📸 Registrando selfie para usuario: {user_id}")

    # 1. Validar completitud total antes de permitir selfie final
    checks = await db.execute(text("""
        SELECT 
            (SELECT COUNT(*) FROM fleet.documentos_chofer WHERE usuario_id = :uid AND activo = true) as doc_count,
            (SELECT nombre FROM auth.perfil_general WHERE usuario_id = :uid) as tiene_datos
    """), {"uid": user_id})
    row = checks.first()
    
    if not row or row[1] is None or row[0] < 4:
        logger.warning(f"❌ Faltan datos o documentos para selfie: docs={row[0] if row else 0}, datos={row[1] if row else None}")
        raise HTTPException(400, detail="Completa todos los datos personales y 4 documentos antes de la selfie")

    # 2. Guardar selfie dual (Perfil + Evidencia documental)
    logger.info("💾 Guardando selfie...")
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
    logger.info("✅ Selfie registrada, expediente en revisión")

    return FinalizarRegistroResponse(
        success=True, 
        estado_aprobacion="en_revision", 
        mensaje="Expediente enviado correctamente a revisión administrativa"
    )


# ==========================================
# CONSULTA DE ESTADO / REANUDACIÓN
# ==========================================
@router.get("/estado-expediente", response_model=EstadoExpedienteResponse)
async def obtener_estado_expediente(
    current_user: tuple = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Devuelve progreso completo, estado aprobación, motivos de rechazo y docs faltantes."""
    user_id = current_user[0]
    logger.info(f"📊 Consultando estado de expediente para usuario: {user_id}")

    # Query consolidada de estado
    try:
        res = await db.execute(text("""
            SELECT 
                cv.estado_aprobacion, 
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
    except Exception as e:
        logger.error(f"❌ Error en consulta de estado: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Error consultando estado del expediente")
    
    row = res.first()
    if not row:
        logger.warning(f"❌ Expediente no encontrado para usuario: {user_id}")
        raise HTTPException(404, detail="Expediente de chofer no encontrado")

    estado, lab, tiene_datos, tiene_selfie, tenant, tiene_vehiculo = row
    logger.info(f"📊 Estado: aprobacion={estado}, laboral={lab}, tenant={tenant}")

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
        motivo_rechazo=None,
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
# VERIFICAR DNI (por tenant)
# ==========================================

@router.get("/verificar-dni")
async def verificar_dni(
    dni: str = Query(..., description="DNI a verificar"),
    ciudad_id: UUID = Query(..., description="Ciudad seleccionada para determinar el tenant"),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica si un DNI ya está registrado como chofer en el tenant asociado a la ciudad.
    Distingue entre registro completo (bloquear) y registro pendiente (permitir reemplazar).
    """
    logger.info(f"🔍 Verificando DNI {dni} en ciudad {ciudad_id}")

    # 1. Obtener el tenant de la ciudad
    ciudad_res = await db.execute(text("""
        SELECT cb.id as tenant_id
        FROM geo.ciudad c
        JOIN tenant.control_base cb ON cb.ciudad_id = c.id
        WHERE c.id = :cid AND cb.activo = true
    """), {"cid": ciudad_id})
    ciudad_row = ciudad_res.first()

    if not ciudad_row:
        raise HTTPException(400, detail="Ciudad no válida o sin tenant activo")

    tenant_id = ciudad_row[0]

    # 2. Buscar chofer con ese DNI en ese tenant
    result = await db.execute(text("""
        SELECT cv.estado_aprobacion, u.id
        FROM auth.perfil_general p
        JOIN auth.usuario u ON u.id = p.usuario_id
        JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id
        WHERE p.documento = :dni
          AND cv.control_base_id = :tenant_id
        LIMIT 1
    """), {"dni": dni, "tenant_id": tenant_id})

    row = result.first()

    if row:
        estado_aprobacion = row[0]

        # Registro PENDIENTE o RECHAZADO → permitir continuar
        # (el registro anterior fue abandonado o rechazado)
        if estado_aprobacion in ('pendiente', 'rechazado'):
            logger.info(f"🔄 DNI {dni} con registro {estado_aprobacion}. Se permite continuar.")
            return {
                "existe": True,
                "estado_aprobacion": estado_aprobacion,
                "bloqueante": False,  # ← No bloquea
                "mensaje": "Ya tenías un registro anterior incompleto. Podés continuar."
            }

        # Registro APROBADO o EN REVISIÓN → bloquear
        logger.warning(f"⚠️ DNI {dni} ya registrado en estado {estado_aprobacion}")
        return {
            "existe": True,
            "estado_aprobacion": estado_aprobacion,
            "bloqueante": True,  # ← Bloquea
            "mensaje": "Ya existe un chofer con este DNI en esta ciudad."
        }

    logger.info(f"✅ DNI {dni} disponible en tenant {tenant_id}")
    return {
        "existe": False,
        "bloqueante": False
    }