"""Rename audit.log_gps.timestamp to created_at

Revision ID: m3_009
Revises: m3_008
Create Date: 2026-09-30
"""
from alembic import op
import sqlalchemy as sa


revision = "m3_009"
down_revision = "m3_008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "log_gps",
        "timestamp",
        new_column_name="created_at",
        schema="audit",
    )


def downgrade() -> None:
    op.alter_column(
        "log_gps",
        "created_at",
        new_column_name="timestamp",
        schema="audit",
    )