"""add Retirement_Setting (single-row retirement config)

Revision ID: f4c2d8b1a6e9
Revises: e3b7c2a9f1d4
Create Date: 2026-06-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4c2d8b1a6e9'
down_revision: Union[str, Sequence[str], None] = 'e3b7c2a9f1d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the single-row retirement-config table.

    Stores the withdrawal rate (default 4%), an optional manual annual
    expense-base override, and whether self-occupied housing is excluded from the
    readiness net worth (default true). Idempotent: startup ``create_all`` may
    have already created it (same convention as the House_Price_Index migration);
    the add-column guard also covers dev DBs created before the
    ``exclude_self_occupied_estate`` column existed.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'Retirement_Setting' not in inspector.get_table_names():
        op.create_table(
            'Retirement_Setting',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('withdrawal_rate', sa.Float(), nullable=False),
            sa.Column('annual_expense_override', sa.Float(), nullable=True),
            sa.Column(
                'exclude_self_occupied_estate',
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.PrimaryKeyConstraint('id'),
        )
    else:
        columns = {c['name'] for c in inspector.get_columns('Retirement_Setting')}
        if 'exclude_self_occupied_estate' not in columns:
            op.add_column(
                'Retirement_Setting',
                sa.Column(
                    'exclude_self_occupied_estate',
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.true(),
                ),
            )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('Retirement_Setting')
