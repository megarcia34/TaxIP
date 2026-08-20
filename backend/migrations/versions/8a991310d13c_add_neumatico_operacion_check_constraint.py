"""add neumatico operacion check constraint

Revision ID: 8a991310d13c
Revises: 0763554a29cf
Create Date: 2026-08-01
"""
from alembic import op

revision = '8a991310d13c'
down_revision = '0763554a29cf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Eliminar el constraint viejo si existe (para evitar errores de duplicado)
    op.execute("""
        ALTER TABLE fleet.neumatico_operacion 
        DROP CONSTRAINT IF EXISTS ck_neumatico_operacion_chk_operacion_tipo
    """)
    
    # 2. Agregar el constraint nuevo con todos los valores actualizados
    op.execute("""
        ALTER TABLE fleet.neumatico_operacion 
        ADD CONSTRAINT ck_neumatico_operacion_chk_operacion_tipo 
        CHECK (tipo_operacion IN ('MONTAJE', 'DESMONTAJE', 'ROTACION', 'REPARACION', 'ALINEACION', 'BALANCEO', 'INVENTARIO', 'OTRO', 'CAMBIO', 'DESECHO'))
    """)


def downgrade() -> None:
    # Eliminar el constraint en el downgrade
    op.execute("""
        ALTER TABLE fleet.neumatico_operacion 
        DROP CONSTRAINT IF EXISTS ck_neumatico_operacion_chk_operacion_tipo
    """)