

"""fundacion_autenticacion

Revision ID: 514f60fb4bab
Revises: 236d0eeac9d3
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '514f60fb4bab'
down_revision = '236d0eeac9d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 1. TABLA: auth.codigo_verificacion (OTP para validacion email)
    # ============================================================
    op.create_table(
        'codigo_verificacion',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('codigo', sa.String(6), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False, server_default='REGISTRO_CHOFER'),
        sa.Column('usado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('intentos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expira_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['auth.usuario.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='auth'
    )

    op.create_index('idx_codigo_verificacion_usuario_usado', 'codigo_verificacion',
                    ['usuario_id', 'usado'], schema='auth')
    op.create_index('idx_codigo_verificacion_expira', 'codigo_verificacion',
                    ['expira_en'], schema='auth')
    op.create_index('idx_codigo_verificacion_codigo', 'codigo_verificacion',
                    ['codigo'], schema='auth')

    # ============================================================
    # 2. TABLA: auth.prestadora_telefonica (Catalogo de operadoras)
    # ============================================================
    op.create_table(
        'prestadora_telefonica',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('codigo_pais', sa.String(10), nullable=True, server_default='+54'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
        schema='auth'
    )

    op.execute("""
        INSERT INTO auth.prestadora_telefonica (nombre, codigo_pais, activo) VALUES
        ('Movistar', '+54', true),
        ('Personal', '+54', true),
        ('Claro', '+54', true),
        ('Tuenti', '+54', true),
        ('Nextel', '+54', true),
        ('Gigared', '+54', true),
        ('Otro', '+54', true)
    """)

    # ============================================================
    # 3. MODIFICACION: fleet.chofer_vehiculo.estado_laboral
    # Cambiar default de 'libre' a 'fuera_servicio'
    # ============================================================
    op.alter_column('chofer_vehiculo', 'estado_laboral',
                    server_default='fuera_servicio',
                    schema='fleet')

    op.execute("""
        UPDATE fleet.chofer_vehiculo cv
        SET estado_laboral = 'fuera_servicio'
        WHERE cv.estado_laboral = 'libre'
          AND NOT EXISTS (
              SELECT 1 FROM fleet.turno_chofer tc
              WHERE tc.chofer_id = cv.usuario_id
                AND tc.estado = 'ACTIVO'
          )
    """)

    # ============================================================
    # 4. MODIFICACION: fleet.chofer_vehiculo.estado_aprobacion
    # Crear CHECK constraint con 'en_revision'
    # ============================================================
    op.create_check_constraint(
        'chk_estado_aprobacion',
        'chofer_vehiculo',
        "estado_aprobacion IN ('pendiente', 'en_revision', 'aprobado', 'rechazado')",
        schema='fleet'
    )


def downgrade() -> None:
    # 4. Eliminar constraint
    op.drop_constraint('chk_estado_aprobacion', 'chofer_vehiculo', schema='fleet', type_='check')

    # 3. Restaurar default 'libre'
    op.alter_column('chofer_vehiculo', 'estado_laboral',
                    server_default='libre',
                    schema='fleet')

    # 2. Eliminar tabla prestadoras
    op.drop_table('prestadora_telefonica', schema='auth')

    # 1. Eliminar tabla codigos verificacion
    op.drop_index('idx_codigo_verificacion_codigo', table_name='codigo_verificacion', schema='auth')
    op.drop_index('idx_codigo_verificacion_expira', table_name='codigo_verificacion', schema='auth')
    op.drop_index('idx_codigo_verificacion_usuario_usado', table_name='codigo_verificacion', schema='auth')
    op.drop_table('codigo_verificacion', schema='auth')