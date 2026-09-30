"""
Cerrar TODOS los turnos activos (para testing).
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def cerrar_todos():
    async with AsyncSessionLocal() as db:
        # Cerrar turnos
        result = await db.execute(text("""
            UPDATE fleet.turno_chofer
            SET estado = 'CERRADO',
                fin_turno = NOW(),
                km_final = km_inicial + 100,
                combustible_final = 'LLENO',
                updated_at = NOW()
            WHERE estado = 'ACTIVO'
        """))
        await db.commit()
        print(f"✅ Turnos cerrados: {result.rowcount}")

        # Limpiar estado laboral de choferes
        result = await db.execute(text("""
            UPDATE fleet.chofer_vehiculo
            SET estado_laboral = 'fuera_servicio',
                updated_at = NOW()
            WHERE estado_laboral IN ('libre', 'ocupado')
        """))
        await db.commit()
        print(f"✅ Choferes reseteados: {result.rowcount}")


if __name__ == "__main__":
    asyncio.run(cerrar_todos())