"""
Verificación de email y notificaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
import uuid as uuid_lib
from datetime import datetime, timedelta
from typing import Optional
import re
import logging
import asyncio

from app.database import get_db
from app.dependencies import get_current_user
from app.core.email import send_verification_email
from app.core.security import generate_verification_code
from app.services.email_validation import email_validator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/verificacion", tags=["Verificación"])


# ============================================
# VALIDAR EMAIL CON TIMEOUT
# ============================================
@router.post("/validar-email")
async def validar_email(
    email: str = Query(..., description="Email a validar"),
    strict: bool = Query(True, description="Validación estricta (SMTP)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Validar email en tiempo real con timeout de 8 segundos
    strict=True: Verifica formato + MX + SMTP (buzón existe)
    strict=False: Solo formato + MX (más rápido)
    """
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email es requerido"
        )
    
    # 1. Validar formato primero (rápido)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    format_valid = bool(re.match(pattern, email))
    
    if not format_valid:
        return {
            "email": email,
            "valid": False,
            "format_valid": False,
            "reason": "Formato de email inválido",
            "domain": None,
            "mx_records": None,
            "buzon_existe": False,
            "smtp_response": None,
            "registrado": False,
            "suggestions": []
        }
    
    # 2. Verificar si ya está registrado (rápido)
    registrado = False
    try:
        query = text("SELECT id FROM auth.usuario WHERE email = :email")
        db_result = await db.execute(query, {"email": email})
        registrado = db_result.first() is not None
    except Exception:
        pass
    
    # 3. Si strict es False, solo formato + MX
    if not strict:
        domain = email.split('@')[1].lower() if '@' in email else None
        mx_records = email_validator.get_mx_records(domain) if domain else []
        return {
            "email": email,
            "valid": True,
            "format_valid": True,
            "reason": "Formato y MX válidos" if mx_records else "No hay servidores MX",
            "domain": domain,
            "mx_records": mx_records,
            "buzon_existe": None,
            "smtp_response": None,
            "registrado": registrado,
            "suggestions": email_validator._get_suggestions(email)
        }
    
    # 4. Validación SMTP con TIMEOUT (8 segundos máximo)
    result = None
    try:
        # Ejecutar validación SMTP en un thread separado con timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(email_validator.validate_email_smtp, email),
            timeout=8.0
        )
    except asyncio.TimeoutError:
        logger.warning(f"⏰ Timeout validando email: {email}")
        return {
            "email": email,
            "valid": False,
            "format_valid": True,
            "reason": "Timeout verificando el email (más de 8 segundos)",
            "domain": email.split('@')[1].lower() if '@' in email else None,
            "mx_records": None,
            "buzon_existe": False,
            "smtp_response": "Timeout",
            "registrado": registrado,
            "suggestions": []
        }
    except Exception as e:
        logger.error(f"Error validando email: {e}")
        return {
            "email": email,
            "valid": False,
            "format_valid": True,
            "reason": f"Error al validar: {str(e)[:100]}",
            "domain": email.split('@')[1].lower() if '@' in email else None,
            "mx_records": None,
            "buzon_existe": False,
            "smtp_response": str(e)[:100],
            "registrado": registrado,
            "suggestions": []
        }
    
    # 5. Registrar auditoría
    try:
        audit_id = uuid_lib.uuid4()
        insert_audit = text("""
            INSERT INTO auth.auditoria_email (
                id, email, valid, format_valid, domain, mx_records,
                smtp_response, ip_address, user_agent, created_at
            )
            VALUES (
                :id, :email, :valid, :format_valid, :domain,
                :mx_records, :smtp_response, :ip_address, :user_agent, NOW()
            )
        """)
        
        await db.execute(insert_audit, {
            "id": audit_id,
            "email": email,
            "valid": result.get("valid", False) if result else False,
            "format_valid": True,
            "domain": result.get("domain") if result else None,
            "mx_records": str(result.get("mx_records", [])) if result and result.get("mx_records") else None,
            "smtp_response": result.get("smtp_response") if result else "Error",
            "ip_address": "0.0.0.0",
            "user_agent": "web"
        })
        await db.commit()
    except Exception as e:
        logger.error(f"Error registrando auditoría: {e}")
    
    # 6. Retornar resultado
    if result:
        return {
            "email": email,
            "valid": result.get("valid", False),
            "format_valid": True,
            "reason": result.get("reason", ""),
            "domain": result.get("domain"),
            "mx_records": result.get("mx_records"),
            "buzon_existe": result.get("buzon_existe", False),
            "smtp_response": result.get("smtp_response"),
            "registrado": registrado,
            "suggestions": email_validator._get_suggestions(email)
        }
    else:
        return {
            "email": email,
            "valid": False,
            "format_valid": True,
            "reason": "No se pudo validar el email",
            "domain": None,
            "mx_records": None,
            "buzon_existe": False,
            "smtp_response": None,
            "registrado": registrado,
            "suggestions": email_validator._get_suggestions(email)
        }


