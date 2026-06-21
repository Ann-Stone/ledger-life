"""add House_Price_Index (cached 住宅價格指數 series)

Revision ID: c9f5a2e8d4b1
Revises: b8e4c1f6a2d7
Create Date: 2026-06-04 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c9f5a2e8d4b1'
down_revision: Union[str, Sequence[str], None] = 'b8e4c1f6a2d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the cached house-price-index table.

    Stores the data.gov.tw 住宅價格指數 quarterly series per region. Idempotent:
    startup ``create_all`` may have already created it (same convention as the
    Stock_Category migration).
    """
    bind = op.get_bind()
    if 'House_Price_Index' not in sa.inspect(bind).get_table_names():
        op.create_table(
            'House_Price_Index',
            sa.Column('region', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('quarter', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('index_value', sa.Float(), nullable=False),
            sa.PrimaryKeyConstraint('region', 'quarter'),
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('House_Price_Index')
