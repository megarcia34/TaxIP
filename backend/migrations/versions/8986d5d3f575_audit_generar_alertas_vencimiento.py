
"""audit generar alertas vencimiento

Revision ID: '8986d5d3f575'
Revises: f4149e326a1a
Create Date: 2026-07-29
"""
from alembic import op

revision = '8986d5d3f575'
down_revision = 'f4149e326a1a'
branch_labels = None
depends_on = None


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
            dv.id AS documento_id,
            dv.vehiculo_id AS entidad_id,
            'vehiculo' AS entidad_tipo,
            dv.tipo_documento,
            dv.fecha_vencimiento,
            dv.notificar_dias,
            v.patente
        FROM fleet.documentos_vehiculo dv
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
            ) ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;

    -- Alertas para documentos de conductores
    FOR v_registro IN
        SELECT
            dc.id AS documento_id,
            dc.usuario_id AS entidad_id,
            'chofer' AS entidad_tipo,
            dc.tipo_documento,
            dc.fecha_vencimiento,
            dc.notificar_dias,
            COALESCE(p.nombre || ' ' || p.apellido, u.email) AS nombre
        FROM auth.documentos_chofer dc
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
            ) ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(FUNCION_SQL)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS audit.generar_alertas_vencimiento()")