"""add Insurance_Value_History (recorded policy surrender values)

Revision ID: a7d3f9b2c1e4
Revises: 5e415e867e06
Create Date: 2026-06-04 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a7d3f9b2c1e4'
down_revision: Union[str, Sequence[str], None] = '5e415e867e06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the user-recorded surrender-value table.

    Lets a savings policy be valued at its real 解約金 (carried forward from the
    latest recorded month) instead of the net-premium estimate. Composite PK
    (insurance_id, vesting_month) mirrors the other monthly snapshot tables.

    Idempotent: the app's startup ``create_all`` may have already created this
    table, so skip when present (same convention as the Stock_Category migration).
    """
    bind = op.get_bind()
    if 'Insurance_Value_History' not in sa.inspect(bind).get_table_names():
        op.create_table(
            'Insurance_Value_History',
            sa.Column('insurance_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('vesting_month', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('surrender_value', sa.Float(), nullable=False),
            sa.Column('memo', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.PrimaryKeyConstraint('insurance_id', 'vesting_month'),
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('Insurance_Value_History')
