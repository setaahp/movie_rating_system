"""create_tables

Revision ID: ada54c31500b
Revises: b5a7984b2776
Create Date: 2025-12-22 23:29:24.107636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ada54c31500b'
down_revision: Union[str, Sequence[str], None] = 'b5a7984b2776'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
