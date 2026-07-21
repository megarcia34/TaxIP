"""
Servicio de validación de email en tiempo real (SMTP)
Verifica si el buzón realmente existe
"""

import re
import smtplib
import socket
import dns.resolver
from typing import Dict, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class EmailValidator:
    """
    Valida emails en tiempo real usando SMTP
    Verifica si el buzón existe sin enviar mensajes
    """
    
    def __init__(self):
        self.timeout = 3  # segundos (aún más reducido)
        self.cache = {}
        self.smtp_from = "verify@taxip.com.ar"
        
        # Dominios que sabemos que son válidos (validación inmediata, sin SMTP)
        self.trusted_domains = {
            'gmail.com', 'gmail.com.ar',
            'hotmail.com', 'hotmail.es', 'hotmail.com.ar',
            'outlook.com', 'outlook.es', 'outlook.com.ar',
            'yahoo.com', 'yahoo.com.ar', 'yahoo.es',
            'protonmail.com', 'protonmail.ch',
            'icloud.com', 'me.com', 'mac.com',
            'live.com', 'msn.com',
            'aol.com', 'mail.com',
            'googlemail.com', 'yandex.com', 
            'zoho.com', 'tutanota.com',
            'gmx.com', 'gmx.es', 'gmx.net',
            'fastmail.com', 'hey.com',
            'segurytec.com.ar'  # Agregar dominios locales
        }
    
    def validate_format(self, email: str) -> bool:
        """Validar formato básico del email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_domain(self, email: str) -> Optional[str]:
        """Extraer dominio del email"""
        try:
            return email.split('@')[1].lower()
        except:
            return None
    
    def get_mx_records(self, domain: str) -> List[Tuple[int, str]]:
        """Obtener registros MX del dominio"""
        try:
            records = dns.resolver.resolve(domain, 'MX')
            return sorted([(r.preference, str(r.exchange).rstrip('.')) for r in records])
        except Exception as e:
            logger.warning(f"Error obteniendo MX para {domain}: {e}")
            return []
    
    def validate_email_smtp(self, email: str) -> Dict:
        """
        Validar email mediante SMTP (verifica si el buzón existe)
        """
        result = {
            "valid": False,
            "reason": "",
            "mx_records": [],
            "domain": "",
            "format_valid": False,
            "smtp_response": "",
            "buzon_existe": False
        }
        
        # 1. Validar formato
        if not self.validate_format(email):
            result["reason"] = "Formato de email inválido"
            result["format_valid"] = False
            return result
        
        result["format_valid"] = True
        
        # 2. Obtener dominio
        domain = self.get_domain(email)
        if not domain:
            result["reason"] = "No se pudo extraer el dominio"
            return result
        
        result["domain"] = domain
        
        # 3. ⭐ SI ES UN DOMINIO CONFIABLE → VÁLIDO INMEDIATAMENTE ⭐
        if domain in self.trusted_domains:
            result["valid"] = True
            result["buzon_existe"] = True
            result["reason"] = f"Dominio confiable ({domain})"
            logger.info(f"✅ Dominio confiable: {domain} - Email aceptado")
            return result
        
        # 4. Obtener registros MX (solo para dominios no confiables)
        mx_records = self.get_mx_records(domain)
        if not mx_records:
            result["reason"] = "No se encontraron servidores MX para el dominio"
            result["mx_records"] = []
            return result
        
        result["mx_records"] = mx_records
        
        # 5. Verificar buzón via SMTP (solo para dominios no confiables)
        smtp_result = self._verify_mailbox(email, domain, mx_records)
        result.update(smtp_result)
        
        return result
    
    def _verify_mailbox(self, email: str, domain: str, mx_records: List[Tuple[int, str]]) -> Dict:
        """
        Conectar al servidor SMTP y verificar si el buzón existe
        """
        result = {
            "valid": False,
            "reason": "",
            "smtp_response": "",
            "buzon_existe": False
        }
        
        # Solo probar el primer MX
        mx_hosts = [mx_records[0][1]]
        
        for mx_host in mx_hosts:
            try:
                logger.info(f"🔄 Conectando a {mx_host} para verificar {email}")
                
                with smtplib.SMTP(mx_host, 25, timeout=self.timeout) as server:
                    server.ehlo_or_helo_if_needed()
                    
                    try:
                        if server.has_extn('STARTTLS'):
                            server.starttls()
                            server.ehlo()
                    except:
                        pass
                    
                    code, response = server.mail(self.smtp_from)
                    logger.debug(f"MAIL FROM: {code} - {response}")
                    
                    if code not in [250, 251]:
                        result["smtp_response"] = f"MAIL FROM failed: {code} - {response}"
                        continue
                    
                    code, response = server.rcpt(email)
                    logger.debug(f"RCPT TO: {code} - {response}")
                    result["smtp_response"] = f"{code} - {response}"
                    
                    if code in [250, 251, 252]:
                        result["valid"] = True
                        result["buzon_existe"] = True
                        result["reason"] = "Buzón verificado y existe"
                        logger.info(f"✅ Buzón {email} existe en {mx_host}")
                        return result
                    elif code == 550:
                        result["valid"] = False
                        result["buzon_existe"] = False
                        result["reason"] = "El buzón no existe en este dominio"
                        logger.warning(f"❌ Buzón {email} NO existe en {mx_host}")
                        return result
                    elif code == 553:
                        result["valid"] = False
                        result["buzon_existe"] = False
                        result["reason"] = "Dirección de email inválida para este dominio"
                        return result
                    else:
                        logger.debug(f"⚠️ Respuesta inesperada {code}")
                        continue
                        
            except smtplib.SMTPConnectError as e:
                logger.warning(f"⚠️ No se pudo conectar a {mx_host}: {e}")
                continue
            except smtplib.SMTPServerDisconnected as e:
                logger.warning(f"⚠️ Servidor {mx_host} se desconectó: {e}")
                continue
            except smtplib.SMTPAuthenticationError as e:
                logger.warning(f"⚠️ Error de autenticación en {mx_host}: {e}")
                continue
            except smtplib.SMTPException as e:
                logger.warning(f"⚠️ Error SMTP en {mx_host}: {e}")
                continue
            except socket.timeout:
                logger.warning(f"⚠️ Timeout conectando a {mx_host}")
                continue
            except Exception as e:
                logger.warning(f"⚠️ Error inesperado en {mx_host}: {e}")
                continue
        
        # Si llegamos aquí, no se pudo verificar
        result["valid"] = False
        result["buzon_existe"] = False
        result["reason"] = "No se pudo verificar el buzón (servidores no responden)"
        
        return result
    
    def validate_email(self, email: str, strict: bool = True) -> Dict:
        """
        Validación completa de email
        """
        if not self.validate_format(email):
            return {
                "email": email,
                "valid": False,
                "format_valid": False,
                "reason": "Formato inválido",
                "domain": None,
                "mx_records": None,
                "buzon_existe": False,
                "suggestions": self._get_suggestions(email)
            }
        
        # Para dominios confiables, validación inmediata
        domain = self.get_domain(email)
        if domain and domain in self.trusted_domains:
            return {
                "email": email,
                "valid": True,
                "format_valid": True,
                "reason": f"Dominio confiable ({domain})",
                "domain": domain,
                "mx_records": None,
                "buzon_existe": True,
                "smtp_response": None,
                "suggestions": []
            }
        
        # Para otros dominios, hacer validación SMTP
        result = self.validate_email_smtp(email)
        
        return {
            "email": email,
            "valid": result.get("valid", False),
            "format_valid": result.get("format_valid", True),
            "reason": result.get("reason", ""),
            "domain": result.get("domain"),
            "mx_records": result.get("mx_records"),
            "buzon_existe": result.get("buzon_existe", False),
            "smtp_response": result.get("smtp_response"),
            "suggestions": self._get_suggestions(email)
        }
    
    def _get_suggestions(self, email: str) -> list:
        """Sugerencias para corregir el email"""
        suggestions = []
        
        common_domains = {
            'gamil.com': 'gmail.com',
            'gmil.com': 'gmail.com',
            'hotnail.com': 'hotmail.com',
            'hotmal.com': 'hotmail.com',
            'yaho.com': 'yahoo.com',
            'outlok.com': 'outlook.com',
            'protonmal.com': 'protonmail.com',
        }
        
        domain = self.get_domain(email)
        if domain and domain in common_domains:
            suggestions.append({
                "suggestion": email.replace(domain, common_domains[domain]),
                "reason": f"Dominio '{domain}' probablemente es '{common_domains[domain]}'"
            })
        
        return suggestions


# Instancia global
email_validator = EmailValidator()