"""
Script de auditoría para contratos
Ejecutar: python auditar_contratos.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import DATABASE_URL

async def audit():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.connect() as conn:
        print("=" * 80)
        print("🔍 AUDITORÍA DE CONTRATOS - TAXIP")
        print("=" * 80)
        
        # 1. Estructura de la tabla
        print("\n📋 ESTRUCTURA DE fleet.contrato_vehiculo:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_schema = 'fleet' 
              AND table_name = 'contrato_vehiculo'
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"  {row[0]:<30} | {row[1]:<20} | nullable: {row[2]}")

        # 2. Índices
        print("\n📊 ÍNDICES:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE schemaname = 'fleet' 
              AND tablename = 'contrato_vehiculo'
        """))
        for row in result:
            print(f"  {row[0]}")
            print(f"    {row[1][:100]}...")

        # 3. Constraints (valores actuales)
        print("\n🔒 CONSTRAINTS ACTUALES:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT conname, contype, convalidated, pg_get_constraintdef(oid) as def
            FROM pg_constraint 
            WHERE conrelid = 'fleet.contrato_vehiculo'::regclass
            ORDER BY conname
        """))
        for row in result:
            print(f"  {row[0]} | tipo: {row[1]} | validado: {row[2]}")
            print(f"    {row[3][:150]}")

        # 4. Verificar `relacion_propietario_vehiculo`
        print("\n📊 fleet.relacion_propietario_vehiculo:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN activo = true THEN 1 END) as activos
            FROM fleet.relacion_propietario_vehiculo
        """))
        row = result.first()
        print(f"  Total registros: {row[0]}")
        print(f"  Activos: {row[1]}")

        # 5. Verificar consistencia de chofer_vehiculo
        print("\n📊 fleet.chofer_vehiculo (muestra):")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT 
                cv.usuario_id::text,
                cv.vehiculo_id::text,
                cv.control_base_id::text,
                c.estado_contrato,
                c.activo as contrato_activo
            FROM fleet.chofer_vehiculo cv
            LEFT JOIN fleet.contrato_vehiculo c 
                ON c.chofer_id = cv.usuario_id 
                AND c.activo = true
            WHERE cv.vehiculo_id IS NOT NULL
            LIMIT 5
        """))
        for row in result:
            estado = row[3] if row[3] else 'NULL'
            print(f"  usuario: {row[0][:8]}... | vehiculo: {row[1][:8]}... | estado: {estado}")

        # 6. Contratos con estado inconsistente
        print("\n⚠️ VERIFICANDO CONSISTENCIA DE ESTADOS:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT id::text, estado_contrato, activo, fecha_fin
            FROM fleet.contrato_vehiculo
            WHERE (estado_contrato = 'ACTIVO' AND activo = false)
               OR (estado_contrato = 'FINALIZADO' AND activo = true)
        """))
        rows = result.all()
        if rows:
            print("⚠️  CONTRATOS CON ESTADO INCONSISTENTE:")
            for row in rows:
                print(f"  ID: {row[0][:8]}... | estado: {row[1]} | activo: {row[2]} | fecha_fin: {row[3]}")
        else:
            print("✅ No hay contratos con estado inconsistente")

        # 7. Contratos ALQUILER con parámetros faltantes
        print("\n⚠️ VERIFICANDO PARÁMETROS DE ALQUILER:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT id::text, tipo_contrato, canon_diario, km_incluidos_dia, valor_km_excedente, estado_contrato
            FROM fleet.contrato_vehiculo
            WHERE tipo_contrato = 'ALQUILER' 
              AND (canon_diario IS NULL OR km_incluidos_dia IS NULL OR valor_km_excedente IS NULL)
              AND estado_contrato = 'ACTIVO'
        """))
        rows = result.all()
        if rows:
            print("⚠️  CONTRATOS ALQUILER ACTIVOS CON PARÁMETROS FALTANTES:")
            for row in rows:
                print(f"  ID: {row[0][:8]}... | canon: {row[2]} | km: {row[3]} | excedente: {row[4]}")
        else:
            print("✅ Todos los contratos ALQUILER activos tienen parámetros completos")

        # 8. Conflictos potenciales (mismo turno)
        print("\n⚠️ VERIFICANDO CONFLICTOS DE TURNO:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT 
                vehiculo_id::text,
                turno_asignado,
                COUNT(*) as cantidad
            FROM fleet.contrato_vehiculo
            WHERE estado_contrato = 'ACTIVO'
            GROUP BY vehiculo_id, turno_asignado
            HAVING COUNT(*) > 1
            LIMIT 5
        """))
        rows = result.all()
        if rows:
            print("⚠️  VEHÍCULOS CON MÚLTIPLES CONTRATOS ACTIVOS EN MISMO TURNO:")
            for row in rows:
                print(f"  Vehículo: {row[0][:8]}... | turno: {row[1]} | cantidad: {row[2]}")
        else:
            print("✅ No hay vehículos con conflictos de turno")

        # 9. Verificar turnos normalizados
        print("\n⚠️ VERIFICANDO TURNOS NORMALIZADOS:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT DISTINCT turno_asignado, COUNT(*) as cantidad
            FROM fleet.contrato_vehiculo
            GROUP BY turno_asignado
        """))
        print("  Turnos existentes:")
        for row in result:
            print(f"    {row[0]} | cantidad: {row[1]}")

        # 10. Verificar modalidad_computo
        print("\n⚠️ VERIFICANDO MODALIDAD_COMPUTO:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT DISTINCT modalidad_computo, COUNT(*) as cantidad
            FROM fleet.contrato_vehiculo
            GROUP BY modalidad_computo
        """))
        print("  Modalidades existentes:")
        for row in result:
            print(f"    {row[0]} | cantidad: {row[1]}")

        # 11. Resumen general
        print("\n" + "=" * 80)
        print("📊 RESUMEN GENERAL:")
        print("-" * 60)
        result = await conn.execute(text("""
            SELECT 
                tipo_contrato,
                estado_contrato,
                COUNT(*) as cantidad
            FROM fleet.contrato_vehiculo
            GROUP BY tipo_contrato, estado_contrato
            ORDER BY tipo_contrato, estado_contrato
        """))
        print("  Por tipo y estado:")
        for row in result:
            print(f"    {row[0]:<15} | {row[1]:<25} | {row[2]}")

        # 12. Valores no esperados
        print("\n⚠️ VALORES NO ESPERADOS:")
        print("-" * 60)
        
        # Modalidad computo con MENSUAL
        result = await conn.execute(text("""
            SELECT COUNT(*) FROM fleet.contrato_vehiculo WHERE modalidad_computo = 'MENSUAL'
        """))
        count = result.scalar()
        if count > 0:
            print(f"  ❌ modalidad_computo = 'MENSUAL': {count} registros")
        else:
            print("  ✅ modalidad_computo: solo DIARIO/SEMANAL")
        
        # Tratamiento con NO_COBRA o DESCUENTO_PROPORCIONAL
        result = await conn.execute(text("""
            SELECT COUNT(*) FROM fleet.contrato_vehiculo 
            WHERE tratamiento_dia_no_trabajado NOT IN ('POR_DISPONIBILIDAD', 'POR_USO_EFECTIVO')
        """))
        count = result.scalar()
        if count > 0:
            print(f"  ❌ tratamiento_dia_no_trabajado inválido: {count} registros")
        else:
            print("  ✅ tratamiento_dia_no_trabajado: solo POR_DISPONIBILIDAD/POR_USO_EFECTIVO")

        print("\n" + "=" * 80)
        print("✅ AUDITORÍA COMPLETADA")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(audit())