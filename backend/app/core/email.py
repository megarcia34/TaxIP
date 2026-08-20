"""
Servicio de envío de emails
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: Optional[str] = None
) -> bool:
    """
    Envía un email con formato texto y HTML

    Args:
        to_email: Destinatario
        subject: Asunto del email
        text_content: Contenido en texto plano
        html_content: Contenido en HTML (opcional)

    Returns:
        bool: True si se envió correctamente
    """
    # Validar configuración SMTP
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error("❌ Configuración SMTP incompleta. Verifica SMTP_HOST, SMTP_USER, SMTP_PASSWORD")
        return False

    try:
        # Crear mensaje multipart
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        # Adjuntar texto plano
        part_text = MIMEText(text_content, "plain", "utf-8")
        msg.attach(part_text)

        # Adjuntar HTML si está presente
        if html_content:
            part_html = MIMEText(html_content, "html", "utf-8")
            msg.attach(part_html)

        # Conectar y enviar
        logger.info(f"📧 Conectando a SMTP {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        
        
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        logger.info(f"✅ Email enviado a {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Error de autenticación SMTP: {e}. Verifica usuario y contraseña.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ Error SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        return False


async def send_verification_email(
    to_email: str,
    verification_code: str,
    nombre_usuario: Optional[str] = None
) -> bool:
    """
    Envía un email de verificación de cuenta

    Args:
        to_email: Email del destinatario
        verification_code: Código de verificación
        nombre_usuario: Nombre del usuario (opcional)

    Returns:
        bool: True si se envió correctamente
    """
    saludo = f"Hola {nombre_usuario}," if nombre_usuario else "Hola,"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Verificación de cuenta - TaxIP</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; border-top: 6px solid #1a73e8;">
            <h1 style="color: #1a73e8;">✅ Verificación de cuenta</h1>
            <p>{saludo}</p>
            <p>Gracias por registrarte en <strong>TaxIP</strong>. Para completar tu registro, ingresa el siguiente código de verificación:</p>
            
            <div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #f0f4ff; border-radius: 8px; border: 2px dashed #1a73e8;">
                <h2 style="font-size: 32px; letter-spacing: 8px; color: #1a73e8; margin: 0;">{verification_code}</h2>
            </div>
            
            <p style="color: #666; font-size: 14px;">Este código expirará en <strong>15 minutos</strong>.</p>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                Si no solicitaste este registro, puedes ignorar este mensaje.
                <br>Este es un mensaje automático de <strong>TaxIP</strong>.
            </p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    ✅ Verificación de cuenta

    {saludo}

    Gracias por registrarte en TaxIP. Para completar tu registro, ingresa el siguiente código de verificación:

    {verification_code}

    Este código expirará en 15 minutos.

    Si no solicitaste este registro, puedes ignorar este mensaje.

    ---
    Este es un mensaje automático de TaxIP.
    """

    return await send_email(
        to_email=to_email,
        subject="✅ Verifica tu cuenta - TaxIP",
        text_content=text_content,
        html_content=html_content
    )


