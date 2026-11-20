"""notificacion_vencimiento: agregar entidad_tipo vehiculo_taxi

Revision ID: m3_023
Revises: m3_022
Create Date: 2026-10-15
"""
from alembic import op


revision = 'm3_023'
down_revision = 'm3_022'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop del CHECK viejo
    op.execute("""
        ALTER TABLE fleet.notificacion_vencimiento
            DROP CONSTRAINT ck_notificacion_vencimiento_chk_notificacion_entidad_ti_fd97
    """)

    # 2. Nuevo CHECK con 'vehiculo_taxi'
    op.execute("""
        ALTER TABLE fleet.notificacion_vencimiento
            ADD CONSTRAINT ck_notificacion_vencimiento_chk_notificacion_entidad_ti_fd97
            CHECK (entidad_tipo IN (
                'propietario', 'vehiculo', 'chofer', 'vehiculo_taxi'
            ))
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE fleet.notificacion_vencimiento
            DROP CONSTRAINT ck_notificacion_vencimiento_chk_notificacion_entidad_ti_fd97
    """)

    op.execute("""
        ALTER TABLE fleet.notificacion_vencimiento
            ADD CONSTRAINT ck_notificacion_vencimiento_chk_notificacion_entidad_ti_fd97
            CHECK (entidad_tipo IN (
                'propietario', 'vehiculo', 'chofer'
            ))
    """)