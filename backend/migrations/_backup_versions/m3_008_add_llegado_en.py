"""add llegado_en to viaje_solicitado

Revision ID: m3_008
Revises: m3_007
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa


revision = "m3_008"
down_revision = "m3_007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "viaje_solicitado",
        sa.Column("llegado_en", sa.DateTime(), nullable=True),
        schema="trip",
    )
    op.create_index(
        "idx_viajes_llegado_en",
        "viaje_solicitado",
        ["llegado_en"],
        schema="trip",
        postgresql_where=sa.text("llegado_en IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_viajes_llegado_en", schema="trip")
    op.drop_column("viaje_solicitado", "llegado_en", schema="trip")