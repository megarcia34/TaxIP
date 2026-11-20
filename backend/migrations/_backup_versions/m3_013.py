"""m3_013: agregar 5 UNIQUE constraints que el ORM declara y la DB no tiene.

Items del diff: D-0003, D-0005, D-0046, D-0057, D-0058.
Deuda: orm.unique_constraints_caso_c (Tier 1 + Tier 2).

La DB no tenia estos UNIQUEs, pero el ORM los declara. Verificado:
- 0 duplicados en las 5 columnas (R10 + reverificacion R12).
- auth.reset_token, tenant.configuracion_tenant y trip.calificacion
  estan vacias. auth.perfil_general (46 filas) y fleet.vehiculo (108
  filas) no tienen duplicados ni NULLs en las columnas afectadas.

Se agregan con el nombre canonico que el ORM ya declara.

Deuda orm.unique_constraints_caso_c (parcial: queda payment.metodo_pago).
Ver docs/DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op

revision = 'm3_013'
down_revision = 'm3_012'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE auth.perfil_general
        ADD CONSTRAINT uq_perfil_general_usuario_id
        UNIQUE (usuario_id)
    """)
    op.execute("""
        ALTER TABLE auth.reset_token
        ADD CONSTRAINT uq_reset_token_token
        UNIQUE (token)
    """)
    op.execute("""
        ALTER TABLE fleet.vehiculo
        ADD CONSTRAINT uq_vehiculo_qr_uuid
        UNIQUE (qr_uuid)
    """)
    op.execute("""
        ALTER TABLE tenant.configuracion_tenant
        ADD CONSTRAINT uq_configuracion_tenant_control_base_id
        UNIQUE (control_base_id)
    """)
    op.execute("""
        ALTER TABLE trip.calificacion
        ADD CONSTRAINT uq_calificacion_viaje_id
        UNIQUE (viaje_id)
    """)


def downgrade():
    op.execute("""
        ALTER TABLE trip.calificacion
        DROP CONSTRAINT uq_calificacion_viaje_id
    """)
    op.execute("""
        ALTER TABLE tenant.configuracion_tenant
        DROP CONSTRAINT uq_configuracion_tenant_control_base_id
    """)
    op.execute("""
        ALTER TABLE fleet.vehiculo
        DROP CONSTRAINT uq_vehiculo_qr_uuid
    """)
    op.execute("""
        ALTER TABLE auth.reset_token
        DROP CONSTRAINT uq_reset_token_token
    """)
    op.execute("""
        ALTER TABLE auth.perfil_general
        DROP CONSTRAINT uq_perfil_general_usuario_id
    """)