"""merge liquidacion and rename migrations

Revision ID: 6553ec8a1785
Revises: 915d4cfb4388, b001791a3759
Create Date: 2026-08-10 20:53:27.394672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6553ec8a1785'
down_revision: Union[str, Sequence[str], None] = ('915d4cfb4388', 'b001791a3759')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
