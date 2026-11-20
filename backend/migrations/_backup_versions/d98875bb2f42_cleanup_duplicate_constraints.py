
"""remove duplicate constraints from contrato_vehiculo

Revision ID: d98875bb2f42
Revises: 182d55b83b69
Create Date: 2026-08-17 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'd98875bb2f42'
down_revision: Union[str, None] = '182d55b83b69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eliminar constraints viejos y conflictivos
    op.execute("""
        DO $$
        BEGIN
            -- Eliminar chk_modalidad_computo (viejo, más restrictivo)
            IF EXISTS (
                SELECT 1 FROM information_schema.check_constraints 
                WHERE constraint_name = 'chk_modalidad_computo'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                DROP CONSTRAINT chk_modalidad_computo;
            END IF;
            
            -- Eliminar chk_tratamiento_dia (viejo, valores diferentes)
            IF EXISTS (
                SELECT 1 FROM information_schema.check_constraints 
                WHERE constraint_name = 'chk_tratamiento_dia'
            ) THEN
                ALTER TABLE fleet.contrato_vehiculo 
                DROP CONSTRAINT chk_tratamiento_dia;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Restaurar constraints viejos si es necesario
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo 
        ADD CONSTRAINT chk_modalidad_computo 
        CHECK (modalidad_computo IN ('DIARIO', 'SEMANAL') OR modalidad_computo IS NULL);
    """)
    
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo 
        ADD CONSTRAINT chk_tratamiento_dia 
        CHECK (tratamiento_dia_no_trabajado IN ('POR_DISPONIBILIDAD', 'POR_USO_EFECTIVO') OR tratamiento_dia_no_trabajado IS NULL);
    """)