"""conciliacion: tablas de diferencias y disputas

Revision ID: m3_028
Revises: m3_027
Create Date: 2026-11-01

Agrega:
- Tabla fleet.conciliacion_diferencia
- Tabla fleet.conciliacion_disputa
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'm3_028'
down_revision: Union[str, None] = 'm3_027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # 1. Crear tabla fleet.conciliacion_diferencia
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.conciliacion_diferencia (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            turno_id UUID NOT NULL,
            liquidacion_id UUID,
            tipo VARCHAR(30) NOT NULL,
            concepto VARCHAR(50) NOT NULL,
            monto NUMERIC NOT NULL,
            descripcion TEXT,
            estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
            saldada_en TIMESTAMP WITHOUT TIME ZONE,
            saldada_por UUID,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_conciliacion_diferencia_turno_chofer
                FOREIGN KEY (turno_id) REFERENCES fleet.turno_chofer(id),
            CONSTRAINT fk_conciliacion_diferencia_liquidacion
                FOREIGN KEY (liquidacion_id) REFERENCES fleet.liquidacion(id),
            CONSTRAINT fk_conciliacion_diferencia_saldada_por_usuario
                FOREIGN KEY (saldada_por) REFERENCES auth.usuario(id),
            CONSTRAINT ck_conciliacion_diferencia_tipo
                CHECK (tipo IN ('DEUDA_CHOFER', 'DEUDA_PROPIETARIO', 'NEUTRA')),
            CONSTRAINT ck_conciliacion_diferencia_estado
                CHECK (estado IN ('PENDIENTE', 'SALDADA'))
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_conciliacion_diferencia_turno_estado
        ON fleet.conciliacion_diferencia (turno_id, estado)
    """)
    op.execute("""
        COMMENT ON TABLE fleet.conciliacion_diferencia
        IS 'Diferencias detectadas durante la conciliación de un turno'
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.conciliacion_diferencia.tipo
        IS 'DEUDA_CHOFER: el chofer debe al propietario. DEUDA_PROPIETARIO: el propietario debe al chofer. NEUTRA: saldada automáticamente'
    """)

    # ============================================================
    # 2. Crear tabla fleet.conciliacion_disputa
    # ============================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.conciliacion_disputa (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            turno_id UUID NOT NULL,
            abierta_por UUID NOT NULL,
            motivo TEXT NOT NULL,
            estado VARCHAR(30) NOT NULL DEFAULT 'ABIERTA',
            resolucion TEXT,
            resuelta_por UUID,
            resuelta_en TIMESTAMP WITHOUT TIME ZONE,
            plazo_tenant TIMESTAMP WITHOUT TIME ZONE,
            plazo_plataforma TIMESTAMP WITHOUT TIME ZONE,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_conciliacion_disputa_turno_chofer
                FOREIGN KEY (turno_id) REFERENCES fleet.turno_chofer(id),
            CONSTRAINT fk_conciliacion_disputa_abierta_por_usuario
                FOREIGN KEY (abierta_por) REFERENCES auth.usuario(id),
            CONSTRAINT fk_conciliacion_disputa_resuelta_por_usuario
                FOREIGN KEY (resuelta_por) REFERENCES auth.usuario(id),
            CONSTRAINT ck_conciliacion_disputa_estado
                CHECK (estado IN ('ABIERTA', 'EN_TENANT', 'EN_PLATAFORMA', 'RESUELTA', 'CERRADA_AUTOMATICA'))
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_conciliacion_disputa_turno_estado
        ON fleet.conciliacion_disputa (turno_id, estado)
    """)
    op.execute("""
        COMMENT ON TABLE fleet.conciliacion_disputa
        IS 'Disputas abiertas por chofer o propietario sobre una conciliación'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS fleet.conciliacion_disputa")
    op.execute("DROP TABLE IF EXISTS fleet.conciliacion_diferencia")