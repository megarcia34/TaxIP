


"""fix documentos alertas vencimiento

Revision ID: 'e4d29503431d'
Revises: 8986d5d3f575
Create Date: 2026-07-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e4d29503431d'
down_revision = '8986d5d3f575'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 0. Crear tabla audit.alertas_vencimiento (con UNIQUE para ON CONFLICT)
    op.create_table(
        'alertas_vencimiento',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('entidad_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entidad_tipo', sa.String(20), nullable=False),
        sa.Column('documento_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('nivel', sa.String(20), nullable=False),
        sa.Column('fecha_vencimiento', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('documento_id', name='uq_alertas_documento'),
        schema='audit'
    )
    op.create_index('idx_alertas_entidad', 'alertas_vencimiento', ['entidad_id', 'entidad_tipo'], schema='audit')
    op.create_index('idx_alertas_fecha', 'alertas_vencimiento', ['fecha_vencimiento'], schema='audit')

    # 1. Agregar columnas faltantes a fleet.documento_vehiculo
    op.add_column('documento_vehiculo', sa.Column('activo', sa.Boolean(), server_default='true', nullable=False), schema='fleet')
    op.add_column('documento_vehiculo', sa.Column('notificar_dias', sa.Integer(), server_default='30', nullable=False), schema='fleet')

    # 2. Agregar columnas faltantes a fleet.documentos_chofer
    op.add_column('documentos_chofer', sa.Column('fecha_vencimiento', sa.Date(), nullable=True), schema='fleet')
    op.add_column('documentos_chofer', sa.Column('notificar_dias', sa.Integer(), server_default='30', nullable=False), schema='fleet')
    op.add_column('documentos_chofer', sa.Column('activo', sa.Boolean(), server_default='true', nullable=False), schema='fleet')

    # 3. Recrear la función con los nombres correctos de tablas y schemas
    FUNCION_SQL = """
    CREATE OR REPLACE FUNCTION audit.generar_alertas_vencimiento()
    RETURNS VOID AS $$
    DECLARE
        v_registro RECORD;
        v_dias INTEGER;
        v_nivel VARCHAR(20);
    BEGIN
        -- Alertas para documentos de vehículos
        FOR v_registro IN 
            SELECT 
                dv.id as documento_id,
                dv.vehiculo_id as entidad_id,
                'vehiculo' as entidad_tipo,
                dv.tipo_documento,
                dv.fecha_vencimiento,
                dv.notificar_dias,
                v.patente
            FROM fleet.documento_vehiculo dv
            JOIN fleet.vehiculo v ON v.id = dv.vehiculo_id
            WHERE dv.activo = true
              AND dv.fecha_vencimiento >= CURRENT_DATE
        LOOP
            v_dias := EXTRACT(DAY FROM v_registro.fecha_vencimiento - CURRENT_DATE)::INTEGER;
            
            IF v_dias <= v_registro.notificar_dias THEN
                IF v_dias <= 7 THEN
                    v_nivel := 'critical';
                ELSIF v_dias <= 15 THEN
                    v_nivel := 'warning';
                ELSE
                    v_nivel := 'info';
                END IF;
                
                INSERT INTO audit.alertas_vencimiento (
                    id, entidad_id, entidad_tipo, documento_id,
                    mensaje, nivel, fecha_vencimiento, created_at
                ) VALUES (
                    gen_random_uuid(),
                    v_registro.entidad_id,
                    v_registro.entidad_tipo,
                    v_registro.documento_id,
                    '📄 ' || v_registro.tipo_documento || ' del vehículo ' || v_registro.patente || ' vence en ' || v_dias || ' días',
                    v_nivel,
                    v_registro.fecha_vencimiento,
                    NOW()
                ) ON CONFLICT (documento_id) DO NOTHING;
            END IF;
        END LOOP;

        -- Alertas para documentos de conductores
        FOR v_registro IN 
            SELECT 
                dc.id as documento_id,
                dc.usuario_id as entidad_id,
                'chofer' as entidad_tipo,
                dc.tipo_documento,
                dc.fecha_vencimiento,
                dc.notificar_dias,
                COALESCE(p.nombre || ' ' || p.apellido, u.email) as nombre
            FROM fleet.documentos_chofer dc
            JOIN auth.usuario u ON u.id = dc.usuario_id
            LEFT JOIN auth.perfil_general p ON p.usuario_id = u.id
            WHERE dc.activo = true
              AND dc.fecha_vencimiento >= CURRENT_DATE
        LOOP
            v_dias := EXTRACT(DAY FROM v_registro.fecha_vencimiento - CURRENT_DATE)::INTEGER;
            
            IF v_dias <= v_registro.notificar_dias THEN
                IF v_dias <= 7 THEN
                    v_nivel := 'critical';
                ELSIF v_dias <= 15 THEN
                    v_nivel := 'warning';
                ELSE
                    v_nivel := 'info';
                END IF;
                
                INSERT INTO audit.alertas_vencimiento (
                    id, entidad_id, entidad_tipo, documento_id,
                    mensaje, nivel, fecha_vencimiento, created_at
                ) VALUES (
                    gen_random_uuid(),
                    v_registro.entidad_id,
                    v_registro.entidad_tipo,
                    v_registro.documento_id,
                    '📄 ' || v_registro.tipo_documento || ' del conductor ' || v_registro.nombre || ' vence en ' || v_dias || ' días',
                    v_nivel,
                    v_registro.fecha_vencimiento,
                    NOW()
                ) ON CONFLICT (documento_id) DO NOTHING;
            END IF;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """
    op.execute(FUNCION_SQL)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS audit.generar_alertas_vencimiento()")
    op.drop_table('alertas_vencimiento', schema='audit')
    op.drop_column('documentos_chofer', 'activo', schema='fleet')
    op.drop_column('documentos_chofer', 'notificar_dias', schema='fleet')
    op.drop_column('documentos_chofer', 'fecha_vencimiento', schema='fleet')
    op.drop_column('documento_vehiculo', 'notificar_dias', schema='fleet')
    op.drop_column('documento_vehiculo', 'activo', schema='fleet')