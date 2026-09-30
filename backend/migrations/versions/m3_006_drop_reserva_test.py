"""M3-006: DROP trip.reserva (solo si son datos de prueba confirmados)

Revision ID: m3_006
Revises: m3_005
Create Date: 2026-09-15
"""
from alembic import op

revision = 'm3_006'
down_revision = 'm3_005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Guardia de seguridad: solo corre si hay <=10 filas
    op.execute("""
        DO $$
        DECLARE n INTEGER;
        BEGIN
            SELECT COUNT(*) INTO n FROM trip.reserva;
            IF n > 10 THEN
                RAISE EXCEPTION 'trip.reserva tiene % filas (>10). Abortando drop. Revisar con negocio.', n;
            END IF;
        END $$;
    """)
    op.execute("DROP TABLE IF EXISTS trip.reserva CASCADE;")


def downgrade() -> None:
    # No recreamos: era legacy. Si se necesita, restaurar desde backup.
    pass
