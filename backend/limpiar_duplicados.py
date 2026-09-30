"""
Script para limpiar duplicados en fleet.chofer_vehiculo.
Mantiene solo la fila más reciente por usuario.
"""
import asyncio
import sys
import os

# Agregar el directorio padre al path para poder importar 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def limpiar():
    async with AsyncSessionLocal() as db:
        # Ver duplicados primero
        result = await db.execute(text("""
            SELECT usuario_id, COUNT(*) as total
            FROM fleet.chofer_vehiculo
            GROUP BY usuario_id
            HAVING COUNT(*) > 1
        """))
        duplicados = result.all()

        if not duplicados:
            print("OK - No hay duplicados")
            return

        print(f"Encontrados {len(duplicados)} usuarios con duplicados:")
        for row in duplicados:
            print(f"  Usuario {row[0]}: {row[1]} filas")

        # Eliminar duplicados manteniendo el más reciente
        result = await db.execute(text("""
            DELETE FROM fleet.chofer_vehiculo
            WHERE id NOT IN (
                SELECT DISTINCT ON (usuario_id) id
                FROM fleet.chofer_vehiculo
                ORDER BY usuario_id, created_at DESC
            )
        """))
        await db.commit()
        print(f"OK - Filas eliminadas: {result.rowcount}")

        # Verificar
        result = await db.execute(text("""
            SELECT usuario_id, COUNT(*) as total
            FROM fleet.chofer_vehiculo
            GROUP BY usuario_id
            HAVING COUNT(*) > 1
        """))
        restantes = result.all()
        if restantes:
            print(f"ATENCION - Aun hay {len(restantes)} usuarios con duplicados")
        else:
            print("OK - Todos los duplicados eliminados")


if __name__ == "__main__":
    asyncio.run(limpiar())