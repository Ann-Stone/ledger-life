"""add Estate.region (house-price-index region)

Revision ID: d1a6b3e9c7f2
Revises: c9f5a2e8d4b1
Create Date: 2026-06-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd1a6b3e9c7f2'
down_revision: Union[str, Sequence[str], None] = 'c9f5a2e8d4b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add nullable Estate.region used to pick the house-price-index series.

    Idempotent: startup ``create_all`` adds the column on a fresh model, so skip
    when it already exists (same convention as the Stock_Journal.category_id migration).
    """
    bind = op.get_bind()
    cols = [c['name'] for c in sa.inspect(bind).get_columns('Estate')]
    if 'region' not in cols:
        op.add_column(
            'Estate',
            sa.Column('region', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('Estate', 'region')
