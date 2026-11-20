"""m3_014: cleanup R13 - drop usuario_rol.control_base_id + indice redundante.

Items del diff: D-0004, D-0005, D-0016.
Deudas: orm.indice_redundante_contrato_vehiculo.

Cambios:
1. auth.usuario_rol.control_base_id: columna huerfana.
   - 0 filas con valor (verificado R13).
   - 0 referencias en codigo (verificado con git grep).
   - Comentario en ORM (# ELIMINADO) confirma decision previa (commit 2f93716).
   - FK fk_usuario_rol_control_base_id_control_base tambien se elimina.

2. fleet.ix_contrato_vehiculo_estado_contrato: indice redundante.
   - Definicion identica a fleet.idx_contrato_estado (btree, no unique, no partial).
   - Creado por error en migracion 182d55b83b69 (17 Ago 2026).
   - El ORM declara idx_contrato_estado como canonico (commit 58a47f0, R11).

Requiere backup DB previo (docs/backups/taxip_db_ronda13.dump).

Deuda orm.indice_redundante_contrato_vehiculo cerrada.
Ver docs/DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'm3_014'
down_revision = 'm3_013'
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------
    # Item 2: eliminar auth.usuario_rol.control_base_id (columna huerfana)
    # ------------------------------------------------------------
    op.execute("""
        ALTER TABLE auth.usuario_rol
        DROP CONSTRAINT IF EXISTS fk_usuario_rol_control_base_id_control_base
    """)
    op.execute("""
        ALTER TABLE auth.usuario_rol
        DROP COLUMN IF EXISTS control_base_id
    """)

    # ------------------------------------------------------------
    # Item 3: eliminar fleet.ix_contrato_vehiculo_estado_contrato (redundante)
    # ------------------------------------------------------------
    op.execute("""
        DROP INDEX IF EXISTS fleet.ix_contrato_vehiculo_estado_contrato
    """)


def downgrade():
    # ------------------------------------------------------------
    # Item 3 (reverso)
    # ------------------------------------------------------------
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_contrato_vehiculo_estado_contrato
        ON fleet.contrato_vehiculo(estado_contrato)
    """)

    # ------------------------------------------------------------
    # Item 2 (reverso)
    # ------------------------------------------------------------
    op.add_column(
        "usuario_rol",
        sa.Column("control_base_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="auth",
    )
    op.create_foreign_key(
        "fk_usuario_rol_control_base_id_control_base",
        "usuario_rol",
        "control_base",
        ["control_base_id"],
        ["id"],
        source_schema="auth",
        referent_schema="tenant",
        ondelete="SET NULL",
    )
