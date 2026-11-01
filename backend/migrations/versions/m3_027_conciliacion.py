"""conciliacion: estados y campos en liquidacion

Revision ID: m3_027
Revises: m3_026
Create Date: 2026-11-01

Agrega:
- Estados nuevos a fleet.turno_chofer.estado
- Estados nuevos a fleet.liquidacion.estado
- Campos de conciliacion a fleet.liquidacion
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'm3_027'
down_revision: Union[str, None] = 'm3_026'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # 1. Actualizar CHECK de fleet.turno_chofer.estado
    # ============================================================
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        DROP CONSTRAINT IF EXISTS ck_turno_chofer_estado
    """)
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD CONSTRAINT ck_turno_chofer_estado
        CHECK (estado IN (
            'ACTIVO',
            'PENDIENTE_CONFIRMACION',
            'CON_DIFERENCIAS_PENDIENTES',
            'EN_DISPUTA',
            'CONCILIADO',
            'CONCILIADO_AUTOMATICO',
            'LIQUIDADO',
            'CERRADO',
            'CANCELADO'
        ))
    """)

    # ============================================================
    # 2. Actualizar CHECK de fleet.liquidacion.estado
    # ============================================================
    op.execute("""
        ALTER TABLE fleet.liquidacion
        DROP CONSTRAINT IF EXISTS ck_liquidacion_estado
    """)
    op.execute("""
        ALTER TABLE fleet.liquidacion
        ADD CONSTRAINT ck_liquidacion_estado
        CHECK (estado IN (
            'BORRADOR',
            'CALCULADA',
            'CONCILIADA',
            'CONCILIADA_AUTOMATICA',
            'APROBADA',
            'RECHAZADA',
            'PAGADA',
            'OBSOLETA'
        ))
    """)

    # ============================================================
    # 3. Agregar campos de conciliacion a fleet.liquidacion
    # ============================================================
    op.execute("""
        ALTER TABLE fleet.liquidacion
        ADD COLUMN IF NOT EXISTS conciliado_por UUID
    """)
    op.execute("""
        ALTER TABLE fleet.liquidacion
        ADD COLUMN IF NOT EXISTS conciliado_en TIMESTAMP WITHOUT TIME ZONE
    """)
    op.execute("""
        ALTER TABLE fleet.liquidacion
        ADD COLUMN IF NOT EXISTS tipo_conciliacion VARCHAR(20) NOT NULL DEFAULT 'MANUAL'
    """)

    # FK para conciliado_por
    op.execute("""
        ALTER TABLE fleet.liquidacion
        ADD CONSTRAINT fk_liquidacion_conciliado_por_usuario
        FOREIGN KEY (conciliado_por) REFERENCES auth.usuario(id)
    """)

    # Comentarios (van a la DB, pueden tener tildes)
    op.execute("""
        COMMENT ON COLUMN fleet.liquidacion.conciliado_por
        IS 'Usuario que concilió la liquidación (NULL si fue automático)'
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.liquidacion.conciliado_en
        IS 'Fecha y hora de la conciliación'
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.liquidacion.tipo_conciliacion
        IS 'Tipo de conciliación: MANUAL o AUTOMATICA'
    """)


def downgrade() -> None:
    # Eliminar FK y campos
    op.execute("""
        ALTER TABLE fleet.liquidacion
        DROP CONSTRAINT IF EXISTS fk_liquidacion_conciliado_por_usuario
    """)
    op.execute("""
        ALTER TABLE fleet.liquidacion
        DROP COLUMN IF EXISTS tipo_conciliacion
    """)
    op.execute("""
        ALTER TABLE fleet.liquidacion
        DROP COLUMN IF EXISTS conciliado_en
    """)
    op.execute("""
        ALTER TABLE fleet.liquidacion
        DROP COLUMN IF EXISTS conciliado_por
    """)

    # Restaurar CHECKs originales
    op.execute("""
        ALTER TABLE fleet.liquidacion
        DROP CONSTRAINT IF EXISTS ck_liquidacion_estado
    """)
    op.execute("""
        ALTER TABLE fleet.liquidacion
        ADD CONSTRAINT ck_liquidacion_estado
        CHECK (estado IN (
            'BORRADOR', 'CALCULADA', 'CONCILIADA', 'CERRADA',
            'APROBADA', 'RECHAZADA', 'PAGADA', 'OBSOLETA'
        ))
    """)

    op.execute("""
        ALTER TABLE fleet.turno_chofer
        DROP CONSTRAINT IF EXISTS ck_turno_chofer_estado
    """)
    op.execute("""
        ALTER TABLE fleet.turno_chofer
        ADD CONSTRAINT ck_turno_chofer_estado
        CHECK (estado IN (
            'ACTIVO', 'PENDIENTE_CONFIRMACION', 'LIQUIDADO', 'CERRADO', 'CANCELADO'
        ))
    """)