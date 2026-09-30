"""
Script temporal para cambiar el estado de aprobación de un chofer.
"""
import asyncio
import sys
from app.database import AsyncSessionLocal
from sqlalchemy import text


async def cambiar_estado(user_id: str, nuevo_estado: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            UPDATE fleet.chofer_vehiculo
            SET estado_aprobacion = :estado, updated_at = NOW()
            WHERE usuario_id = :uid
        """), {"estado": nuevo_estado, "uid": user_id})
        await db.commit()
        print(f"OK - Estado cambiado a '{nuevo_estado}' para usuario {user_id}")
        print(f"Filas afectadas: {result.rowcount}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python cambiar_estado.py <user_id> <nuevo_estado>")
        print("Ejemplo: python cambiar_estado.py b811ee2f-51b1-41b4-8f8e-0bb3fa9e58d9 aprobado")
        sys.exit(1)

    user_id = sys.argv[1]
    nuevo_estado = sys.argv[2]
    asyncio.run(cambiar_estado(user_id, nuevo_estado))