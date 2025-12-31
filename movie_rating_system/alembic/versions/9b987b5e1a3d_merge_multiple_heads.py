"""merge multiple heads

Revision ID: 9b987b5e1a3d
Revises: create_tables, ada54c31500b
Create Date: 2025-12-26 15:20:57.169578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b987b5e1a3d'
down_revision: Union[str, Sequence[str], None] = ('create_tables', 'ada54c31500b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
