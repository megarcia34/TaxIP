
"""correcciones escaneo qr y snapshots turno

Revision ID: e6e68da8c451
Revises: 49452ce684ec
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa

revision = 'e6e68da8c451'
down_revision = '49452ce684ec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 1. Permitir NULL en comercio_id de public.escaneo_qr
    # Motivo: Los nuevos tipos de QR (OPERATIVO, VEHICULO) no están
    #         vinculados a un comercio, solo los QR de COMERCIO sí.
    # ============================================================
    op.execute("""
        ALTER TABLE public.escaneo_qr 
        ALTER COLUMN comercio_id DROP NOT NULL
    """)
    
    # Agregar comentario para documentar el cambio
    op.execute("""
        COMMENT ON COLUMN public.escaneo_qr.comercio_id IS 
        'ID del comercio escaneado. NULL para QRs de tipo OPERATIVO o VEHICULO.'
    """)
    
    # ============================================================
    # 2. Agregar columnas snapshot a fleet.turno_chofer
    # Motivo: Capturar el contexto contractual del turno al momento
    #         del inicio, para auditoría y cálculos históricos
    #         (ej. si el contrato cambia después, el turno ya iniciado
    #         conserva los valores originales).
    # ============================================================
    op.add_column(
        'turno_chofer', 
        sa.Column('snapshot_dia_contractual', sa.String(20), nullable=True), 
        schema='fleet'
    )
    op.add_column(
        'turno_chofer', 
        sa.Column('snapshot_turno_contractual', sa.String(20), nullable=True), 
        schema='fleet'
    )
    
    # Comentarios descriptivos
    op.execute("""
        COMMENT ON COLUMN fleet.turno_chofer.snapshot_dia_contractual IS 
        'Día contractual al inicio del turno (ej. LUNES, MARTES). Snapshot inmutable.'
    """)
    op.execute("""
        COMMENT ON COLUMN fleet.turno_chofer.snapshot_turno_contractual IS 
        'Turno contractual al inicio (ej. DIURNO, NOCTURNO, COMPLETO). Snapshot inmutable.'
    """)


def downgrade() -> None:
    # ============================================================
    # 1. Eliminar columnas snapshot
    # ============================================================
    op.drop_column('turno_chofer', 'snapshot_turno_contractual', schema='fleet')
    op.drop_column('turno_chofer', 'snapshot_dia_contractual', schema='fleet')
    
    # ============================================================
    # 2. Restaurar NOT NULL en comercio_id
    # IMPORTANTE: Si hay registros con comercio_id = NULL, esto fallará.
    # Primero verificamos y, si es necesario, eliminamos esos registros
    # o los asignamos a un comercio por defecto.
    # ============================================================
    op.execute("""
        DO $$
        DECLARE
            null_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO null_count
            FROM public.escaneo_qr
            WHERE comercio_id IS NULL;
            
            IF null_count > 0 THEN
                RAISE WARNING 'Hay % registros en escaneo_qr con comercio_id NULL. No se puede restaurar NOT NULL.', null_count;
                RAISE WARNING 'Elimine o actualice esos registros manualmente antes de hacer downgrade.';
                RAISE EXCEPTION 'Downgrade abortado: existen registros con comercio_id NULL';
            END IF;
        END $$;
    """)
    
    op.execute("""
        ALTER TABLE public.escaneo_qr 
        ALTER COLUMN comercio_id SET NOT NULL
    """)