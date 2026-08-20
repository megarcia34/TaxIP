"""add alquiler fields to contrato

Revision ID: 276dc5da658a
Revises: 8a991310d13c
Create Date: 2026-08-06 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

revision = '276dc5da658a'
down_revision = '8a991310d13c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─────────────────────────────────────────────────────────
    # 0. Eliminar constraints antiguos que bloquean la migración de datos
    # ─────────────────────────────────────────────────────────
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS check_monto")
    op.execute("ALTER TABLE fleet.contrato_vehiculo DROP CONSTRAINT IF EXISTS check_tipo_contrato")
    
    # ─────────────────────────────────────────────────────────
    # 1. Agregar nuevas columnas
    # ─────────────────────────────────────────────────────────
    op.add_column('contrato_vehiculo', sa.Column('canon_diario', sa.Numeric(10, 2), nullable=True), schema='fleet')
    op.add_column('contrato_vehiculo', sa.Column('km_incluidos_dia', sa.Numeric(10, 2), nullable=True), schema='fleet')
    op.add_column('contrato_vehiculo', sa.Column('valor_km_excedente', sa.Numeric(10, 2), nullable=True), schema='fleet')
    op.add_column('contrato_vehiculo', sa.Column('modalidad_computo', sa.String(20), server_default='DIARIO', nullable=False), schema='fleet')
    op.add_column('contrato_vehiculo', sa.Column('dias_contractuales', postgresql.JSONB, nullable=True), schema='fleet')
    op.add_column('contrato_vehiculo', sa.Column('tratamiento_dia_no_trabajado', sa.String(30), server_default='POR_DISPONIBILIDAD', nullable=False), schema='fleet')

    # ─────────────────────────────────────────────────────────
    # 2. CHECK constraints para integridad de datos (Nuevos)
    # ─────────────────────────────────────────────────────────
    op.create_check_constraint(
        'chk_contrato_modalidad_computo',
        'contrato_vehiculo',
        "modalidad_computo IN ('DIARIO', 'SEMANAL', 'MENSUAL')",
        schema='fleet'
    )
    op.create_check_constraint(
        'chk_contrato_tratamiento_dia',
        'contrato_vehiculo',
        "tratamiento_dia_no_trabajado IN ('POR_DISPONIBILIDAD', 'NO_COBRA', 'DESCUENTO_PROPORCIONAL')",
        schema='fleet'
    )
    
    # (Opcional) Si necesitas un nuevo constraint para tipo_contrato, descomenta esto:
    # op.create_check_constraint(
    #     'check_tipo_contrato',
    #     'contrato_vehiculo',
    #     "tipo_contrato IN ('ALQUILER', 'PORCENTUAL', 'MIXTO')",
    #     schema='fleet'
    # )

    # ─────────────────────────────────────────────────────────
    # 3. Migración de datos existentes
    # ─────────────────────────────────────────────────────────
    
    # 3.1 Convertir CANON_FIJO -> ALQUILER
    op.execute(text("""
        UPDATE fleet.contrato_vehiculo
        SET tipo_contrato = 'ALQUILER'
        WHERE tipo_contrato = 'CANON_FIJO'
    """))

    # 3.2 Poblar canon_diario con monto_diario (solo ALQUILER)
    op.execute(text("""
        UPDATE fleet.contrato_vehiculo
        SET canon_diario = monto_diario
        WHERE tipo_contrato = 'ALQUILER' AND monto_diario IS NOT NULL
    """))

    # 3.3 Asignar defaults para contratos ALQUILER históricos
    op.execute(text("""
        UPDATE fleet.contrato_vehiculo
        SET 
            km_incluidos_dia = COALESCE(km_incluidos_dia, 200),
            valor_km_excedente = COALESCE(valor_km_excedente, 200),
            modalidad_computo = COALESCE(modalidad_computo, 'DIARIO'),
            dias_contractuales = COALESCE(dias_contractuales, '["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]'::jsonb),
            tratamiento_dia_no_trabajado = COALESCE(tratamiento_dia_no_trabajado, 'POR_DISPONIBILIDAD')
        WHERE tipo_contrato = 'ALQUILER'
    """))

    # 3.4 Normalizar turnos: mañana -> DIURNO, tarde -> NOCTURNO, noche -> COMPLETO
    op.execute(text("""
        UPDATE fleet.contrato_vehiculo
        SET turno_asignado = 
            CASE turno_asignado
                WHEN 'mañana' THEN 'DIURNO'
                WHEN 'tarde'  THEN 'NOCTURNO'
                WHEN 'noche'  THEN 'COMPLETO'
                ELSE turno_asignado
            END
        WHERE turno_asignado IN ('mañana', 'tarde', 'noche')
    """))

    # 3.5 Sincronizar estado_contrato y activo
    op.execute(text("""
        UPDATE fleet.contrato_vehiculo
        SET estado_contrato = 
            CASE 
                WHEN activo = true AND fecha_fin IS NULL THEN 'ACTIVO'
                WHEN activo = false AND fecha_fin IS NOT NULL THEN 'FINALIZADO'
                ELSE estado_contrato
            END
    """))

    # 3.6 Asegurar que todos los contratos tengan un estado coherente
    op.execute(text("""
        UPDATE fleet.contrato_vehiculo
        SET activo = (estado_contrato = 'ACTIVO')
    """))


def downgrade() -> None:
    # 1. Eliminar CHECK constraints nuevos
    op.drop_constraint('chk_contrato_tratamiento_dia', 'contrato_vehiculo', schema='fleet')
    op.drop_constraint('chk_contrato_modalidad_computo', 'contrato_vehiculo', schema='fleet')
    
    # 2. Eliminar columnas en orden inverso
    op.drop_column('contrato_vehiculo', 'tratamiento_dia_no_trabajado', schema='fleet')
    op.drop_column('contrato_vehiculo', 'dias_contractuales', schema='fleet')
    op.drop_column('contrato_vehiculo', 'modalidad_computo', schema='fleet')
    op.drop_column('contrato_vehiculo', 'valor_km_excedente', schema='fleet')
    op.drop_column('contrato_vehiculo', 'km_incluidos_dia', schema='fleet')
    op.drop_column('contrato_vehiculo', 'canon_diario', schema='fleet')
    
    # Nota: Los constraints originales (check_monto, check_tipo_contrato) fueron eliminados 
    # en el upgrade. Si eran críticos, deberás recrearlos manualmente o agregarlos aquí.