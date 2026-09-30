"""
Servicio para envío de códigos de verificación (OTP) via email.
Complementa a email_validation.py (que solo valida existencia).
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    @staticmethod
    async def send_verification_code(email: str, code: str) -> bool:
        """
        Envía un código de verificación de 6 dígitos.
        Retorna True si se despachó correctamente al servidor SMTP.
        """
        subject = "TAX IP - Código de Verificación de Cuenta"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
            <h2 style="color: #00bfff;">Bienvenido a TAX IP</h2>
            <p>Estás registrando tu cuenta de chofer. Ingresa el siguiente código para validar tu email:</p>
            <h1 style="letter-spacing: 5px; color: #333; background: #f0f0f0; padding: 10px; text-align: center; border-radius: 5px;">{code}</h1>
            <p><strong>Este código expira en 10 minutos.</strong></p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <small style="color: #888;">Si no solicitaste este registro, ignora este correo.</small>
        </div>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM
        msg['To'] = email
        msg.attach(MIMEText(html_content, 'html'))

        # Validar configuración
        if not all([
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.SMTP_FROM,
        ]):
            logger.error("❌ Configuración SMTP incompleta en .env")
            return False

        try:
            # Puerto 465 → SSL directo
            if settings.SMTP_PORT == 465:
                logger.info(f"📧 Conectando por SSL a {settings.SMTP_HOST}:{settings.SMTP_PORT}")
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_FROM, [email], msg.as_string())
            else:
                # Puerto 587 u otros → STARTTLS
                logger.info(f"📧 Conectando por STARTTLS a {settings.SMTP_HOST}:{settings.SMTP_PORT}")
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_FROM, [email], msg.as_string())

            logger.info(f"✅ Código OTP enviado exitosamente a {email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ Error de autenticación SMTP: {str(e)}")
            logger.error("   Verificá que SMTP_USER y SMTP_PASSWORD sean correctos")
            logger.error("   Si usás Gmail, recordá usar una 'Contraseña de aplicación'")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"❌ Error SMTP al enviar a {email}: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"❌ Error crítico enviando OTP a {email}: {str(e)}")
            return False


# Instancia singleton para uso global
email_sender = EmailSender()