async def send_password_recovery_email(
    to_email: str,
    recovery_token: str,
    nombre_usuario: Optional[str] = None
) -> bool:
    """
    Envía un email de recuperación de contraseña

    Args:
        to_email: Email del destinatario
        recovery_token: Token de recuperación
        nombre_usuario: Nombre del usuario (opcional)

    Returns:
        bool: True si se envió correctamente
    """
    recovery_url = f"{settings.FRONTEND_URL}/recuperar-contrasenia?token={recovery_token}"
    
    saludo = f"Hola {nombre_usuario}," if nombre_usuario else "Hola,"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recuperación de contraseña - TaxIP</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; border-top: 6px solid #ea580c;">
            <h1 style="color: #ea580c;">🔄 Recuperación de contraseña</h1>
            <p>{saludo}</p>
            <p>Hemos recibido una solicitud para restablecer tu contraseña en <strong>TaxIP</strong>.</p>
            <p>Para continuar, haz clic en el siguiente botón:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{recovery_url}" 
                   style="background-color: #ea580c; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 6px; font-weight: bold;">
                    🔑 Restablecer contraseña
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">O copia y pega este enlace en tu navegador:</p>
            <p style="color: #666; font-size: 12px; word-break: break-all;">{recovery_url}</p>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                Si no solicitaste este cambio, puedes ignorar este mensaje.
                <br>Este enlace expirará en 24 horas.
                <br>Este es un mensaje automático de <strong>TaxIP</strong>.
            </p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    🔄 Recuperación de contraseña

    {saludo}

    Hemos recibido una solicitud para restablecer tu contraseña en TaxIP.

    Para continuar, haz clic en el siguiente enlace:
    {recovery_url}

    Si no solicitaste este cambio, puedes ignorar este mensaje.
    Este enlace expirará en 24 horas.

    ---
    Este es un mensaje automático de TaxIP.
    """

    return await send_email(
        to_email=to_email,
        subject="🔑 Recuperación de contraseña - TaxIP",
        text_content=text_content,
        html_content=html_content
    )


async def send_notificacion_vencimiento_email(
    to_email: str,
    tipo_documento: str,
    numero: str,
    fecha_vencimiento: str,
    dias_restantes: int,
    nivel: str
) -> bool:
    """
    Envía un email de notificación de vencimiento de documento

    Args:
        to_email: Email del destinatario
        tipo_documento: Tipo de documento (ej: 'seguro', 'vtv')
        numero: Número del documento
        fecha_vencimiento: Fecha de vencimiento
        dias_restantes: Días restantes (puede ser negativo)
        nivel: Nivel de alerta (vencido, critico, urgente, preventivo)

    Returns:
        bool: True si se envió correctamente
    """
    niveles = {
        "vencido": {
            "titulo": "⚠️ Documento Vencido",
            "color": "#dc2626",
            "icono": "⚠️",
            "accion": "Renueve el documento inmediatamente."
        },
        "critico": {
            "titulo": f"🔴 Documento Crítico - Vence en {dias_restantes} días",
            "color": "#ea580c",
            "icono": "🔴",
            "accion": "Renueve el documento lo antes posible."
        },
        "urgente": {
            "titulo": f"🟠 Documento Urgente - Vence en {dias_restantes} días",
            "color": "#ca8a04",
            "icono": "🟠",
            "accion": "Planifique la renovación del documento."
        },
        "preventivo": {
            "titulo": f"📋 Documento Preventivo - Vence en {dias_restantes} días",
            "color": "#2563eb",
            "icono": "📋",
            "accion": "Recuerde renovar el documento antes de la fecha de vencimiento."
        }
    }

    info = niveles.get(nivel, niveles["preventivo"])
    tipo_display = tipo_documento.replace('_', ' ').upper()

    textos = {
        "vencido": f"está <strong>VENCIDO</strong> desde hace <strong>{abs(dias_restantes)} días</strong>.",
        "critico": f"vence en <strong>{dias_restantes} días</strong>.",
        "urgente": f"vence en <strong>{dias_restantes} días</strong>.",
        "preventivo": f"vence en <strong>{dias_restantes} días</strong>."
    }

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{info['titulo']}</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; border-top: 6px solid {info['color']};">
            <h1 style="color: {info['color']};">{info['icono']} {info['titulo']}</h1>
            <p>Estimado propietario,</p>
            <p>El documento <strong>{tipo_display}</strong> N° <strong>{numero}</strong> 
            {textos.get(nivel, '')}</p>
            <p>{info['accion']}</p>
            
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">📄 Detalles del documento</h3>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Tipo:</strong> {tipo_display}</li>
                    <li><strong>Número:</strong> {numero}</li>
                    <li><strong>Fecha de vencimiento:</strong> {fecha_vencimiento}</li>
                    <li><strong>Días restantes:</strong> {dias_restantes}</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 25px 0;">
                <a href="{settings.FRONTEND_URL}/dashboard-propietario/documentos" 
                   style="background-color: {info['color']}; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 6px; font-weight: bold;">
                    📂 Ver todos los documentos
                </a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                Este es un mensaje automático de <strong>TaxIP</strong>.
            </p>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    {info['icono']} {info['titulo']}

    Estimado propietario,

    El documento {tipo_display} N° {numero} 
    {textos.get(nivel, '')}
    {info['accion']}

    Detalles:
    - Tipo: {tipo_display}
    - Número: {numero}
    - Fecha de vencimiento: {fecha_vencimiento}
    - Días restantes: {dias_restantes}

    Para ver todos los documentos: {settings.FRONTEND_URL}/dashboard-propietario/documentos

    ---
    Este es un mensaje automático de TaxIP.
    """

    return await send_email(
        to_email=to_email,
        subject=f"{info['icono']} {info['titulo']}",
        text_content=text_content,
        html_content=html_content
    )