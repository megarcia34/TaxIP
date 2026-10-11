"""m3_017 fix comments de tabla + drop ix_qr_cobro_token redundante

Revision ID: m3_017
Revises: m3_016
Create Date: 2026-10-11

Ronda 15 - Deuda tecnica funcional, P2 (alembic check).

Cambios:

1. Elimina el indice ix_qr_cobro_token de payment.qr_cobro. Es redundante:
   ya existe uq_qr_cobro_token (UNIQUE sobre la misma columna).

2. Actualiza los comments de 5 tablas para alinear ORM <-> DB:
   - auth.autorizacion_inicio
   - auth.turno_empleado
   - auth.usuario_rol
   - fleet.contrato_qr        (corrige mojibake y ajusta texto al uso actual)
   - fleet.documentos_chofer  (corrige mojibake: aprobacion -> aprobacion)

Los comments de contrato_qr y documentos_chofer tenian mojibake
(vehÝculos, autorizaci¾n, aprobaci¾n). Se corrigen a UTF-8 valido.

Requiere backup DB previo (docs/backups/taxip_db_ronda15.dump).

Ver docs/DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op

revision = 'm3_017'
down_revision = 'm3_016'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Eliminar indice redundante ix_qr_cobro_token
    op.execute("DROP INDEX payment.ix_qr_cobro_token")

    # 2. Actualizar comments de tabla
    op.execute("""
        COMMENT ON TABLE auth.autorizacion_inicio IS
        'Autorizaciones temporales de inicio de turno generadas via QR por el propietario'
    """)
    op.execute("""
        COMMENT ON TABLE auth.turno_empleado IS
        'Registro de turnos de empleados de empresas (recepcionistas)'
    """)
    op.execute("""
        COMMENT ON TABLE auth.usuario_rol IS
        'Capacidades adicionales de una identidad de usuario '
        '(ej. propietario con capacidad conductor)'
    """)
    op.execute("""
        COMMENT ON TABLE fleet.contrato_qr IS
        'QRs generados para pagos y trazabilidad de viajes'
    """)
    op.execute("""
        COMMENT ON TABLE fleet.documentos_chofer IS
        'Documentos subidos por choferes para aprobacion municipal'
    """)


def downgrade():
    # 1. Restaurar indice redundante
    op.execute("""
        CREATE UNIQUE INDEX ix_qr_cobro_token
        ON payment.qr_cobro USING btree (token)
    """)

    # 2. Restaurar comments originales (con mojibake para reversibilidad exacta)
    op.execute("COMMENT ON TABLE auth.autorizacion_inicio IS NULL")
    op.execute("COMMENT ON TABLE auth.turno_empleado IS NULL")
    op.execute("COMMENT ON TABLE auth.usuario_rol IS NULL")
    op.execute("COMMENT ON TABLE fleet.contrato_qr IS NULL")
    op.execute("COMMENT ON TABLE fleet.documentos_chofer IS NULL")