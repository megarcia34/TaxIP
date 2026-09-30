"""
Ver turnos activos.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def ver_turnos():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT 
                t.id,
                t.chofer_id,
                t.vehiculo_id,
                t.estado,
                t.inicio_turno,
                v.patente,
                u.email
            FROM fleet.turno_chofer t
            LEFT JOIN fleet.vehiculo v ON v.id = t.vehiculo_id
            LEFT JOIN auth.usuario u ON u.id = t.chofer_id
            WHERE t.estado = 'ACTIVO'
            ORDER BY t.inicio_turno DESC
        """))
        turnos = result.all()

        if not turnos:
            print("OK - No hay turnos activos")
            return

        print(f"Encontrados {len(turnos)} turnos activos:")
        print()
        for t in turnos:
            print(f"  Turno ID: {t[0]}")
            print(f"  Chofer: {t[6]} ({t[1]})")
            print(f"  Vehículo: {t[5]} ({t[2]})")
            print(f"  Inicio: {t[4]}")
            print()


if __name__ == "__main__":
    asyncio.run(ver_turnos())