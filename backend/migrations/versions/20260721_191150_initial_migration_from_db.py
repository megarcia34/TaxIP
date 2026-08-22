"""Initial migration generated from existing database schema"""

revision = '20260721_191150_initial'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

def upgrade() -> None:
    """Create all schemas and tables."""
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute("CREATE SCHEMA IF NOT EXISTS comunicacion")
    op.execute("CREATE SCHEMA IF NOT EXISTS fleet")
    op.execute("CREATE SCHEMA IF NOT EXISTS geo")
    op.execute("CREATE SCHEMA IF NOT EXISTS notification")
    op.execute("CREATE SCHEMA IF NOT EXISTS payment")
    op.execute("CREATE SCHEMA IF NOT EXISTS tenant")
    op.execute("CREATE SCHEMA IF NOT EXISTS trip")

    # Create tables

    op.create_table(
        'audit.log_gps',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID()),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('latitud', sa.NUMERIC(), nullable=False),
        sa.Column('longitud', sa.NUMERIC(), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'audit.alerta_desvio',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID(), nullable=False),
        sa.Column('latitud', sa.NUMERIC(), nullable=False),
        sa.Column('longitud', sa.NUMERIC(), nullable=False),
        sa.Column('distancia_desvio_metros', sa.NUMERIC(), nullable=False),
        sa.Column('ruta_esperada_json', sa.TEXT()),
        sa.Column('notificado', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('resuelto', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.tipo_usuario',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'auth.usuario',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', sa.UUID()),
        sa.Column('tipo_usuario_id', sa.UUID()),
        sa.Column('email', sa.VARCHAR(), nullable=False),
        sa.Column('password_hash', sa.TEXT(), nullable=False),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('fecha_suspension', sa.TIMESTAMP()),
        sa.Column('motivo_suspension', sa.TEXT()),
        sa.Column('suspendido_por', sa.UUID()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.perfil_general',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID()),
        sa.Column('nombre', sa.VARCHAR()),
        sa.Column('apellido', sa.VARCHAR()),
        sa.Column('telefono', sa.VARCHAR()),
        sa.Column('documento', sa.VARCHAR()),
        sa.Column('ciudad_id', sa.UUID()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('direccion', sa.TEXT()),
        sa.Column('foto_perfil_url', sa.TEXT()),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('fecha_nacimiento', sa.DATE()),
        sa.Column('barrio', sa.VARCHAR()),
        sa.Column('codigo_postal', sa.VARCHAR()),
        sa.Column('tipo_conductor', sa.VARCHAR()),
        sa.Column('agencia', sa.VARCHAR()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.reset_token',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('token', sa.VARCHAR(), nullable=False),
        sa.Column('expiracion', sa.TIMESTAMP(), nullable=False),
        sa.Column('usado', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.refresh_token',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('token', sa.VARCHAR(), nullable=False),
        sa.Column('expiracion', sa.TIMESTAMP(), nullable=False),
        sa.Column('usado', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.direccion_frecuente',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('nombre', sa.VARCHAR()),
        sa.Column('latitud', sa.NUMERIC()),
        sa.Column('longitud', sa.NUMERIC()),
        sa.Column('direccion_texto', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.taxista_favorito',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('pasajero_id', sa.UUID(), nullable=False),
        sa.Column('chofer_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.usuario_empresa',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('empresa_id', sa.UUID(), nullable=False),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('rol', sa.VARCHAR(), server_default=sa.text("'recepcionista'::character varying")),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.turno_empleado',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('empleado_id', sa.UUID(), nullable=False),
        sa.Column('empresa_id', sa.UUID(), nullable=False),
        sa.Column('fecha_inicio', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_fin', sa.TIMESTAMP()),
        sa.Column('estado', sa.VARCHAR(), nullable=False, server_default=sa.text("'ACTIVO'::character varying")),
        sa.Column('viajes_gestionados', sa.INTEGER(), server_default=sa.text('0')),
        sa.Column('facturado_total', sa.NUMERIC(), server_default=sa.text('0.0')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'auth.auditoria_email',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.VARCHAR(), nullable=False),
        sa.Column('valid', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('reason', sa.TEXT()),
        sa.Column('domain', sa.VARCHAR()),
        sa.Column('mx_records', sa.TEXT()),
        sa.Column('smtp_response', sa.TEXT()),
        sa.Column('ip_address', sa.VARCHAR()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('user_agent', sa.TEXT()),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'comunicacion.conversacion',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('participante_1', sa.UUID(), nullable=False),
        sa.Column('participante_2', sa.UUID(), nullable=False),
        sa.Column('ultimo_mensaje', sa.TEXT()),
        sa.Column('ultimo_mensaje_en', sa.TIMESTAMP()),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'comunicacion.mensaje',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversacion_id', sa.UUID(), nullable=False),
        sa.Column('remitente_id', sa.UUID(), nullable=False),
        sa.Column('viaje_id', sa.UUID()),
        sa.Column('contenido', sa.TEXT(), nullable=False),
        sa.Column('leido', sa.BOOLEAN(), nullable=False, server_default=sa.text('false')),
        sa.Column('leido_en', sa.TIMESTAMP()),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'comunicacion.email_enviado',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID()),
        sa.Column('destinatario_email', sa.VARCHAR(), nullable=False),
        sa.Column('asunto', sa.VARCHAR(), nullable=False),
        sa.Column('template_id', sa.VARCHAR()),
        sa.Column('estado', sa.VARCHAR(), nullable=False, server_default=sa.text("'pendiente'::character varying")),
        sa.Column('error_mensaje', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('enviado_en', sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.relacion_propietario_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehiculo_id', sa.UUID()),
        sa.Column('propietario_id', sa.UUID()),
        sa.Column('porcentaje_participacion', sa.NUMERIC(), server_default=sa.text('100')),
        sa.Column('fecha_inicio', sa.DATE()),
        sa.Column('fecha_fin', sa.DATE()),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.historial_chofer_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehiculo_id', sa.UUID()),
        sa.Column('chofer_id', sa.UUID()),
        sa.Column('fecha_inicio', sa.TIMESTAMP()),
        sa.Column('fecha_fin', sa.TIMESTAMP()),
        sa.Column('estado', sa.VARCHAR()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', sa.UUID()),
        sa.Column('patente', sa.VARCHAR(), nullable=False),
        sa.Column('marca', sa.VARCHAR()),
        sa.Column('modelo', sa.VARCHAR()),
        sa.Column('anio', sa.INTEGER()),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('numero_licencia', sa.VARCHAR()),
        sa.Column('qr_uuid', sa.UUID(), server_default=sa.text('gen_random_uuid()')),
        sa.Column('qr_activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.gasto_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehiculo_id', sa.UUID(), nullable=False),
        sa.Column('propietario_id', sa.UUID(), nullable=False),
        sa.Column('tipo_gasto', sa.VARCHAR()),
        sa.Column('monto', sa.NUMERIC(), nullable=False),
        sa.Column('moneda', sa.VARCHAR(), server_default=sa.text("'ARS'::character varying")),
        sa.Column('descripcion', sa.TEXT()),
        sa.Column('kilometraje', sa.INTEGER()),
        sa.Column('comprobante_url', sa.TEXT()),
        sa.Column('fecha_gasto', sa.DATE()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.mantenimiento_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehiculo_id', sa.UUID(), nullable=False),
        sa.Column('propietario_id', sa.UUID(), nullable=False),
        sa.Column('tipo_servicio', sa.VARCHAR()),
        sa.Column('taller_nombre', sa.VARCHAR()),
        sa.Column('taller_direccion', sa.TEXT()),
        sa.Column('costo', sa.NUMERIC()),
        sa.Column('kilometraje', sa.INTEGER()),
        sa.Column('observaciones', sa.TEXT()),
        sa.Column('fecha_servicio', sa.DATE()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.chofer_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('vehiculo_id', sa.UUID()),
        sa.Column('control_base_id', sa.UUID(), nullable=False),
        sa.Column('latitud', sa.NUMERIC()),
        sa.Column('longitud', sa.NUMERIC()),
        sa.Column('ubicacion', sa.Text()),
        sa.Column('estado_laboral', sa.VARCHAR(), server_default=sa.text("'libre'::character varying")),
        sa.Column('estado_panico', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('calificacion_promedio', sa.NUMERIC(), server_default=sa.text('5.0')),
        sa.Column('total_calificaciones', sa.INTEGER(), server_default=sa.text('0')),
        sa.Column('ultima_conexion', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('estado_aprobacion', sa.VARCHAR(), server_default=sa.text("'pendiente'::character varying")),
        sa.Column('total_viajes', sa.INTEGER(), server_default=sa.text('0')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.marca',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'fleet.modelo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('marca_id', sa.UUID(), nullable=False),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.propietario_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('propietario_id', sa.UUID(), nullable=False),
        sa.Column('vehiculo_id', sa.UUID(), nullable=False),
        sa.Column('porcentaje_participacion', sa.NUMERIC(), server_default=sa.text('100')),
        sa.Column('fecha_inicio', sa.DATE(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('fecha_fin', sa.DATE()),
        sa.Column('activo', sa.BOOLEAN(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.documento_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehiculo_id', sa.UUID(), nullable=False),
        sa.Column('tipo_documento', sa.VARCHAR(), nullable=False),
        sa.Column('numero', sa.VARCHAR(), nullable=False),
        sa.Column('fecha_emision', sa.DATE()),
        sa.Column('fecha_vencimiento', sa.DATE()),
        sa.Column('observaciones', sa.TEXT()),
        sa.Column('url_archivo', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.documentos_chofer',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('tipo_documento', sa.VARCHAR(), nullable=False),
        sa.Column('url', sa.TEXT(), nullable=False),
        sa.Column('subido_en', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.contrato_vehiculo',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', sa.UUID(), nullable=False),
        sa.Column('propietario_id', sa.UUID(), nullable=False),
        sa.Column('vehiculo_id', sa.UUID(), nullable=False),
        sa.Column('chofer_id', sa.UUID(), nullable=False),
        sa.Column('tipo_contrato', sa.VARCHAR(), nullable=False),
        sa.Column('turno_asignado', sa.VARCHAR(), nullable=False),
        sa.Column('porcentaje_chofer', sa.NUMERIC()),
        sa.Column('monto_diario', sa.NUMERIC()),
        sa.Column('fecha_inicio', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_fin', sa.TIMESTAMP()),
        sa.Column('activo', sa.BOOLEAN(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('estado_contrato', sa.VARCHAR(), server_default=sa.text("'PENDIENTE_CONFIGURACION'::character varying")),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.turno_chofer',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('contrato_id', sa.UUID(), nullable=False),
        sa.Column('chofer_id', sa.UUID(), nullable=False),
        sa.Column('vehiculo_id', sa.UUID(), nullable=False),
        sa.Column('estado', sa.VARCHAR(), nullable=False, server_default=sa.text("'ACTIVO'::character varying")),
        sa.Column('km_inicial', sa.NUMERIC(), nullable=False),
        sa.Column('km_final', sa.NUMERIC()),
        sa.Column('combustible_inicial', sa.VARCHAR(), nullable=False),
        sa.Column('combustible_final', sa.VARCHAR()),
        sa.Column('recaudacion_app_efectivo', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('recaudacion_app_debito', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('recaudacion_ticketera_calle', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('monto_bruto_calculado', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('comision_chofer_calculada', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('utilidad_propietario_calculada', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('inicio_turno', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fin_turno', sa.TIMESTAMP()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'fleet.gasto_turno',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('turno_id', sa.UUID(), nullable=False),
        sa.Column('tipo_gasto', sa.VARCHAR(), nullable=False),
        sa.Column('monto', sa.NUMERIC(), nullable=False),
        sa.Column('km_registro', sa.NUMERIC()),
        sa.Column('url_comprobante', sa.VARCHAR()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'geo.pais',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('codigo_iso', sa.VARCHAR()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'geo.provincia',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('pais_id', sa.UUID()),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'geo.ciudad',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('provincia_id', sa.UUID()),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'notification.notificacion',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('titulo', sa.VARCHAR()),
        sa.Column('mensaje', sa.TEXT(), nullable=False),
        sa.Column('tipo', sa.VARCHAR(), nullable=False),
        sa.Column('leida', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'payment.metodo_pago',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'payment.transaccion',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID()),
        sa.Column('metodo_pago_id', sa.UUID()),
        sa.Column('monto', sa.NUMERIC()),
        sa.Column('estado', sa.VARCHAR()),
        sa.Column('referencia_externa', sa.VARCHAR()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('tipo', sa.VARCHAR()),
        sa.Column('saldo_despues', sa.NUMERIC()),
        sa.Column('descripcion', sa.TEXT()),
        sa.Column('billetera_id', sa.UUID()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'payment.configuracion_tarifa',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', sa.UUID(), nullable=False),
        sa.Column('nombre', sa.VARCHAR()),
        sa.Column('tarifa_base', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('precio_por_km', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('precio_por_minuto', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('recargo_nocturno', sa.NUMERIC(), server_default=sa.text('1.0')),
        sa.Column('recargo_feriado', sa.NUMERIC(), server_default=sa.text('1.0')),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('modo_calculo', sa.VARCHAR(), server_default=sa.text("'por_km'::character varying")),
        sa.Column('distancia_por_ficha', sa.NUMERIC(), server_default=sa.text('100')),
        sa.Column('precio_por_ficha', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('precio_por_minuto_espera', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('recargo_domingo', sa.NUMERIC(), server_default=sa.text('1.0')),
        sa.Column('hora_inicio_nocturno', sa.TIME(), server_default=sa.text("'22:00:00'::time without time zone")),
        sa.Column('hora_fin_nocturno', sa.TIME(), server_default=sa.text("'06:00:00'::time without time zone")),
        sa.Column('moneda', sa.VARCHAR(), server_default=sa.text("'ARS'::character varying")),
        sa.Column('descripcion', sa.TEXT()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'payment.billetera',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('saldo', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('moneda', sa.VARCHAR(), server_default=sa.text("'ARS'::character varying")),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'payment.factura_empresa',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('empresa_id', sa.UUID(), nullable=False),
        sa.Column('periodo', sa.DATE(), nullable=False),
        sa.Column('total', sa.NUMERIC()),
        sa.Column('descuento', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('total_final', sa.NUMERIC()),
        sa.Column('estado', sa.VARCHAR(), server_default=sa.text("'pendiente'::character varying")),
        sa.Column('pdf_url', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('pagada_at', sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'payment.pago_empresa',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('empresa_id', sa.UUID(), nullable=False),
        sa.Column('monto', sa.NUMERIC(), nullable=False),
        sa.Column('metodo_pago', sa.VARCHAR(), nullable=False),
        sa.Column('referencia', sa.VARCHAR()),
        sa.Column('estado', sa.VARCHAR(), server_default=sa.text("'pendiente'::character varying")),
        sa.Column('comprobante_url', sa.TEXT()),
        sa.Column('factura_id', sa.UUID()),
        sa.Column('observaciones', sa.TEXT()),
        sa.Column('fecha_pago', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('confirmado_en', sa.TIMESTAMP()),
        sa.Column('confirmado_por', sa.UUID()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'comercio',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('rubro', sa.VARCHAR()),
        sa.Column('direccion', sa.TEXT(), nullable=False),
        sa.Column('latitud', sa.NUMERIC(), nullable=False),
        sa.Column('longitud', sa.NUMERIC(), nullable=False),
        sa.Column('codigo_qr', sa.VARCHAR(), nullable=False),
        sa.Column('email_contacto', sa.VARCHAR()),
        sa.Column('telefono', sa.VARCHAR()),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('control_base_id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'escaneo_qr',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('comercio_id', sa.UUID(), nullable=False),
        sa.Column('viaje_id', sa.UUID()),
        sa.Column('user_agent', sa.TEXT()),
        sa.Column('ip_address', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'tenant.configuracion_tenant',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', sa.UUID()),
        sa.Column('moneda_default', sa.VARCHAR(), server_default=sa.text("'ARS'::character varying")),
        sa.Column('timezone', sa.VARCHAR(), server_default=sa.text("'America/Argentina/Tucuman'::character varying")),
        sa.Column('idioma', sa.VARCHAR(), server_default=sa.text("'es'::character varying")),
        sa.Column('habilitar_fidelizacion', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('habilitar_pagos_online', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'tenant.control_base',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('email', sa.VARCHAR()),
        sa.Column('telefono', sa.VARCHAR()),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('latitud', sa.NUMERIC()),
        sa.Column('longitud', sa.NUMERIC()),
        sa.Column('fecha_suspension', sa.TIMESTAMP()),
        sa.Column('motivo_suspension', sa.TEXT()),
        sa.Column('suspendido_por', sa.UUID()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'tenant.empresa',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('tipo', sa.VARCHAR(), server_default=sa.text("'hotel'::character varying")),
        sa.Column('email_facturacion', sa.VARCHAR()),
        sa.Column('telefono', sa.VARCHAR()),
        sa.Column('direccion', sa.TEXT()),
        sa.Column('latitud', sa.NUMERIC()),
        sa.Column('longitud', sa.NUMERIC()),
        sa.Column('tarifa_preferencial', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('condiciones_pago', sa.VARCHAR(), server_default=sa.text("'mensual'::character varying")),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('control_base_id', sa.UUID(), nullable=False),
        sa.Column('limite_credito', sa.NUMERIC(), server_default=sa.text('0.0')),
        sa.Column('contacto_nombre', sa.VARCHAR()),
        sa.Column('contacto_telefono', sa.VARCHAR()),
        sa.Column('contacto_email', sa.VARCHAR()),
        sa.Column('fecha_suspension', sa.TIMESTAMP()),
        sa.Column('motivo_suspension', sa.TEXT()),
        sa.Column('suspendido_por', sa.UUID()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'tenant.factura',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', sa.UUID(), nullable=False),
        sa.Column('periodo', sa.DATE(), nullable=False),
        sa.Column('vehiculos_activos', sa.INTEGER(), nullable=False, server_default=sa.text('0')),
        sa.Column('canon_total', sa.NUMERIC(), nullable=False, server_default=sa.text('0')),
        sa.Column('porcentaje_plataforma', sa.NUMERIC(), nullable=False, server_default=sa.text('15')),
        sa.Column('total_a_pagar', sa.NUMERIC(), nullable=False, server_default=sa.text('0')),
        sa.Column('estado', sa.VARCHAR(), nullable=False, server_default=sa.text("'pendiente'::character varying")),
        sa.Column('fecha_emision', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_vencimiento', sa.TIMESTAMP()),
        sa.Column('pagada_at', sa.TIMESTAMP()),
        sa.Column('pagada_por', sa.UUID()),
        sa.Column('numero_factura', sa.VARCHAR()),
        sa.Column('observaciones', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.historial_estado_viaje',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID()),
        sa.Column('estado', sa.VARCHAR()),
        sa.Column('observacion', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.panico',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID()),
        sa.Column('ubicacion', sa.Text()),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.objeto_olvidado',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID(), nullable=False),
        sa.Column('pasajero_id', sa.UUID(), nullable=False),
        sa.Column('chofer_id', sa.UUID(), nullable=False),
        sa.Column('descripcion', sa.TEXT(), nullable=False),
        sa.Column('estado', sa.VARCHAR(), server_default=sa.text("'reportado'::character varying")),
        sa.Column('foto_url', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.calificacion',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID(), nullable=False),
        sa.Column('calificador_id', sa.UUID(), nullable=False),
        sa.Column('calificado_id', sa.UUID(), nullable=False),
        sa.Column('puntaje', sa.INTEGER(), nullable=False),
        sa.Column('comentario', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.foto_viaje',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viaje_id', sa.UUID(), nullable=False),
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('url', sa.TEXT(), nullable=False),
        sa.Column('thumbnail_url', sa.TEXT()),
        sa.Column('metadata_json', sa.TEXT()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.viaje_solicitado',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('control_base_id', sa.UUID()),
        sa.Column('pasajero_id', sa.UUID()),
        sa.Column('chofer_id', sa.UUID()),
        sa.Column('vehiculo_id', sa.UUID()),
        sa.Column('origen', sa.Text()),
        sa.Column('destino', sa.Text()),
        sa.Column('estado', sa.VARCHAR(), server_default=sa.text("'pendiente'::character varying")),
        sa.Column('precio_estimado', sa.NUMERIC()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('finalizado_at', sa.TIMESTAMP()),
        sa.Column('fecha_programada', sa.TIMESTAMP()),
        sa.Column('reserva_procesada', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('procesado_en', sa.TIMESTAMP()),
        sa.Column('direccion_origen', sa.TEXT()),
        sa.Column('direccion_destino', sa.TEXT()),
        sa.Column('tiempo_estimado_segundos', sa.INTEGER()),
        sa.Column('distancia_metros', sa.INTEGER()),
        sa.Column('url_seguimiento', sa.VARCHAR()),
        sa.Column('codigo_compartido', sa.VARCHAR()),
        sa.Column('aceptado_en', sa.TIMESTAMP()),
        sa.Column('iniciado_en', sa.TIMESTAMP()),
        sa.Column('finalizado_en', sa.TIMESTAMP()),
        sa.Column('cancelado_en', sa.TIMESTAMP()),
        sa.Column('cancelado_por', sa.VARCHAR()),
        sa.Column('motivo_cancelacion', sa.TEXT()),
        sa.Column('precio_final', sa.NUMERIC()),
        sa.Column('moneda', sa.VARCHAR(), server_default=sa.text("'ARS'::character varying")),
        sa.Column('comercio_id', sa.UUID()),
        sa.Column('empresa_id', sa.UUID()),
        sa.Column('nombre_pasajero', sa.VARCHAR()),
        sa.Column('notas', sa.TEXT()),
        sa.Column('facturado', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.reserva',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('empresa_id', sa.UUID(), nullable=False),
        sa.Column('empleado_id', sa.UUID(), nullable=False),
        sa.Column('turno_id', sa.UUID()),
        sa.Column('pasajero_nombre', sa.VARCHAR()),
        sa.Column('pasajero_telefono', sa.VARCHAR()),
        sa.Column('direccion_origen', sa.TEXT(), nullable=False),
        sa.Column('latitud_origen', sa.NUMERIC()),
        sa.Column('longitud_origen', sa.NUMERIC()),
        sa.Column('direccion_destino', sa.TEXT(), nullable=False),
        sa.Column('latitud_destino', sa.NUMERIC()),
        sa.Column('longitud_destino', sa.NUMERIC()),
        sa.Column('paradas_intermedias', postgresql.JSONB(), server_default=sa.text("'[]'::jsonb")),
        sa.Column('tipo_vehiculo', sa.VARCHAR(), server_default=sa.text("'standard'::character varying")),
        sa.Column('nota_conductor', sa.TEXT()),
        sa.Column('estado', sa.VARCHAR(), server_default=sa.text("'reservado'::character varying")),
        sa.Column('es_programado', sa.BOOLEAN(), server_default=sa.text('false')),
        sa.Column('fecha_programada', sa.TIMESTAMP()),
        sa.Column('distancia_estimada_km', sa.NUMERIC()),
        sa.Column('tiempo_estimado_minutos', sa.INTEGER()),
        sa.Column('precio_estimado', sa.NUMERIC()),
        sa.Column('precio_final', sa.NUMERIC()),
        sa.Column('metodo_pago', sa.VARCHAR(), server_default=sa.text("'vehiculo'::character varying")),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('creado_por', sa.UUID()),
        sa.Column('cantidad_pasajeros', sa.INTEGER(), server_default=sa.text('1')),
        sa.Column('cantidad_equipaje', sa.INTEGER(), server_default=sa.text('0')),
        sa.Column('centro_costo', sa.VARCHAR()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'trip.tipo_vehiculo',
        sa.Column('id', sa.VARCHAR(), nullable=False),
        sa.Column('nombre', sa.VARCHAR(), nullable=False),
        sa.Column('descripcion', sa.TEXT()),
        sa.Column('tarifa_base', sa.NUMERIC(), nullable=False, server_default=sa.text('0')),
        sa.Column('tarifa_por_km', sa.NUMERIC(), nullable=False, server_default=sa.text('0')),
        sa.Column('tarifa_por_minuto', sa.NUMERIC(), nullable=False, server_default=sa.text('0')),
        sa.Column('capacidad_pasajeros', sa.INTEGER(), server_default=sa.text('4')),
        sa.Column('capacidad_equipaje', sa.INTEGER(), server_default=sa.text('2')),
        sa.Column('activo', sa.BOOLEAN(), server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('precio_por_ficha', sa.NUMERIC(), server_default=sa.text('0')),
        sa.Column('distancia_por_ficha', sa.NUMERIC(), server_default=sa.text('100')),
        sa.Column('precio_por_minuto_espera', sa.NUMERIC(), server_default=sa.text('0')),
        sa.PrimaryKeyConstraint('id')
    )



    # ============================================================
    # FASE B: CREACION DE FOREIGN KEYS
    # ============================================================
    op.create_foreign_key(
        'fk_log_gps_usuario_id',
        'log_gps',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='audit',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_log_gps_viaje_id',
        'log_gps',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='audit',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_alerta_desvio_viaje_id',
        'alerta_desvio',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='audit',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_usuario_control_base_id',
        'usuario',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='auth',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_usuario_suspendido_por',
        'usuario',
        'usuario',
        ['suspendido_por'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_usuario_tipo_usuario_id',
        'usuario',
        'tipo_usuario',
        ['tipo_usuario_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_perfil_general_ciudad_id',
        'perfil_general',
        'ciudad',
        ['ciudad_id'],
        ['id'],
        source_schema='auth',
        referent_schema='geo'
    )
    op.create_foreign_key(
        'fk_perfil_general_usuario_id',
        'perfil_general',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_reset_token_usuario_id',
        'reset_token',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_refresh_token_usuario_id',
        'refresh_token',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_direccion_frecuente_usuario_id',
        'direccion_frecuente',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_taxista_favorito_chofer_id',
        'taxista_favorito',
        'usuario',
        ['chofer_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_taxista_favorito_pasajero_id',
        'taxista_favorito',
        'usuario',
        ['pasajero_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_usuario_empresa_empresa_id',
        'usuario_empresa',
        'empresa',
        ['empresa_id'],
        ['id'],
        source_schema='auth',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_usuario_empresa_usuario_id',
        'usuario_empresa',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_turno_empleado_empleado_id',
        'turno_empleado',
        'usuario',
        ['empleado_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_turno_empleado_empresa_id',
        'turno_empleado',
        'empresa',
        ['empresa_id'],
        ['id'],
        source_schema='auth',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_conversacion_participante_1',
        'conversacion',
        'usuario',
        ['participante_1'],
        ['id'],
        source_schema='comunicacion',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_conversacion_participante_2',
        'conversacion',
        'usuario',
        ['participante_2'],
        ['id'],
        source_schema='comunicacion',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_mensaje_conversacion_id',
        'mensaje',
        'conversacion',
        ['conversacion_id'],
        ['id'],
        source_schema='comunicacion',
        referent_schema='comunicacion'
    )
    op.create_foreign_key(
        'fk_mensaje_remitente_id',
        'mensaje',
        'usuario',
        ['remitente_id'],
        ['id'],
        source_schema='comunicacion',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_mensaje_viaje_id',
        'mensaje',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='comunicacion',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_email_enviado_usuario_id',
        'email_enviado',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='comunicacion',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_relacion_propietario_vehiculo_propietario_id',
        'relacion_propietario_vehiculo',
        'usuario',
        ['propietario_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_relacion_propietario_vehiculo_vehiculo_id',
        'relacion_propietario_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_historial_chofer_vehiculo_chofer_id',
        'historial_chofer_vehiculo',
        'usuario',
        ['chofer_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_historial_chofer_vehiculo_vehiculo_id',
        'historial_chofer_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_vehiculo_control_base_id',
        'vehiculo',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_gasto_vehiculo_propietario_id',
        'gasto_vehiculo',
        'usuario',
        ['propietario_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_gasto_vehiculo_vehiculo_id',
        'gasto_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_mantenimiento_vehiculo_propietario_id',
        'mantenimiento_vehiculo',
        'usuario',
        ['propietario_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_mantenimiento_vehiculo_vehiculo_id',
        'mantenimiento_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_chofer_vehiculo_control_base_id',
        'chofer_vehiculo',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_chofer_vehiculo_usuario_id',
        'chofer_vehiculo',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_chofer_vehiculo_vehiculo_id',
        'chofer_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_modelo_marca_id',
        'modelo',
        'marca',
        ['marca_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_propietario_vehiculo_propietario_id',
        'propietario_vehiculo',
        'usuario',
        ['propietario_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_propietario_vehiculo_vehiculo_id',
        'propietario_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_documento_vehiculo_vehiculo_id',
        'documento_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_documentos_chofer_usuario_id',
        'documentos_chofer',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_contrato_vehiculo_chofer_id',
        'contrato_vehiculo',
        'usuario',
        ['chofer_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_contrato_vehiculo_control_base_id',
        'contrato_vehiculo',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_contrato_vehiculo_propietario_id',
        'contrato_vehiculo',
        'usuario',
        ['propietario_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_contrato_vehiculo_vehiculo_id',
        'contrato_vehiculo',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_turno_chofer_chofer_id',
        'turno_chofer',
        'usuario',
        ['chofer_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_turno_chofer_contrato_id',
        'turno_chofer',
        'contrato_vehiculo',
        ['contrato_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_turno_chofer_vehiculo_id',
        'turno_chofer',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_gasto_turno_turno_id',
        'gasto_turno',
        'turno_chofer',
        ['turno_id'],
        ['id'],
        source_schema='fleet',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_provincia_pais_id',
        'provincia',
        'pais',
        ['pais_id'],
        ['id'],
        source_schema='geo',
        referent_schema='geo'
    )
    op.create_foreign_key(
        'fk_ciudad_provincia_id',
        'ciudad',
        'provincia',
        ['provincia_id'],
        ['id'],
        source_schema='geo',
        referent_schema='geo'
    )
    op.create_foreign_key(
        'fk_notificacion_usuario_id',
        'notificacion',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='notification',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_transaccion_billetera_id',
        'transaccion',
        'billetera',
        ['billetera_id'],
        ['id'],
        source_schema='payment',
        referent_schema='payment'
    )
    op.create_foreign_key(
        'fk_transaccion_metodo_pago_id',
        'transaccion',
        'metodo_pago',
        ['metodo_pago_id'],
        ['id'],
        source_schema='payment',
        referent_schema='payment'
    )
    op.create_foreign_key(
        'fk_transaccion_viaje_id',
        'transaccion',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='payment',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_configuracion_tarifa_control_base_id',
        'configuracion_tarifa',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='payment',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_billetera_usuario_id',
        'billetera',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='payment',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_factura_empresa_empresa_id',
        'factura_empresa',
        'empresa',
        ['empresa_id'],
        ['id'],
        source_schema='payment',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_pago_empresa_confirmado_por',
        'pago_empresa',
        'usuario',
        ['confirmado_por'],
        ['id'],
        source_schema='payment',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_pago_empresa_empresa_id',
        'pago_empresa',
        'empresa',
        ['empresa_id'],
        ['id'],
        source_schema='payment',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_pago_empresa_factura_id',
        'pago_empresa',
        'factura_empresa',
        ['factura_id'],
        ['id'],
        source_schema='payment',
        referent_schema='payment'
    )
    op.create_foreign_key(
        'fk_comercio_control_base_id',
        'comercio',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='public',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_escaneo_qr_comercio_id',
        'escaneo_qr',
        'comercio',
        ['comercio_id'],
        ['id'],
        source_schema='public',
        referent_schema='public'
    )
    op.create_foreign_key(
        'fk_escaneo_qr_viaje_id',
        'escaneo_qr',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='public',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_configuracion_tenant_control_base_id',
        'configuracion_tenant',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='tenant',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_control_base_suspendido_por',
        'control_base',
        'usuario',
        ['suspendido_por'],
        ['id'],
        source_schema='tenant',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_empresa_control_base_id',
        'empresa',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='tenant',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_empresa_suspendido_por',
        'empresa',
        'usuario',
        ['suspendido_por'],
        ['id'],
        source_schema='tenant',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_factura_control_base_id',
        'factura',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='tenant',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_factura_pagada_por',
        'factura',
        'usuario',
        ['pagada_por'],
        ['id'],
        source_schema='tenant',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_historial_estado_viaje_viaje_id',
        'historial_estado_viaje',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='trip',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_panico_viaje_id',
        'panico',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='trip',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_objeto_olvidado_chofer_id',
        'objeto_olvidado',
        'usuario',
        ['chofer_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_objeto_olvidado_pasajero_id',
        'objeto_olvidado',
        'usuario',
        ['pasajero_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_objeto_olvidado_viaje_id',
        'objeto_olvidado',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='trip',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_calificacion_calificado_id',
        'calificacion',
        'usuario',
        ['calificado_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_calificacion_calificador_id',
        'calificacion',
        'usuario',
        ['calificador_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_calificacion_viaje_id',
        'calificacion',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='trip',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_foto_viaje_usuario_id',
        'foto_viaje',
        'usuario',
        ['usuario_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_foto_viaje_viaje_id',
        'foto_viaje',
        'viaje_solicitado',
        ['viaje_id'],
        ['id'],
        source_schema='trip',
        referent_schema='trip'
    )
    op.create_foreign_key(
        'fk_viaje_solicitado_chofer_id',
        'viaje_solicitado',
        'usuario',
        ['chofer_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_viaje_solicitado_comercio_id',
        'viaje_solicitado',
        'comercio',
        ['comercio_id'],
        ['id'],
        source_schema='trip',
        referent_schema='public'
    )
    op.create_foreign_key(
        'fk_viaje_solicitado_control_base_id',
        'viaje_solicitado',
        'control_base',
        ['control_base_id'],
        ['id'],
        source_schema='trip',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_viaje_solicitado_empresa_id',
        'viaje_solicitado',
        'empresa',
        ['empresa_id'],
        ['id'],
        source_schema='trip',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_viaje_solicitado_pasajero_id',
        'viaje_solicitado',
        'usuario',
        ['pasajero_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_viaje_solicitado_vehiculo_id',
        'viaje_solicitado',
        'vehiculo',
        ['vehiculo_id'],
        ['id'],
        source_schema='trip',
        referent_schema='fleet'
    )
    op.create_foreign_key(
        'fk_reserva_empleado_id',
        'reserva',
        'usuario',
        ['empleado_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_reserva_empresa_id',
        'reserva',
        'empresa',
        ['empresa_id'],
        ['id'],
        source_schema='trip',
        referent_schema='tenant'
    )
    op.create_foreign_key(
        'fk_reserva_turno_id',
        'reserva',
        'turno_empleado',
        ['turno_id'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )
    op.create_foreign_key(
        'fk_reserva_creado_por',
        'reserva',
        'usuario',
        ['creado_por'],
        ['id'],
        source_schema='trip',
        referent_schema='auth'
    )

def downgrade() -> None:

    # ============================================================
    # ELIMINAR FOREIGN KEYS
    # ============================================================
    op.drop_constraint('fk_reserva_creado_por', 'reserva', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_reserva_turno_id', 'reserva', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_reserva_empresa_id', 'reserva', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_reserva_empleado_id', 'reserva', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_viaje_solicitado_vehiculo_id', 'viaje_solicitado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_viaje_solicitado_pasajero_id', 'viaje_solicitado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_viaje_solicitado_empresa_id', 'viaje_solicitado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_viaje_solicitado_control_base_id', 'viaje_solicitado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_viaje_solicitado_comercio_id', 'viaje_solicitado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_viaje_solicitado_chofer_id', 'viaje_solicitado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_foto_viaje_viaje_id', 'foto_viaje', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_foto_viaje_usuario_id', 'foto_viaje', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_calificacion_viaje_id', 'calificacion', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_calificacion_calificador_id', 'calificacion', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_calificacion_calificado_id', 'calificacion', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_objeto_olvidado_viaje_id', 'objeto_olvidado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_objeto_olvidado_pasajero_id', 'objeto_olvidado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_objeto_olvidado_chofer_id', 'objeto_olvidado', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_panico_viaje_id', 'panico', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_historial_estado_viaje_viaje_id', 'historial_estado_viaje', schema='trip', type_='foreignkey')
    op.drop_constraint('fk_factura_pagada_por', 'factura', schema='tenant', type_='foreignkey')
    op.drop_constraint('fk_factura_control_base_id', 'factura', schema='tenant', type_='foreignkey')
    op.drop_constraint('fk_empresa_suspendido_por', 'empresa', schema='tenant', type_='foreignkey')
    op.drop_constraint('fk_empresa_control_base_id', 'empresa', schema='tenant', type_='foreignkey')
    op.drop_constraint('fk_control_base_suspendido_por', 'control_base', schema='tenant', type_='foreignkey')
    op.drop_constraint('fk_configuracion_tenant_control_base_id', 'configuracion_tenant', schema='tenant', type_='foreignkey')
    op.drop_constraint('fk_escaneo_qr_viaje_id', 'escaneo_qr', schema='public', type_='foreignkey')
    op.drop_constraint('fk_escaneo_qr_comercio_id', 'escaneo_qr', schema='public', type_='foreignkey')
    op.drop_constraint('fk_comercio_control_base_id', 'comercio', schema='public', type_='foreignkey')
    op.drop_constraint('fk_pago_empresa_factura_id', 'pago_empresa', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_pago_empresa_empresa_id', 'pago_empresa', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_pago_empresa_confirmado_por', 'pago_empresa', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_factura_empresa_empresa_id', 'factura_empresa', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_billetera_usuario_id', 'billetera', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_configuracion_tarifa_control_base_id', 'configuracion_tarifa', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_transaccion_viaje_id', 'transaccion', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_transaccion_metodo_pago_id', 'transaccion', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_transaccion_billetera_id', 'transaccion', schema='payment', type_='foreignkey')
    op.drop_constraint('fk_notificacion_usuario_id', 'notificacion', schema='notification', type_='foreignkey')
    op.drop_constraint('fk_ciudad_provincia_id', 'ciudad', schema='geo', type_='foreignkey')
    op.drop_constraint('fk_provincia_pais_id', 'provincia', schema='geo', type_='foreignkey')
    op.drop_constraint('fk_gasto_turno_turno_id', 'gasto_turno', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_turno_chofer_vehiculo_id', 'turno_chofer', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_turno_chofer_contrato_id', 'turno_chofer', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_turno_chofer_chofer_id', 'turno_chofer', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_contrato_vehiculo_vehiculo_id', 'contrato_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_contrato_vehiculo_propietario_id', 'contrato_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_contrato_vehiculo_control_base_id', 'contrato_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_contrato_vehiculo_chofer_id', 'contrato_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_documentos_chofer_usuario_id', 'documentos_chofer', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_documento_vehiculo_vehiculo_id', 'documento_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_propietario_vehiculo_vehiculo_id', 'propietario_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_propietario_vehiculo_propietario_id', 'propietario_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_modelo_marca_id', 'modelo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_chofer_vehiculo_vehiculo_id', 'chofer_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_chofer_vehiculo_usuario_id', 'chofer_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_chofer_vehiculo_control_base_id', 'chofer_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_mantenimiento_vehiculo_vehiculo_id', 'mantenimiento_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_mantenimiento_vehiculo_propietario_id', 'mantenimiento_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_gasto_vehiculo_vehiculo_id', 'gasto_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_gasto_vehiculo_propietario_id', 'gasto_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_vehiculo_control_base_id', 'vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_historial_chofer_vehiculo_vehiculo_id', 'historial_chofer_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_historial_chofer_vehiculo_chofer_id', 'historial_chofer_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_relacion_propietario_vehiculo_vehiculo_id', 'relacion_propietario_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_relacion_propietario_vehiculo_propietario_id', 'relacion_propietario_vehiculo', schema='fleet', type_='foreignkey')
    op.drop_constraint('fk_email_enviado_usuario_id', 'email_enviado', schema='comunicacion', type_='foreignkey')
    op.drop_constraint('fk_mensaje_viaje_id', 'mensaje', schema='comunicacion', type_='foreignkey')
    op.drop_constraint('fk_mensaje_remitente_id', 'mensaje', schema='comunicacion', type_='foreignkey')
    op.drop_constraint('fk_mensaje_conversacion_id', 'mensaje', schema='comunicacion', type_='foreignkey')
    op.drop_constraint('fk_conversacion_participante_2', 'conversacion', schema='comunicacion', type_='foreignkey')
    op.drop_constraint('fk_conversacion_participante_1', 'conversacion', schema='comunicacion', type_='foreignkey')
    op.drop_constraint('fk_turno_empleado_empresa_id', 'turno_empleado', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_turno_empleado_empleado_id', 'turno_empleado', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_usuario_empresa_usuario_id', 'usuario_empresa', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_usuario_empresa_empresa_id', 'usuario_empresa', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_taxista_favorito_pasajero_id', 'taxista_favorito', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_taxista_favorito_chofer_id', 'taxista_favorito', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_direccion_frecuente_usuario_id', 'direccion_frecuente', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_refresh_token_usuario_id', 'refresh_token', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_reset_token_usuario_id', 'reset_token', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_perfil_general_usuario_id', 'perfil_general', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_perfil_general_ciudad_id', 'perfil_general', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_usuario_tipo_usuario_id', 'usuario', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_usuario_suspendido_por', 'usuario', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_usuario_control_base_id', 'usuario', schema='auth', type_='foreignkey')
    op.drop_constraint('fk_alerta_desvio_viaje_id', 'alerta_desvio', schema='audit', type_='foreignkey')
    op.drop_constraint('fk_log_gps_viaje_id', 'log_gps', schema='audit', type_='foreignkey')
    op.drop_constraint('fk_log_gps_usuario_id', 'log_gps', schema='audit', type_='foreignkey')

    """Drop all tables in reverse dependency order."""

    op.drop_table('trip.tipo_vehiculo')
    op.drop_table('trip.reserva')
    op.drop_table('trip.viaje_solicitado')
    op.drop_table('trip.foto_viaje')
    op.drop_table('trip.calificacion')
    op.drop_table('trip.objeto_olvidado')
    op.drop_table('trip.panico')
    op.drop_table('trip.historial_estado_viaje')
    op.drop_table('tenant.factura')
    op.drop_table('tenant.empresa')
    op.drop_table('tenant.control_base')
    op.drop_table('tenant.configuracion_tenant')
    op.drop_table('escaneo_qr')
    op.drop_table('comercio')
    op.drop_table('payment.pago_empresa')
    op.drop_table('payment.factura_empresa')
    op.drop_table('payment.billetera')
    op.drop_table('payment.configuracion_tarifa')
    op.drop_table('payment.transaccion')
    op.drop_table('payment.metodo_pago')
    op.drop_table('notification.notificacion')
    op.drop_table('geo.ciudad')
    op.drop_table('geo.provincia')
    op.drop_table('geo.pais')
    op.drop_table('fleet.gasto_turno')
    op.drop_table('fleet.turno_chofer')
    op.drop_table('fleet.contrato_vehiculo')
    op.drop_table('fleet.documentos_chofer')
    op.drop_table('fleet.documento_vehiculo')
    op.drop_table('fleet.propietario_vehiculo')
    op.drop_table('fleet.modelo')
    op.drop_table('fleet.marca')
    op.drop_table('fleet.chofer_vehiculo')
    op.drop_table('fleet.mantenimiento_vehiculo')
    op.drop_table('fleet.gasto_vehiculo')
    op.drop_table('fleet.vehiculo')
    op.drop_table('fleet.historial_chofer_vehiculo')
    op.drop_table('fleet.relacion_propietario_vehiculo')
    op.drop_table('comunicacion.email_enviado')
    op.drop_table('comunicacion.mensaje')
    op.drop_table('comunicacion.conversacion')
    op.drop_table('auth.auditoria_email')
    op.drop_table('auth.turno_empleado')
    op.drop_table('auth.usuario_empresa')
    op.drop_table('auth.taxista_favorito')
    op.drop_table('auth.direccion_frecuente')
    op.drop_table('auth.refresh_token')
    op.drop_table('auth.reset_token')
    op.drop_table('auth.perfil_general')
    op.drop_table('auth.usuario')
    op.drop_table('auth.tipo_usuario')
    op.drop_table('audit.alerta_desvio')
    op.drop_table('audit.log_gps')
