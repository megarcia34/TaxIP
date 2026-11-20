"""M3-007: Motor unificado de tarifas TaxIP 2.1

Revision ID: m3_007
Revises: m3_006
Create Date: 2026-09-25

Cambios:
- Agrega 6 nuevas columnas a payment.configuracion_tarifa
- Crea tabla payment.configuracion_tarifa_vehiculo (factores por tipo de vehículo)
- Migra datos legacy según modo_calculo
- Limpia trip.tipo_vehiculo de valores tarifarios
- Inserta factores por defecto
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm3_007'
down_revision = 'm3_006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ================================================================
    # PASO 1: Nuevas columnas en payment.configuracion_tarifa
    # ================================================================
    op.add_column(
        'configuracion_tarifa',
        sa.Column('metros_por_ficha', sa.Numeric(), server_default='100', nullable=False),
        schema='payment'
    )
    op.add_column(
        'configuracion_tarifa',
        sa.Column('seg_por_ficha_espera', sa.Numeric(), server_default='60', nullable=False),
        schema='payment'
    )
    op.add_column(
        'configuracion_tarifa',
        sa.Column('velocidad_referencia_kmh', sa.Numeric(), server_default='30', nullable=False),
        schema='payment'
    )
    op.add_column(
        'configuracion_tarifa',
        sa.Column('velocidad_umbral_kmh', sa.Numeric(), server_default='15', nullable=False),
        schema='payment'
    )
    op.add_column(
        'configuracion_tarifa',
        sa.Column('modo_cobro_tiempo', sa.String(), server_default='detenido', nullable=False),
        schema='payment'
    )
    op.add_column(
        'configuracion_tarifa',
        sa.Column('redondeo_comercial', sa.Integer(), server_default='100', nullable=False),
        schema='payment'
    )

    # ================================================================
    # PASO 2: Crear tabla intermedia configuracion_tarifa_vehiculo
    # ================================================================
    op.create_table(
        'configuracion_tarifa_vehiculo',
        sa.Column('id', postgresql.UUID(as_uuid=True),
                  server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('configuracion_tarifa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_vehiculo_id', sa.String(), nullable=False),
        sa.Column('factor_precio', sa.Numeric(), server_default='1.0', nullable=False),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['configuracion_tarifa_id'],
            ['payment.configuracion_tarifa.id'],
            ondelete='CASCADE',
            name='fk_config_tarifa_vehiculo_config_tarifa'
        ),
        sa.ForeignKeyConstraint(
            ['tipo_vehiculo_id'],
            ['trip.tipo_vehiculo.id'],
            ondelete='CASCADE',
            name='fk_config_tarifa_vehiculo_tipo_vehiculo'
        ),
        sa.UniqueConstraint(
            'configuracion_tarifa_id', 'tipo_vehiculo_id',
            name='uq_config_tarifa_vehiculo'
        ),
        sa.PrimaryKeyConstraint('id'),
        schema='payment'
    )

    # ================================================================
    # PASO 3: Migración de datos según modo_calculo
    # ================================================================

    # 3a. Ficha Argentina: copiar distancia_por_ficha a metros_por_ficha
    op.execute("""
        UPDATE payment.configuracion_tarifa
        SET metros_por_ficha = COALESCE(distancia_por_ficha, 100),
            seg_por_ficha_espera = 60,
            modo_cobro_tiempo = 'detenido'
        WHERE modo_calculo = 'ficha_argentina'
          AND activo = true
    """)

    # 3b. Por KM: metros_por_ficha=1000, seg=0, copiar precio_por_km a precio_por_ficha
    op.execute("""
        UPDATE payment.configuracion_tarifa
        SET metros_por_ficha = 1000,
            seg_por_ficha_espera = 0,
            modo_cobro_tiempo = 'detenido',
            precio_por_ficha = COALESCE(precio_por_km, 0)
        WHERE modo_calculo = 'por_km'
          AND activo = true
    """)

    # 3c. Por Minuto: metros=0, seg=60, modo='total', copiar precio_por_minuto a precio_por_ficha
    op.execute("""
        UPDATE payment.configuracion_tarifa
        SET metros_por_ficha = 0,
            seg_por_ficha_espera = 60,
            modo_cobro_tiempo = 'total',
            precio_por_ficha = COALESCE(precio_por_minuto, 0)
        WHERE modo_calculo = 'por_minuto'
          AND activo = true
    """)

    # 3d. Mixto: metros=1000, seg=60, modo='detenido', copiar precio_por_km a precio_por_ficha
    op.execute("""
        UPDATE payment.configuracion_tarifa
        SET metros_por_ficha = 1000,
            seg_por_ficha_espera = 60,
            modo_cobro_tiempo = 'detenido',
            precio_por_ficha = COALESCE(precio_por_km, 0)
        WHERE modo_calculo = 'mixto'
          AND activo = true
    """)

    # 3e. Fallback: cualquier otra config que no tenga modo_calculo reconocido
    op.execute("""
        UPDATE payment.configuracion_tarifa
        SET metros_por_ficha = COALESCE(distancia_por_ficha, 100),
            seg_por_ficha_espera = 60,
            modo_cobro_tiempo = 'detenido'
        WHERE modo_calculo NOT IN ('ficha_argentina', 'por_km', 'por_minuto', 'mixto')
           OR modo_calculo IS NULL
    """)

    # ================================================================
    # PASO 4: Limpieza de trip.tipo_vehiculo
    # ================================================================
    op.execute("""
        UPDATE trip.tipo_vehiculo
        SET tarifa_base = 0,
            tarifa_por_km = 0,
            tarifa_por_minuto = 0,
            precio_por_ficha = 0,
            distancia_por_ficha = 0,
            precio_por_minuto_espera = 0
        WHERE activo = true
    """)

    # ================================================================
    # PASO 5: Insertar factores por defecto
    # ================================================================
    op.execute("""
        INSERT INTO payment.configuracion_tarifa_vehiculo
            (configuracion_tarifa_id, tipo_vehiculo_id, factor_precio)
        SELECT
            ct.id,
            tv.id,
            CASE
                WHEN tv.id = 'standard' THEN 1.0
                WHEN tv.id = 'premium' THEN 1.30
                WHEN tv.id = 'van' THEN 1.40
                WHEN tv.id = 'minivan' THEN 1.50
                ELSE 1.0
            END
        FROM payment.configuracion_tarifa ct
        CROSS JOIN trip.tipo_vehiculo tv
        WHERE ct.activo = true
          AND tv.activo = true
        ON CONFLICT (configuracion_tarifa_id, tipo_vehiculo_id)
        DO NOTHING
    """)


def downgrade() -> None:
    # ================================================================
    # REVERSO: eliminar factores por defecto
    # ================================================================
    op.execute("DELETE FROM payment.configuracion_tarifa_vehiculo")

    # ================================================================
    # REVERSO: eliminar tabla intermedia
    # ================================================================
    op.drop_table('configuracion_tarifa_vehiculo', schema='payment')

    # ================================================================
    # REVERSO: eliminar nuevas columnas
    # ================================================================
    op.drop_column('configuracion_tarifa', 'redondeo_comercial', schema='payment')
    op.drop_column('configuracion_tarifa', 'modo_cobro_tiempo', schema='payment')
    op.drop_column('configuracion_tarifa', 'velocidad_umbral_kmh', schema='payment')
    op.drop_column('configuracion_tarifa', 'velocidad_referencia_kmh', schema='payment')
    op.drop_column('configuracion_tarifa', 'seg_por_ficha_espera', schema='payment')
    op.drop_column('configuracion_tarifa', 'metros_por_ficha', schema='payment')

    # NOTA: No se restauran los valores de trip.tipo_vehiculo.
    # Si se necesita rollback real, usar backup previo a la migración.