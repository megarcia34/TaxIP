"""
Email service for password recovery and notifications
"""

import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@taxip.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


# ============================================
# GENERAR CÓDIGO DE VERIFICACIÓN
# ============================================
def generate_verification_code(length: int = 6) -> str:
    """Generar código numérico de verificación"""
    return ''.join(random.choices(string.digits, k=length))


# ============================================
# ENVIAR EMAIL DE VERIFICACIÓN
# ============================================
async def send_verification_email(email_to: str, codigo: str) -> bool:
    """
    Enviar email con código de verificación
    """
    subject = "🔐 Verifica tu email - TaxIP"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Verifica tu email</title>
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
            <div style="text-align: center; padding-bottom: 20px;">
                <h1 style="color: #1a1a1a;">🚕 TaxIP</h1>
            </div>
            <p>Hola,</p>
            <p>Gracias por registrarte en <strong>TaxIP</strong>. Para verificar tu email, utiliza el siguiente código:</p>
            <div style="font-size: 36px; font-weight: bold; color: #FBBF24; text-align: center; padding: 20px; background: #FFFBEB; border-radius: 8px; margin: 20px 0; letter-spacing: 8px;">
                {codigo}
            </div>
            <p style="font-size: 14px; color: #666;">Este código expira en <strong>10 minutos</strong>.</p>
            <p style="font-size: 14px; color: #666;">Si no solicitaste este registro, ignora este mensaje.</p>
            <hr style="margin: 20px 0;">
            <p style="color: #777; font-size: 12px; text-align: center;">© 2026 TaxIP - Tu viaje seguro</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Verifica tu email - TaxIP
    
    Gracias por registrarte en TaxIP.
    
    Tu código de verificación es: {codigo}
    
    Este código expira en 10 minutos.
    
    Si no solicitaste este registro, ignora este mensaje.
    
    TaxIP - Tu viaje seguro
    """
    
    return await send_email(email_to, subject, html_content, text_content)


# ============================================
# ENVIAR EMAIL DE RECUPERACIÓN DE CONTRASEÑA
# ============================================
async def send_password_recovery_email(email_to: str, reset_token: str) -> bool:
    """
    Send password recovery email with reset link
    """
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    
    subject = "Recuperación de contraseña - TaxIP"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recuperación de contraseña</title>
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
            <div style="text-align: center; padding-bottom: 20px;">
                <h1 style="color: #1a1a1a;">🚕 TaxIP</h1>
            </div>
            <h2 style="color: #555;">Recuperación de contraseña</h2>
            <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
            <p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #FBBF24; color: #1a1a1a; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: 600;">
                    Restablecer contraseña
                </a>
            </div>
            <p style="font-size: 14px; color: #666;">Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
            <p style="font-size: 14px; color: #666;">Este enlace expirará en <strong>1 hora</strong>.</p>
            <hr style="margin: 20px 0;">
            <p style="color: #777; font-size: 12px; text-align: center;">© 2026 TaxIP - Tu viaje seguro</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Recuperación de contraseña - TaxIP
    
    Hemos recibido una solicitud para restablecer tu contraseña.
    
    Copia y pega este enlace en tu navegador:
    {reset_url}
    
    Este enlace expirará en 1 hora.
    
    Si no solicitaste este cambio, puedes ignorar este mensaje.
    
    TaxIP - Tu viaje seguro
    """
    
    return await send_email(email_to, subject, html_content, text_content)


# ============================================
# ENVIAR EMAIL GENÉRICO
# ============================================
async def send_email(to_email: str, subject: str, html_content: str, text_content: str) -> bool:
    """
    Generic email sender using SMTP
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"⚠️ Email not configured. Would send to {to_email}: {subject}")
        return False
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SMTP_FROM
        message["To"] = to_email
        
        # Attach both plain text and HTML versions
        part_text = MIMEText(text_content, "plain")
        part_html = MIMEText(html_content, "html")
        
        message.attach(part_text)
        message.attach(part_html)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, message.as_string())
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False