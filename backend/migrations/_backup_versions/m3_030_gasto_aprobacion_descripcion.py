"""conciliacion: agregar estado_aprobacion y descripcion a gasto_turno

Revision ID: m3_030
Revises: m3_029
Create Date: 2026-11-02

Agrega:
- Columna estado_aprobacion VARCHAR(20) DEFAULT 'pendiente' a fleet.gasto_turno
- Columna descripcion TEXT a fleet.gasto_turno
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'm3_030'
down_revision: Union[str, None] = 'm3_029'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Cambio estructural 1
    op.execute("""
        ALTER TABLE fleet.gasto_turno
        ADD COLUMN IF NOT EXISTS estado_aprobacion VARCHAR(20) DEFAULT 'pendiente'
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.gasto_turno.estado_aprobacion
        IS 'Estado de aprobacion del gasto por parte del propietario: pendiente, aprobado, rechazado'
    """)
    
    # Cambio estructural 2
    op.execute("""
        ALTER TABLE fleet.gasto_turno
        ADD COLUMN IF NOT EXISTS descripcion TEXT
    """)

def downgrade() -> None:
    op.execute("""
        ALTER TABLE fleet.gasto_turno
        DROP COLUMN IF EXISTS estado_aprobacion
    """)
    op.execute("""
        ALTER TABLE fleet.gasto_turno
        DROP COLUMN IF EXISTS descripcion
    """)