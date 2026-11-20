

"""add neumaticos configuracion tenant

Revision ID: 0763554a29cf
Revises: 4d93c605fb25
Create Date: 2026-08-01
"""
from alembic import op
import sqlalchemy as sa

revision = '0763554a29cf'
down_revision = '4d93c605fb25'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar las 5 columnas de configuración de neumáticos
    op.add_column(
        'configuracion_tenant', 
        sa.Column('vida_util_neumaticos_km', sa.Integer(), server_default='50000', nullable=True), 
        schema='tenant'
    )
    op.add_column(
        'configuracion_tenant', 
        sa.Column('umbral_rotacion_neumaticos_km', sa.Integer(), server_default='10000', nullable=True), 
        schema='tenant'
    )
    op.add_column(
        'configuracion_tenant', 
        sa.Column('umbral_cambio_neumaticos_km', sa.Integer(), server_default='45000', nullable=True), 
        schema='tenant'
    )
    op.add_column(
        'configuracion_tenant', 
        sa.Column('profundidad_minima_neumaticos_mm', sa.Numeric(3, 1), server_default='2.0', nullable=True), 
        schema='tenant'
    )
    op.add_column(
        'configuracion_tenant', 
        sa.Column('factor_desgaste_delantero', sa.Numeric(3, 2), server_default='1.5', nullable=True), 
        schema='tenant'
    )

    # Agregar comentarios para documentar el propósito de cada columna
    op.execute("""
        COMMENT ON COLUMN tenant.configuracion_tenant.vida_util_neumaticos_km IS 'Kilómetros estimados de vida útil total de un neumático';
        COMMENT ON COLUMN tenant.configuracion_tenant.umbral_rotacion_neumaticos_km IS 'Kilómetros sugeridos para realizar una rotación de neumáticos';
        COMMENT ON COLUMN tenant.configuracion_tenant.umbral_cambio_neumaticos_km IS 'Kilómetros sugeridos para el cambio preventivo de neumáticos';
        COMMENT ON COLUMN tenant.configuracion_tenant.profundidad_minima_neumaticos_mm IS 'Profundidad mínima del dibujo en mm antes de requerir cambio obligatorio';
        COMMENT ON COLUMN tenant.configuracion_tenant.factor_desgaste_delantero IS 'Multiplicador de desgaste para neumáticos delanteros vs traseros (ej: 1.5 = 50% más desgaste)';
    """)


def downgrade() -> None:
    # Eliminar las columnas en orden inverso
    op.drop_column('configuracion_tenant', 'factor_desgaste_delantero', schema='tenant')
    op.drop_column('configuracion_tenant', 'profundidad_minima_neumaticos_mm', schema='tenant')
    op.drop_column('configuracion_tenant', 'umbral_cambio_neumaticos_km', schema='tenant')
    op.drop_column('configuracion_tenant', 'umbral_rotacion_neumaticos_km', schema='tenant')
    op.drop_column('configuracion_tenant', 'vida_util_neumaticos_km', schema='tenant')