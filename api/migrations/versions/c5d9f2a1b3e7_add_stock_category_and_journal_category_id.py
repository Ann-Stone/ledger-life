"""add Stock_Category dictionary + Stock_Journal.category_id

Revision ID: c5d9f2a1b3e7
Revises: f2c8a4719b3e
Create Date: 2026-05-30 19:10:00.000000

Adds the user-maintained ``Stock_Category`` dictionary and a nullable
``Stock_Journal.category_id`` referencing it. Seeds three starter categories
(成長型 / 債券 / 類現金); existing holdings keep ``category_id = NULL``
(unclassified) until classified through the UI.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c5d9f2a1b3e7'
down_revision: Union[str, Sequence[str], None] = 'f2c8a4719b3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    if 'Stock_Category' not in tables:
        op.create_table(
            'Stock_Category',
            sa.Column('category_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('in_use', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('category_index', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('category_id'),
        )
        op.bulk_insert(
            sa.table(
                'Stock_Category',
                sa.column('category_id', sa.String),
                sa.column('name', sa.String),
                sa.column('in_use', sa.String),
                sa.column('category_index', sa.Integer),
            ),
            [
                {'category_id': 'SC-001', 'name': '成長型', 'in_use': 'Y', 'category_index': 1},
                {'category_id': 'SC-002', 'name': '債券', 'in_use': 'Y', 'category_index': 2},
                {'category_id': 'SC-003', 'name': '類現金', 'in_use': 'Y', 'category_index': 3},
            ],
        )
    if 'Stock_Journal' in tables:
        columns = [c['name'] for c in inspector.get_columns('Stock_Journal')]
        if 'category_id' not in columns:
            op.add_column(
                'Stock_Journal',
                sa.Column('category_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('Stock_Journal', 'category_id')
    op.drop_table('Stock_Category')
