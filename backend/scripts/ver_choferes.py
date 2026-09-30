"""
Script temporal para ver los últimos choferes registrados.
"""
import asyncio
import sys
import os

# Agregar el directorio padre al path para poder importar 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT 
                u.id,
                u.email,
                cv.estado_aprobacion,
                u.created_at
            FROM auth.usuario u
            JOIN fleet.chofer_vehiculo cv ON cv.usuario_id = u.id
            ORDER BY u.created_at DESC
            LIMIT 5
        """))
        for row in result.all():
            print(dict(row._mapping))


if __name__ == "__main__":
    asyncio.run(check())