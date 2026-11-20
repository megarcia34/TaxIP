"""M3-005: Vista materializada trip.mv_broadcast_kpis

Revision ID: m3_005
Revises: m3_004
Create Date: 2026-09-15
"""
from alembic import op

revision = 'm3_005'
down_revision = 'm3_004'
branch_labels = None
depends_on = None

MV_SQL = """
CREATE MATERIALIZED VIEW trip.mv_broadcast_kpis AS
SELECT
  control_base_id,
  DATE(emitido_en) AS fecha,
  COUNT(*) AS total_broadcasts,
  COUNT(*) FILTER (WHERE respuesta = 'aceptado') AS aceptados,
  COUNT(*) FILTER (WHERE respuesta = 'rechazado') AS rechazados,
  COUNT(*) FILTER (WHERE respuesta = 'timeout') AS timeouts,
  AVG(tiempo_respuesta_segundos) FILTER (WHERE respuesta = 'aceptado') AS tiempo_promedio_aceptacion,
  COUNT(DISTINCT chofer_id) AS choferes_activos,
  COUNT(DISTINCT viaje_id) AS viajes_publicados
FROM trip.broadcast_log
GROUP BY control_base_id, DATE(emitido_en);
CREATE UNIQUE INDEX ix_mv_bk_cb_fecha ON trip.mv_broadcast_kpis (control_base_id, fecha);
"""


def upgrade() -> None:
    op.execute(MV_SQL)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS trip.mv_broadcast_kpis;")
