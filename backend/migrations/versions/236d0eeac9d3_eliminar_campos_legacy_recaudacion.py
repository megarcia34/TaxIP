
"""eliminar_campos_legacy_recaudacion

Revision ID: [236d0eeac9d3]
Revises: cd27a5e41478
Create Date: 2026-08-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '236d0eeac9d3'
down_revision: Union[str, Sequence[str], None] = 'cd27a5e41478'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    ELIMINAR CAMPOS LEGACY DE RECAUDACIÓN Y LIQUIDACIÓN EN turno_chofer
    """
    
    # Eliminar campos de turno_chofer
    op.drop_column('turno_chofer', 'recaudacion_app_efectivo', schema='fleet')
    op.drop_column('turno_chofer', 'recaudacion_app_debito', schema='fleet')
    op.drop_column('turno_chofer', 'recaudacion_ticketera_calle', schema='fleet')
    op.drop_column('turno_chofer', 'monto_bruto_calculado', schema='fleet')
    op.drop_column('turno_chofer', 'comision_chofer_calculada', schema='fleet')
    op.drop_column('turno_chofer', 'utilidad_propietario_calculada', schema='fleet')


def downgrade() -> None:
    """
    REVERTIR: Restaurar campos legacy
    """
    
    op.add_column('turno_chofer', sa.Column('recaudacion_app_efectivo', sa.DECIMAL(12, 2), server_default='0', nullable=True), schema='fleet')
    op.add_column('turno_chofer', sa.Column('recaudacion_app_debito', sa.DECIMAL(12, 2), server_default='0', nullable=True), schema='fleet')
    op.add_column('turno_chofer', sa.Column('recaudacion_ticketera_calle', sa.DECIMAL(12, 2), server_default='0', nullable=True), schema='fleet')
    op.add_column('turno_chofer', sa.Column('monto_bruto_calculado', sa.DECIMAL(12, 2), server_default='0', nullable=True), schema='fleet')
    op.add_column('turno_chofer', sa.Column('comision_chofer_calculada', sa.DECIMAL(12, 2), server_default='0', nullable=True), schema='fleet')
    op.add_column('turno_chofer', sa.Column('utilidad_propietario_calculada', sa.DECIMAL(12, 2), server_default='0', nullable=True), schema='fleet')