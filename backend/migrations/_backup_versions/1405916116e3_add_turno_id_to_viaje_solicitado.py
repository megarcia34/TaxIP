

"""add turno id to viaje solicitado

Revision ID: <1405916116e3>
Revises: e6e68da8c451
Create Date: 2026-08-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

revision = '1405916116e3'
down_revision = 'e6e68da8c451'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 1. Agregar columna turno_id (nullable inicialmente)
    # ============================================================
    op.add_column(
        'viaje_solicitado',
        sa.Column('turno_id', UUID(as_uuid=True), nullable=True),
        schema='trip'
    )

    # ============================================================
    # 2. Crear índice para mejorar rendimiento
    # ============================================================
    op.create_index(
        'ix_viaje_solicitado_turno_id',
        'viaje_solicitado',
        ['turno_id'],
        schema='trip'
    )

    # ============================================================
    # 3. Agregar FK (sin validación inmediata para permitir población)
    # ============================================================
    op.create_foreign_key(
        'fk_viaje_solicitado_turno_id',
        'viaje_solicitado',
        'turno_chofer',
        ['turno_id'],
        ['id'],
        source_schema='trip',
        referent_schema='fleet',
        use_alter=True  # Permite crear FKs en tablas con datos existentes
    )

    # ============================================================
    # 4. Poblar turno_id para viajes existentes (atribución conservadora)
    #    Estrategia: asigna el turno cuyo rango temporal contenga
    #    el momento del viaje (finalizado_en o iniciado_en),
    #    matching por vehículo y opcionalmente por chofer.
    # ============================================================
    op.execute(text("""
        UPDATE trip.viaje_solicitado AS vs
        SET turno_id = (
            SELECT t.id
            FROM fleet.turno_chofer AS t
            WHERE t.vehiculo_id = vs.vehiculo_id
              AND (t.chofer_id = vs.chofer_id OR vs.chofer_id IS NULL)
              AND t.inicio_turno <= COALESCE(vs.finalizado_en, vs.iniciado_en, vs.created_at)
              AND (t.fin_turno IS NULL OR t.fin_turno >= COALESCE(vs.iniciado_en, vs.created_at))
            ORDER BY
                -- Priorizar turnos cerrados sobre activos
                CASE WHEN t.fin_turno IS NOT NULL THEN 1 ELSE 2 END,
                -- Dentro de cerrados, el más reciente
                t.fin_turno DESC NULLS LAST,
                -- Dentro de activos, el más antiguo (más probable)
                t.inicio_turno ASC
            LIMIT 1
        )
        WHERE vs.turno_id IS NULL
          AND vs.vehiculo_id IS NOT NULL
          AND (vs.estado = 'finalizado' OR vs.iniciado_en IS NOT NULL);
    """))

    # ============================================================
    # 5. Reporte de viajes sin atribuir (solo informativo)
    # ============================================================
    op.execute(text("""
        DO $$
        DECLARE
            sin_atribuir INTEGER;
            total_viajes INTEGER;
        BEGIN
            SELECT COUNT(*) INTO total_viajes
            FROM trip.viaje_solicitado
            WHERE estado = 'finalizado' OR iniciado_en IS NOT NULL;
            
            SELECT COUNT(*) INTO sin_atribuir
            FROM trip.viaje_solicitado
            WHERE turno_id IS NULL
              AND (estado = 'finalizado' OR iniciado_en IS NOT NULL);
            
            RAISE NOTICE 'Viajes finalizados/iniciados: %, sin turno asignado: %', 
                total_viajes, sin_atribuir;
        END $$;
    """))

    # ============================================================
    # 6. Comentario descriptivo en la columna
    # ============================================================
    op.execute("""
        COMMENT ON COLUMN trip.viaje_solicitado.turno_id IS 
        'Turno al que pertenece el viaje; puede ser NULL para viajes históricos no atribuibles o pendientes de inicio'
    """)


def downgrade() -> None:
    # ============================================================
    # 1. Verificar si hay datos antes de eliminar (advertencia)
    # ============================================================
    op.execute(text("""
        DO $$
        DECLARE
            viajes_con_turno INTEGER;
        BEGIN
            SELECT COUNT(*) INTO viajes_con_turno
            FROM trip.viaje_solicitado
            WHERE turno_id IS NOT NULL;
            
            IF viajes_con_turno > 0 THEN
                RAISE WARNING 'Hay % viajes con turno_id asignado. Se perderá esta información.', viajes_con_turno;
            END IF;
        END $$;
    """))

    # ============================================================
    # 2. Eliminar FK, índice y columna en orden correcto
    # ============================================================
    op.drop_constraint(
        'fk_viaje_solicitado_turno_id', 
        'viaje_solicitado', 
        schema='trip', 
        type_='foreignkey'
    )
    op.drop_index(
        'ix_viaje_solicitado_turno_id', 
        table_name='viaje_solicitado', 
        schema='trip'
    )
    op.drop_column(
        'viaje_solicitado', 
        'turno_id', 
        schema='trip'
    )