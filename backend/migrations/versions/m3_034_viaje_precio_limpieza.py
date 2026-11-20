"""m3_034: limpieza de datos sucios de precio_final

Revision ID: m3_034
Revises: m3_033

Responsabilidad unica: corregir precio_final inconsistente con el estado.
En VPS es no-op (0 cancelados con precio, 0 finalizados sin precio),
pero se aplica para mantener la cadena de migraciones consistente.
"""
from alembic import op

revision = 'm3_034'
down_revision = 'm3_033'
branch_labels = None
depends_on = None


def upgrade():
    # Snapshot de auditoria ANTES de tocar (rollback selectivo)
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit._backup_m3_034 AS
        SELECT id, estado, precio_estimado, precio_final, cancelado_en
        FROM trip.viaje_solicitado
        WHERE (estado = 'cancelado' AND precio_final > 0)
           OR (estado = 'finalizado' AND precio_final IS NULL);
    """)

    # 1. Cancelados: precio_final = 0 (no generan ingreso)
    op.execute("""
        UPDATE trip.viaje_solicitado
        SET precio_final = 0
        WHERE estado = 'cancelado' AND precio_final > 0;
    """)

    # 2. Finalizados sin precio: backfill desde precio_estimado, o 0 si tambien es NULL
    op.execute("""
        UPDATE trip.viaje_solicitado
        SET precio_final = COALESCE(precio_estimado, 0)
        WHERE estado = 'finalizado' AND precio_final IS NULL;
    """)


def downgrade():
    op.execute("""
        UPDATE trip.viaje_solicitado vs
        SET precio_final = b.precio_final
        FROM audit._backup_m3_034 b
        WHERE vs.id = b.id;
    """)
    op.execute("DROP TABLE IF EXISTS audit._backup_m3_034;")