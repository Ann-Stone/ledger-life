"""add Estate_Value_History (recorded real-estate market values)

Revision ID: b8e4c1f6a2d7
Revises: a7d3f9b2c1e4
Create Date: 2026-06-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b8e4c1f6a2d7'
down_revision: Union[str, Sequence[str], None] = 'a7d3f9b2c1e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the user-recorded market-value table for real estate.

    Lets a property be valued at a recorded appraisal (carried forward from the
    latest recorded month) instead of staying flat at purchase cost. Idempotent:
    the app's startup ``create_all`` may have already created this table, so skip
    when present (same convention as the Stock_Category migration).
    """
    bind = op.get_bind()
    if 'Estate_Value_History' not in sa.inspect(bind).get_table_names():
        op.create_table(
            'Estate_Value_History',
            sa.Column('estate_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('vesting_month', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('market_value', sa.Float(), nullable=False),
            sa.Column('memo', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.PrimaryKeyConstraint('estate_id', 'vesting_month'),
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('Estate_Value_History')
