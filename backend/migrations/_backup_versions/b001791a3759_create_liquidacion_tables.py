

"""create liquidacion tables

Revision ID: b001791a3759
Revises: 53a477f5d47c
Create Date: 2026-08-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'b001791a3759'
down_revision = '53a477f5d47c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================================
    # 1. Tabla: fleet.liquidacion
    # ========================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion'
            ) THEN
                CREATE TABLE fleet.liquidacion (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    control_base_id UUID NOT NULL,
                    turno_id UUID NOT NULL,
                    contrato_id UUID NOT NULL,
                    vehiculo_id UUID NOT NULL,
                    chofer_id UUID NOT NULL,
                    propietario_id UUID NOT NULL,
                    tipo_contrato VARCHAR(20) NOT NULL,
                    periodo_desde TIMESTAMP NOT NULL,
                    periodo_hasta TIMESTAMP NOT NULL,
                    monto_bruto NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    total_gastos NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    comision_chofer NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    canon NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    total_chofer NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    total_propietario NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
                    version INTEGER NOT NULL DEFAULT 1,
                    calculada_en TIMESTAMP NOT NULL DEFAULT now(),
                    created_at TIMESTAMP NOT NULL DEFAULT now(),
                    updated_at TIMESTAMP NOT NULL DEFAULT now()
                );
                
                CREATE INDEX ix_liquidacion_turno_id ON fleet.liquidacion(turno_id);
                CREATE INDEX ix_liquidacion_contrato_id ON fleet.liquidacion(contrato_id);
                CREATE INDEX ix_liquidacion_vehiculo_id ON fleet.liquidacion(vehiculo_id);
                CREATE INDEX ix_liquidacion_chofer_id ON fleet.liquidacion(chofer_id);
                CREATE INDEX ix_liquidacion_propietario_id ON fleet.liquidacion(propietario_id);
                CREATE INDEX ix_liquidacion_control_base_id ON fleet.liquidacion(control_base_id);
                
                ALTER TABLE fleet.liquidacion 
                    ADD CONSTRAINT fk_liquidacion_control_base 
                    FOREIGN KEY (control_base_id) REFERENCES tenant.control_base(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion 
                    ADD CONSTRAINT fk_liquidacion_turno 
                    FOREIGN KEY (turno_id) REFERENCES fleet.turno_chofer(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion 
                    ADD CONSTRAINT fk_liquidacion_contrato 
                    FOREIGN KEY (contrato_id) REFERENCES fleet.contrato_vehiculo(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion 
                    ADD CONSTRAINT fk_liquidacion_vehiculo 
                    FOREIGN KEY (vehiculo_id) REFERENCES fleet.vehiculo(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion 
                    ADD CONSTRAINT fk_liquidacion_chofer 
                    FOREIGN KEY (chofer_id) REFERENCES auth.usuario(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion 
                    ADD CONSTRAINT fk_liquidacion_propietario 
                    FOREIGN KEY (propietario_id) REFERENCES auth.usuario(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)

    # ========================================
    # 2. Tabla: fleet.liquidacion_detalle
    # ========================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion_detalle'
            ) THEN
                CREATE TABLE fleet.liquidacion_detalle (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    liquidacion_id UUID NOT NULL,
                    tipo_linea VARCHAR(20) NOT NULL,
                    concepto VARCHAR(255),
                    fuente_tipo VARCHAR(50),
                    fuente_id UUID,
                    monto NUMERIC(12, 2) NOT NULL,
                    signo VARCHAR(5) NOT NULL,
                    meta_data JSONB,
                    created_at TIMESTAMP NOT NULL DEFAULT now()
                );
                
                CREATE INDEX ix_liquidacion_detalle_liquidacion_id ON fleet.liquidacion_detalle(liquidacion_id);
                CREATE INDEX ix_liquidacion_detalle_fuente_id ON fleet.liquidacion_detalle(fuente_id);
                
                ALTER TABLE fleet.liquidacion_detalle 
                    ADD CONSTRAINT fk_liquidacion_detalle_liquidacion 
                    FOREIGN KEY (liquidacion_id) REFERENCES fleet.liquidacion(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)

    # ========================================
    # 3. Tabla: fleet.liquidacion_estado_historial
    # ========================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion_estado_historial'
            ) THEN
                CREATE TABLE fleet.liquidacion_estado_historial (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    liquidacion_id UUID NOT NULL,
                    control_base_id UUID NOT NULL,
                    estado_anterior VARCHAR(20),
                    estado_nuevo VARCHAR(20) NOT NULL,
                    cambiado_por UUID,
                    motivo TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT now()
                );
                
                CREATE INDEX ix_liquidacion_estado_historial_liquidacion_id ON fleet.liquidacion_estado_historial(liquidacion_id);
                
                ALTER TABLE fleet.liquidacion_estado_historial 
                    ADD CONSTRAINT fk_liquidacion_estado_historial_liquidacion 
                    FOREIGN KEY (liquidacion_id) REFERENCES fleet.liquidacion(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion_estado_historial 
                    ADD CONSTRAINT fk_liquidacion_estado_historial_control_base 
                    FOREIGN KEY (control_base_id) REFERENCES tenant.control_base(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion_estado_historial 
                    ADD CONSTRAINT fk_liquidacion_estado_historial_usuario 
                    FOREIGN KEY (cambiado_por) REFERENCES auth.usuario(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)

    # ========================================
    # 4. Tabla: fleet.liquidacion_ajuste
    # ========================================
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'fleet' AND table_name = 'liquidacion_ajuste'
            ) THEN
                CREATE TABLE fleet.liquidacion_ajuste (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    liquidacion_id UUID NOT NULL,
                    control_base_id UUID NOT NULL,
                    tipo_ajuste VARCHAR(20) NOT NULL,
                    monto NUMERIC(12, 2) NOT NULL,
                    motivo TEXT,
                    usuario_id UUID,
                    created_at TIMESTAMP NOT NULL DEFAULT now()
                );
                
                CREATE INDEX ix_liquidacion_ajuste_liquidacion_id ON fleet.liquidacion_ajuste(liquidacion_id);
                
                ALTER TABLE fleet.liquidacion_ajuste 
                    ADD CONSTRAINT fk_liquidacion_ajuste_liquidacion 
                    FOREIGN KEY (liquidacion_id) REFERENCES fleet.liquidacion(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion_ajuste 
                    ADD CONSTRAINT fk_liquidacion_ajuste_control_base 
                    FOREIGN KEY (control_base_id) REFERENCES tenant.control_base(id) ON DELETE CASCADE;
                
                ALTER TABLE fleet.liquidacion_ajuste 
                    ADD CONSTRAINT fk_liquidacion_ajuste_usuario 
                    FOREIGN KEY (usuario_id) REFERENCES auth.usuario(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS fleet.liquidacion_ajuste")
    op.execute("DROP TABLE IF EXISTS fleet.liquidacion_estado_historial")
    op.execute("DROP TABLE IF EXISTS fleet.liquidacion_detalle")
    op.execute("DROP TABLE IF EXISTS fleet.liquidacion")