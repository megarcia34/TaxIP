"""m3_015: renombrar CHECKs al naming canonico ck_<tabla>_<col>.

Items del diff: D-0001, D-0002, D-0004 a D-0017 (16 CHECKs).
Deuda: orm.naming_convention_check_divergente (Grupo 2).

Renombra los CHECKs en DB para que coincidan con la naming convention
de SQLAlchemy (app/database.py):
    ck_%(table_name)s_%(constraint_name)s

Los 16 CHECKs se renombran a ck_<tabla>_<sufijo>, donde <sufijo> es
el name= que se va a declarar en el ORM.

Requiere backup DB previo (docs/backups/taxip_db_ronda14.dump).

Ver docs/DEUDA_TECNICA_ACTUAL.md.
"""
from alembic import op

revision = 'm3_015'
down_revision = 'm3_014'
branch_labels = None
depends_on = None


def upgrade():
    # auth.codigo_verificacion
    op.execute("""
        ALTER TABLE auth.codigo_verificacion
        RENAME CONSTRAINT chk_codigo_verificacion_tipo
        TO ck_codigo_verificacion_tipo
    """)

    # auth.turno_empleado
    op.execute("""
        ALTER TABLE auth.turno_empleado
        RENAME CONSTRAINT check_estado_turno
        TO ck_turno_empleado_estado
    """)

    # fleet.contrato_vehiculo (9 CHECKs)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_compensacion_km
        TO ck_contrato_vehiculo_compensacion_km
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_estado
        TO ck_contrato_vehiculo_estado
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_extension_valida
        TO ck_contrato_vehiculo_extension_valida
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_dia_inicio_semana
        TO ck_contrato_vehiculo_dia_inicio_semana
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT check_porcentaje
        TO ck_contrato_vehiculo_porcentaje
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_activo_estado
        TO ck_contrato_vehiculo_activo_estado
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_horario_valido
        TO ck_contrato_vehiculo_horario_valido
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_duracion_minima
        TO ck_contrato_vehiculo_duracion_minima
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT check_auto_gestion
        TO ck_contrato_vehiculo_auto_gestion
    """)

    # payment.pago_empresa (2 CHECKs)
    op.execute("""
        ALTER TABLE payment.pago_empresa
        RENAME CONSTRAINT pago_empresa_estado_check
        TO ck_pago_empresa_estado
    """)
    op.execute("""
        ALTER TABLE payment.pago_empresa
        RENAME CONSTRAINT pago_empresa_monto_check
        TO ck_pago_empresa_monto
    """)

    # public.escaneo_qr (2 CHECKs)
    op.execute("""
        ALTER TABLE public.escaneo_qr
        RENAME CONSTRAINT chk_escaneo_qr_resultado
        TO ck_escaneo_qr_resultado
    """)
    op.execute("""
        ALTER TABLE public.escaneo_qr
        RENAME CONSTRAINT chk_escaneo_qr_tipo
        TO ck_escaneo_qr_tipo
    """)

    # trip.calificacion
    op.execute("""
        ALTER TABLE trip.calificacion
        RENAME CONSTRAINT calificacion_puntaje_check
        TO ck_calificacion_puntaje
    """)


def downgrade():
    # Reverso: renombrar al nombre original
    op.execute("""
        ALTER TABLE trip.calificacion
        RENAME CONSTRAINT ck_calificacion_puntaje
        TO calificacion_puntaje_check
    """)
    op.execute("""
        ALTER TABLE public.escaneo_qr
        RENAME CONSTRAINT ck_escaneo_qr_tipo
        TO chk_escaneo_qr_tipo
    """)
    op.execute("""
        ALTER TABLE public.escaneo_qr
        RENAME CONSTRAINT ck_escaneo_qr_resultado
        TO chk_escaneo_qr_resultado
    """)
    op.execute("""
        ALTER TABLE payment.pago_empresa
        RENAME CONSTRAINT ck_pago_empresa_monto
        TO pago_empresa_monto_check
    """)
    op.execute("""
        ALTER TABLE payment.pago_empresa
        RENAME CONSTRAINT ck_pago_empresa_estado
        TO pago_empresa_estado_check
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_auto_gestion
        TO check_auto_gestion
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_duracion_minima
        TO ck_contrato_duracion_minima
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_horario_valido
        TO ck_contrato_horario_valido
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_activo_estado
        TO ck_contrato_activo_estado
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_porcentaje
        TO check_porcentaje
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_dia_inicio_semana
        TO ck_contrato_dia_inicio_semana
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_extension_valida
        TO ck_contrato_extension_valida
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_estado
        TO ck_contrato_estado
    """)
    op.execute("""
        ALTER TABLE fleet.contrato_vehiculo
        RENAME CONSTRAINT ck_contrato_vehiculo_compensacion_km
        TO ck_contrato_compensacion_km
    """)
    op.execute("""
        ALTER TABLE auth.turno_empleado
        RENAME CONSTRAINT ck_turno_empleado_estado
        TO check_estado_turno
    """)
    op.execute("""
        ALTER TABLE auth.codigo_verificacion
        RENAME CONSTRAINT ck_codigo_verificacion_tipo
        TO chk_codigo_verificacion_tipo
    """)
