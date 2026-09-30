"""
Script para probar el envío de email.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.email_sender import email_sender


async def test():
    destinatario = input("Email destinatario: ")
    codigo = "123456"

    print(f"Enviando código {codigo} a {destinatario}...")
    resultado = await email_sender.send_verification_code(destinatario, codigo)

    if resultado:
        print(f"✅ OK - Email enviado a {destinatario}")
        print("   Revisá tu bandeja de entrada (y spam)")
    else:
        print(f"❌ ERROR - No se pudo enviar el email")
        print("   Revisá los logs del backend para más detalles")


if __name__ == "__main__":
    asyncio.run(test())