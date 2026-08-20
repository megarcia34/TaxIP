


"""Add neumaticos tables

Revision ID: 4d93c605fb25
Revises: 2a49bcd3e516
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '4d93c605fb25'
down_revision = '2a49bcd3e516'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─────────────────────────────────────────────────────────
    # 1. Tabla: neumatico_vehiculo (catálogo de neumáticos)
    # ─────────────────────────────────────────────────────────
    op.create_table(
        'neumatico_vehiculo',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vehiculo_id', UUID(as_uuid=True), nullable=False),
        sa.Column('control_base_id', UUID(as_uuid=True), nullable=False),
        sa.Column('codigo_interno', sa.String(20), nullable=False),
        sa.Column('marca', sa.String(50), nullable=False),
        sa.Column('modelo_dibujo', sa.String(50), nullable=True),
        sa.Column('medida', sa.String(20), nullable=True),
        sa.Column('tipo_neumatico', sa.String(20), nullable=False),
        sa.Column('fecha_fabricacion', sa.Date(), nullable=True),
        sa.Column('estado', sa.String(20), nullable=False, server_default='ACTIVO'),
        sa.Column('km_totales_acumulados', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('fecha_alta', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_baja', sa.DateTime(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_neumatico_vehiculo')),
        sa.CheckConstraint(
            "estado IN ('ACTIVO','EN_USO','DESBASTADO','RECICLADO','DESECHADO','BAJA')",
            name='chk_neumatico_estado'
        ),
        sa.CheckConstraint(
            "tipo_neumatico IN ('RADIAL','BIAS','TUBELESS','RUN_FLAT','TODO_TERRENO')",
            name='chk_neumatico_tipo'
        ),
        sa.UniqueConstraint('control_base_id', 'codigo_interno', name='uq_neumatico_codigo_interno'),
        schema='fleet'
    )

    op.create_index('idx_neumatico_vehiculo_vehiculo', 'neumatico_vehiculo', ['vehiculo_id'], schema='fleet')
    op.create_index('idx_neumatico_vehiculo_control_base', 'neumatico_vehiculo', ['control_base_id'], schema='fleet')
    op.create_index('idx_neumatico_vehiculo_estado', 'neumatico_vehiculo', ['estado'], schema='fleet')
    op.create_index('idx_neumatico_vehiculo_codigo', 'neumatico_vehiculo', ['codigo_interno'], schema='fleet')

    op.create_foreign_key('fk_neumatico_vehiculo_vehiculo', 'neumatico_vehiculo', 'vehiculo',
                          ['vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')
    op.create_foreign_key('fk_neumatico_vehiculo_control_base', 'neumatico_vehiculo', 'control_base',
                          ['control_base_id'], ['id'], source_schema='fleet', referent_schema='tenant')

    # ─────────────────────────────────────────────────────────
    # 2. Tabla: neumatico_operacion (rotación, montaje, desmontaje, etc.)
    #    Se crea ANTES que historial_posicion porque esta última la referencia
    # ─────────────────────────────────────────────────────────
    op.create_table(
        'neumatico_operacion',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vehiculo_id', UUID(as_uuid=True), nullable=False),
        sa.Column('control_base_id', UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_operacion', sa.String(30), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('km_vehiculo_actual', sa.Integer(), nullable=False),
        sa.Column('fecha_operacion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('costo', sa.Numeric(10, 2), nullable=True),
        sa.Column('moneda', sa.String(3), nullable=True, server_default='ARS'),
        sa.Column('proveedor', sa.String(100), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('creado_por', UUID(as_uuid=True), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_neumatico_operacion')),
        sa.CheckConstraint(
            "tipo_operacion IN ('MONTAJE','DESMONTAJE','ROTACION','REPARACION','ALINEACION','BALANCEO','INVENTARIO','OTRO')",
            name='chk_operacion_tipo'
        ),
        schema='fleet'
    )

    op.create_index('idx_operacion_vehiculo', 'neumatico_operacion', ['vehiculo_id'], schema='fleet')
    op.create_index('idx_operacion_tipo', 'neumatico_operacion', ['tipo_operacion'], schema='fleet')
    op.create_index('idx_operacion_control_base', 'neumatico_operacion', ['control_base_id'], schema='fleet')
    op.create_index('idx_operacion_fecha', 'neumatico_operacion', ['fecha_operacion'], schema='fleet')

    op.create_foreign_key('fk_operacion_vehiculo', 'neumatico_operacion', 'vehiculo',
                          ['vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')
    op.create_foreign_key('fk_operacion_control_base', 'neumatico_operacion', 'control_base',
                          ['control_base_id'], ['id'], source_schema='fleet', referent_schema='tenant')
    op.create_foreign_key('fk_operacion_creado_por', 'neumatico_operacion', 'usuario',
                          ['creado_por'], ['id'], source_schema='fleet', referent_schema='auth',
                          ondelete='SET NULL')

    # ─────────────────────────────────────────────────────────
    # 3. Tabla: neumatico_historial_posicion
    # ─────────────────────────────────────────────────────────
    op.create_table(
        'neumatico_historial_posicion',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('neumatico_vehiculo_id', UUID(as_uuid=True), nullable=False),
        sa.Column('vehiculo_id', UUID(as_uuid=True), nullable=False),
        sa.Column('control_base_id', UUID(as_uuid=True), nullable=False),
        sa.Column('eje_posicion', sa.String(5), nullable=False),
        sa.Column('km_montaje', sa.Integer(), nullable=False),
        sa.Column('km_desmontaje', sa.Integer(), nullable=True),
        sa.Column('fecha_montaje', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_desmontaje', sa.DateTime(), nullable=True),
        sa.Column('operacion_id', UUID(as_uuid=True), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_neumatico_historial_posicion')),
        sa.CheckConstraint(
            "eje_posicion ~ '^[DT][1-4]$'",
            name='chk_eje_posicion_formato'
        ),
        schema='fleet'
    )

    op.create_index('idx_historial_pos_neumatico', 'neumatico_historial_posicion', ['neumatico_vehiculo_id'], schema='fleet')
    op.create_index('idx_historial_pos_vehiculo', 'neumatico_historial_posicion', ['vehiculo_id'], schema='fleet')
    op.create_index('idx_historial_pos_control_base', 'neumatico_historial_posicion', ['control_base_id'], schema='fleet')
    op.create_index('idx_historial_pos_eje', 'neumatico_historial_posicion', ['eje_posicion'], schema='fleet')
    # Índice parcial: solo posiciones activas (montajes vigentes)
    op.create_index(
        'idx_historial_pos_activa_vehiculo',
        'neumatico_historial_posicion',
        ['vehiculo_id', 'eje_posicion'],
        schema='fleet',
        postgresql_where=sa.text("activo = TRUE AND fecha_desmontaje IS NULL")
    )

    op.create_foreign_key('fk_historial_pos_neumatico', 'neumatico_historial_posicion', 'neumatico_vehiculo',
                          ['neumatico_vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')
    op.create_foreign_key('fk_historial_pos_vehiculo', 'neumatico_historial_posicion', 'vehiculo',
                          ['vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')
    op.create_foreign_key('fk_historial_pos_control_base', 'neumatico_historial_posicion', 'control_base',
                          ['control_base_id'], ['id'], source_schema='fleet', referent_schema='tenant')
    op.create_foreign_key('fk_historial_pos_operacion', 'neumatico_historial_posicion', 'neumatico_operacion',
                          ['operacion_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='SET NULL')

    # ─────────────────────────────────────────────────────────
    # 4. Tabla: neumatico_medicion (profundidad de dibujo)
    # ─────────────────────────────────────────────────────────
    op.create_table(
        'neumatico_medicion',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('historial_posicion_id', UUID(as_uuid=True), nullable=False),
        sa.Column('control_base_id', UUID(as_uuid=True), nullable=False),
        sa.Column('profundidad_mm', sa.Numeric(3, 1), nullable=False),
        sa.Column('fecha_medicion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('medido_por', UUID(as_uuid=True), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_neumatico_medicion')),
        sa.CheckConstraint("profundidad_mm >= 0 AND profundidad_mm <= 30", name='chk_profundidad_rango'),
        schema='fleet'
    )

    op.create_index('idx_medicion_historial', 'neumatico_medicion', ['historial_posicion_id'], schema='fleet')
    op.create_index('idx_medicion_control_base', 'neumatico_medicion', ['control_base_id'], schema='fleet')
    op.create_index('idx_medicion_fecha', 'neumatico_medicion', ['fecha_medicion'], schema='fleet')

    op.create_foreign_key('fk_medicion_historial', 'neumatico_medicion', 'neumatico_historial_posicion',
                          ['historial_posicion_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')
    op.create_foreign_key('fk_medicion_control_base', 'neumatico_medicion', 'control_base',
                          ['control_base_id'], ['id'], source_schema='fleet', referent_schema='tenant')
    op.create_foreign_key('fk_medicion_medido_por', 'neumatico_medicion', 'usuario',
                          ['medido_por'], ['id'], source_schema='fleet', referent_schema='auth',
                          ondelete='SET NULL')

    # ─────────────────────────────────────────────────────────
    # 5. Tabla: neumatico_operacion_detalle
    # ─────────────────────────────────────────────────────────
    op.create_table(
        'neumatico_operacion_detalle',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('operacion_id', UUID(as_uuid=True), nullable=False),
        sa.Column('neumatico_vehiculo_id', UUID(as_uuid=True), nullable=False),
        sa.Column('posicion_antes', sa.String(5), nullable=True),
        sa.Column('posicion_despues', sa.String(5), nullable=True),
        sa.Column('km_neumatico_en_operacion', sa.Integer(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_neumatico_operacion_detalle')),
        schema='fleet'
    )

    op.create_index('idx_operacion_detalle_operacion', 'neumatico_operacion_detalle', ['operacion_id'], schema='fleet')
    op.create_index('idx_operacion_detalle_neumatico', 'neumatico_operacion_detalle', ['neumatico_vehiculo_id'], schema='fleet')

    op.create_foreign_key('fk_detalle_operacion', 'neumatico_operacion_detalle', 'neumatico_operacion',
                          ['operacion_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')
    op.create_foreign_key('fk_detalle_neumatico', 'neumatico_operacion_detalle', 'neumatico_vehiculo',
                          ['neumatico_vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')

    # ─────────────────────────────────────────────────────────
    # 6. Tabla: neumatico_sugerencia (alertas inteligentes)
    # ─────────────────────────────────────────────────────────
    op.create_table(
        'neumatico_sugerencia',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vehiculo_id', UUID(as_uuid=True), nullable=False),
        sa.Column('control_base_id', UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_sugerencia', sa.String(30), nullable=False),
        sa.Column('neumatico_vehiculo_id', UUID(as_uuid=True), nullable=True),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('prioridad', sa.String(10), nullable=False),
        sa.Column('km_actual', sa.Integer(), nullable=True),
        sa.Column('km_umbral', sa.Integer(), nullable=True),
        sa.Column('estado', sa.String(20), nullable=True, server_default='PENDIENTE'),
        sa.Column('fecha_generacion', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('fecha_atendida', sa.DateTime(), nullable=True),
        sa.Column('atendida_por', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_neumatico_sugerencia')),
        sa.CheckConstraint(
            "tipo_sugerencia IN ('ROTACION','REEMPLAZO','REPARACION','INSPECCION','INVENTARIO','OTRO')",
            name='chk_sugerencia_tipo'
        ),
        sa.CheckConstraint(
            "prioridad IN ('ALTA','MEDIA','BAJA')",
            name='chk_sugerencia_prioridad'
        ),
        sa.CheckConstraint(
            "estado IN ('PENDIENTE','EN_PROCESO','ATENDIDA','DESCARTADA')",
            name='chk_sugerencia_estado'
        ),
        schema='fleet'
    )

    op.create_index('idx_sugerencia_vehiculo', 'neumatico_sugerencia', ['vehiculo_id'], schema='fleet')
    op.create_index('idx_sugerencia_estado', 'neumatico_sugerencia', ['estado'], schema='fleet')
    op.create_index('idx_sugerencia_control_base', 'neumatico_sugerencia', ['control_base_id'], schema='fleet')
    # Índice parcial: solo sugerencias pendientes (las activas)
    op.create_index(
        'idx_sugerencia_pendientes',
        'neumatico_sugerencia',
        ['vehiculo_id', 'prioridad'],
        schema='fleet',
        postgresql_where=sa.text("estado = 'PENDIENTE'")
    )

    op.create_foreign_key('fk_sugerencia_vehiculo', 'neumatico_sugerencia', 'vehiculo',
                          ['vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='CASCADE')
    op.create_foreign_key('fk_sugerencia_control_base', 'neumatico_sugerencia', 'control_base',
                          ['control_base_id'], ['id'], source_schema='fleet', referent_schema='tenant')
    op.create_foreign_key('fk_sugerencia_neumatico', 'neumatico_sugerencia', 'neumatico_vehiculo',
                          ['neumatico_vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='SET NULL')
    op.create_foreign_key('fk_sugerencia_atendida_por', 'neumatico_sugerencia', 'usuario',
                          ['atendida_por'], ['id'], source_schema='fleet', referent_schema='auth',
                          ondelete='SET NULL')

    # ─────────────────────────────────────────────────────────
    # 7. Tabla: neumatico_imagen (fotos en Cloudinary)
    # ─────────────────────────────────────────────────────────
    op.create_table(
        'neumatico_imagen',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('control_base_id', UUID(as_uuid=True), nullable=False),
        sa.Column('neumatico_vehiculo_id', UUID(as_uuid=True), nullable=True),
        sa.Column('operacion_id', UUID(as_uuid=True), nullable=True),
        sa.Column('cloudinary_public_id', sa.String(255), nullable=False),
        sa.Column('cloudinary_url', sa.String(500), nullable=False),
        sa.Column('cloudinary_secure_url', sa.String(500), nullable=True),
        sa.Column('tipo_imagen', sa.String(30), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('peso_bytes', sa.Integer(), nullable=True),
        sa.Column('dimensiones', sa.String(20), nullable=True),
        sa.Column('subido_por', UUID(as_uuid=True), nullable=True),
        sa.Column('fecha_subida', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('activo', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_neumatico_imagen')),
        sa.CheckConstraint(
            "tipo_imagen IN ('NEUMATICO','OPERACION','DANO','MEDICION','INVENTARIO','OTRO')",
            name='chk_imagen_tipo'
        ),
        schema='fleet'
    )

    op.create_index('idx_neumatico_imagen_neumatico', 'neumatico_imagen', ['neumatico_vehiculo_id'], schema='fleet')
    op.create_index('idx_neumatico_imagen_operacion', 'neumatico_imagen', ['operacion_id'], schema='fleet')
    op.create_index('idx_neumatico_imagen_control_base', 'neumatico_imagen', ['control_base_id'], schema='fleet')
    op.create_index('idx_neumatico_imagen_cloudinary', 'neumatico_imagen', ['cloudinary_public_id'],
                    unique=True, schema='fleet')

    op.create_foreign_key('fk_imagen_control_base', 'neumatico_imagen', 'control_base',
                          ['control_base_id'], ['id'], source_schema='fleet', referent_schema='tenant')
    op.create_foreign_key('fk_imagen_neumatico', 'neumatico_imagen', 'neumatico_vehiculo',
                          ['neumatico_vehiculo_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='SET NULL')
    op.create_foreign_key('fk_imagen_operacion', 'neumatico_imagen', 'neumatico_operacion',
                          ['operacion_id'], ['id'], source_schema='fleet', referent_schema='fleet',
                          ondelete='SET NULL')
    op.create_foreign_key('fk_imagen_subido_por', 'neumatico_imagen', 'usuario',
                          ['subido_por'], ['id'], source_schema='fleet', referent_schema='auth',
                          ondelete='SET NULL')

    # ─────────────────────────────────────────────────────────
    # 8. Triggers de updated_at
    # ─────────────────────────────────────────────────────────
    # La función actualizar_updated_at() ya existe (creada en la migración 20260726)
    for tabla in ['neumatico_vehiculo', 'neumatico_operacion', 'neumatico_sugerencia']:
        op.execute(f"""
            CREATE TRIGGER trigger_{tabla}_updated_at
                BEFORE UPDATE ON fleet.{tabla}
                FOR EACH ROW
                EXECUTE FUNCTION actualizar_updated_at();
        """)


def downgrade() -> None:
    # 1. Eliminar triggers
    for tabla in ['neumatico_vehiculo', 'neumatico_operacion', 'neumatico_sugerencia']:
        op.execute(f"DROP TRIGGER IF EXISTS trigger_{tabla}_updated_at ON fleet.{tabla}")

    # 2. Eliminar tablas en orden inverso (respetando dependencias)
    op.drop_table('neumatico_imagen', schema='fleet')
    op.drop_table('neumatico_sugerencia', schema='fleet')
    op.drop_table('neumatico_operacion_detalle', schema='fleet')
    op.drop_table('neumatico_medicion', schema='fleet')
    op.drop_table('neumatico_historial_posicion', schema='fleet')
    op.drop_table('neumatico_operacion', schema='fleet')
    op.drop_table('neumatico_vehiculo', schema='fleet')