# ============================================
# ENVIAR CÓDIGO DE VERIFICACIÓN
# ============================================
@router.post("/enviar")
async def enviar_codigo_verificacion(
    email: str = Query(..., description="Email para verificar"),
    db: AsyncSession = Depends(get_db)
):
    """
    Enviar código de verificación al email
    """
    if not email or "@" not in email or "." not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email inválido"
        )
    
    # Verificar si ya está registrado
    query = text("SELECT id FROM auth.usuario WHERE email = :email")
    result = await db.execute(query, {"email": email})
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado en la plataforma"
        )
    
    # Generar código
    codigo = generate_verification_code()
    expiracion = datetime.utcnow() + timedelta(minutes=10)
    
    # Guardar en tabla temporal
    try:
        check_table = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'auth' AND table_name = 'verificacion_email'
            )
        """)
        table_exists = await db.execute(check_table)
        exists = table_exists.scalar()
        
        if exists:
            insert_query = text("""
                INSERT INTO auth.verificacion_email (id, email, codigo, expiracion, usado, created_at)
                VALUES (gen_random_uuid(), :email, :codigo, :expiracion, false, NOW())
                ON CONFLICT (email) DO UPDATE SET
                    codigo = :codigo,
                    expiracion = :expiracion,
                    usado = false,
                    created_at = NOW()
            """)
            
            await db.execute(insert_query, {
                "email": email,
                "codigo": codigo,
                "expiracion": expiracion
            })
            await db.commit()
        else:
            logger.warning(f"⚠️ Tabla auth.verificacion_email no existe. Creándola...")
            create_table = text("""
                CREATE TABLE IF NOT EXISTS auth.verificacion_email (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR NOT NULL UNIQUE,
                    codigo VARCHAR(6) NOT NULL,
                    expiracion TIMESTAMP NOT NULL,
                    usado BOOLEAN DEFAULT false,
                    verificado_en TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await db.execute(create_table)
            await db.commit()
            
            insert_query = text("""
                INSERT INTO auth.verificacion_email (id, email, codigo, expiracion, usado, created_at)
                VALUES (gen_random_uuid(), :email, :codigo, :expiracion, false, NOW())
            """)
            await db.execute(insert_query, {
                "email": email,
                "codigo": codigo,
                "expiracion": expiracion
            })
            await db.commit()
            
    except Exception as e:
        logger.error(f"Error guardando código: {e}")
    
    # Enviar email
    try:
        await send_verification_email(email, codigo)
    except Exception as e:
        logger.error(f"Error enviando email: {e}")
    
    return {
        "success": True,
        "message": "Código enviado al email",
        "expira_en": 10,
        "codigo": codigo
    }


# ============================================
# VERIFICAR CÓDIGO
# ============================================
@router.post("/verificar")
async def verificar_codigo(
    email: str = Query(..., description="Email verificado"),
    codigo: str = Query(..., description="Código de 6 dígitos"),
    db: AsyncSession = Depends(get_db)
):
    """
    Verificar código de email
    """
    query = text("""
        SELECT id, expiracion, usado
        FROM auth.verificacion_email
        WHERE email = :email AND codigo = :codigo
    """)
    result = await db.execute(query, {"email": email, "codigo": codigo})
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido"
        )
    
    verif_id, expiracion, usado = row
    
    if usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código ya fue usado"
        )
    
    if datetime.utcnow() > expiracion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código ha expirado"
        )
    
    update_query = text("""
        UPDATE auth.verificacion_email
        SET usado = true, verificado_en = NOW()
        WHERE id = :id
    """)
    await db.execute(update_query, {"id": verif_id})
    await db.commit()
    
    return {
        "success": True,
        "message": "Email verificado correctamente",
        "email": email
    }


