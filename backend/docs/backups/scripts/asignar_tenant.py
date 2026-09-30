import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import DATABASE_URL

async def update_tenant():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        # Verificar estado actual del chofer
        result = await conn.execute(text("""
            SELECT u.id::text, u.email, u.control_base_id::text, tu.nombre
            FROM auth.usuario u
            JOIN auth.tipo_usuario tu ON tu.id = u.tipo_usuario_id
            WHERE u.email = 'chofer1@taxip.com'
        """))
        row = result.first()
        if row:
            print(f'📋 Antes: {row[0][:8]}... | {row[1]} | tenant: {row[2] if row[2] else "NULL"} | rol: {row[3]}')
        
        # Actualizar tenant
        result = await conn.execute(text("""
            UPDATE auth.usuario
            SET control_base_id = (SELECT control_base_id FROM auth.usuario WHERE email = 'propietario.conductor2@taxip.com')
            WHERE email = 'chofer1@taxip.com'
            RETURNING id::text
        """))
        await conn.commit()
        row = result.first()
        if row:
            print(f'✅ Tenant actualizado para chofer: {row[0][:8]}...')
        
        # Verificar después
        result = await conn.execute(text("""
            SELECT u.id::text, u.email, u.control_base_id::text, tu.nombre
            FROM auth.usuario u
            JOIN auth.tipo_usuario tu ON tu.id = u.tipo_usuario_id
            WHERE u.email = 'chofer1@taxip.com'
        """))
        row = result.first()
        if row:
            print(f'📋 Después: {row[0][:8]}... | {row[1]} | tenant: {row[2] if row[2] else "NULL"} | rol: {row[3]}')

asyncio.run(update_tenant())