"""fill_db

Revision ID: d11d4cbf9e35
Revises: 575eeb473830
Create Date: 2026-01-13 19:33:46.541625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd11d4cbf9e35'
down_revision: Union[str, Sequence[str], None] = '575eeb473830'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    """Remove data inserted in upgrade"""
    pass