# ============================================
# VERIFICAR SI EMAIL ESTÁ REGISTRADO
# ============================================
@router.get("/check-registro")
async def check_email_registrado(
    email: str = Query(..., description="Email a verificar"),
    db: AsyncSession = Depends(get_db)
):
    """
    Verificar si un email ya está registrado en la plataforma
    """
    query = text("""
        SELECT id FROM auth.usuario WHERE email = :email
    """)
    result = await db.execute(query, {"email": email})
    row = result.first()
    
    return {
        "email": email,
        "registrado": row is not None
    }


# ============================================
# OBTENER ESTADO DE VERIFICACIÓN
# ============================================
@router.get("/estado")
async def obtener_estado_verificacion(
    email: str = Query(..., description="Email a consultar"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estado de verificación de un email
    """
    query = text("""
        SELECT usado, verificado_en, created_at
        FROM auth.verificacion_email
        WHERE email = :email
        ORDER BY created_at DESC
        LIMIT 1
    """)
    result = await db.execute(query, {"email": email})
    row = result.first()
    
    if not row:
        return {
            "email": email,
            "verificado": False,
            "message": "Email no verificado"
        }
    
    usado, verificado_en, created_at = row
    
    return {
        "email": email,
        "verificado": usado and verificado_en is not None,
        "verificado_en": verificado_en,
        "created_at": created_at
    }


# ============================================
# NOTIFICACIONES
# ============================================
@router.get("/notificaciones")
async def get_notificaciones(
    limit: int = Query(20, description="Límite de resultados"),
    offset: int = Query(0, description="Desplazamiento"),
    solo_no_leidas: bool = Query(False, description="Solo no leídas"),
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener notificaciones del usuario actual
    """
    user_id = current_user[0]
    
    where_clause = "usuario_id = :user_id"
    params = {"user_id": user_id, "limit": limit, "offset": offset}
    
    if solo_no_leidas:
        where_clause += " AND leida = false"
    
    query = text(f"""
        SELECT id, titulo, mensaje, tipo, leida, created_at
        FROM notification.notificacion
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = await db.execute(query, params)
    rows = result.all()
    
    count_query = text("""
        SELECT COUNT(*) FROM notification.notificacion
        WHERE usuario_id = :user_id AND leida = false
    """)
    count_result = await db.execute(count_query, {"user_id": user_id})
    no_leidas = count_result.scalar() or 0
    
    return {
        "notificaciones": [
            {
                "id": row[0],
                "titulo": row[1],
                "mensaje": row[2],
                "tipo": row[3],
                "leida": row[4],
                "created_at": row[5]
            }
            for row in rows
        ],
        "no_leidas": no_leidas
    }


@router.put("/notificaciones/{notificacion_id}/leer")
async def marcar_como_leida(
    notificacion_id: UUID,
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marcar una notificación como leída
    """
    user_id = current_user[0]
    
    update_query = text("""
        UPDATE notification.notificacion
        SET leida = true
        WHERE id = :id AND usuario_id = :user_id
        RETURNING id
    """)
    
    result = await db.execute(update_query, {
        "id": notificacion_id,
        "user_id": user_id
    })
    
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    await db.commit()
    
    return {"success": True, "message": "Notificación marcada como leída"}


@router.put("/notificaciones/leer-todas")
async def marcar_todas_como_leidas(
    current_user: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marcar todas las notificaciones como leídas
    """
    user_id = current_user[0]
    
    update_query = text("""
        UPDATE notification.notificacion
        SET leida = true
        WHERE usuario_id = :user_id AND leida = false
    """)
    
    await db.execute(update_query, {"user_id": user_id})
    await db.commit()
    
    return {"success": True, "message": "Todas las notificaciones marcadas como leídas"}