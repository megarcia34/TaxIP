


"""documento vehiculo campos detallados

Revision ID: '390dc56c9bea'
Revises: e4d29503431d
Create Date: 2026-07-30
"""
from alembic import op
import sqlalchemy as sa

revision = '390dc56c9bea'
down_revision = 'e4d29503431d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Datos generales del vehículo ──
    op.add_column('documento_vehiculo', sa.Column('marca', sa.String(50), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('modelo', sa.String(50), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('tipo_vehiculo', sa.String(50), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('uso', sa.String(30), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('chasis', sa.String(30), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('motor', sa.String(30), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('dominio', sa.String(20), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('vtv_fecha_vencimiento', sa.Date(), nullable=True), schema='fleet')

    # ── Datos del seguro ──
    op.add_column('documento_vehiculo', sa.Column('seguro_compania', sa.String(100), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('seguro_poliza', sa.String(50), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('seguro_fecha_emision', sa.Date(), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('seguro_fecha_vencimiento', sa.Date(), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('seguro_cobertura', sa.String(100), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('seguro_suma_asegurada', sa.String(50), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('seguro_tomador', sa.String(100), nullable=True), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('seguro_vehiculo', sa.String(50), nullable=True), schema='fleet')


def downgrade() -> None:
    op.drop_column('documento_vehiculo', 'seguro_vehiculo', schema='fleet')
    op.drop_column('documento_vehiculo', 'seguro_tomador', schema='fleet')
    op.drop_column('documento_vehiculo', 'seguro_suma_asegurada', schema='fleet')
    op.drop_column('documento_vehiculo', 'seguro_cobertura', schema='fleet')
    op.drop_column('documento_vehiculo', 'seguro_fecha_vencimiento', schema='fleet')
    op.drop_column('documento_vehiculo', 'seguro_fecha_emision', schema='fleet')
    op.drop_column('documento_vehiculo', 'seguro_poliza', schema='fleet')
    op.drop_column('documento_vehiculo', 'seguro_compania', schema='fleet')
    op.drop_column('documento_vehiculo', 'vtv_fecha_vencimiento', schema='fleet')
    op.drop_column('documento_vehiculo', 'dominio', schema='fleet')
    op.drop_column('documento_vehiculo', 'motor', schema='fleet')
    op.drop_column('documento_vehiculo', 'chasis', schema='fleet')
    op.drop_column('documento_vehiculo', 'uso', schema='fleet')
    op.drop_column('documento_vehiculo', 'tipo_vehiculo', schema='fleet')
    op.drop_column('documento_vehiculo', 'modelo', schema='fleet')
    op.drop_column('documento_vehiculo', 'marca', schema='fleet')