"""add fx_code/fx_rate to estate and loan (multi-currency)

Revision ID: 5e415e867e06
Revises: c5d9f2a1b3e7
Create Date: 2026-05-31 00:39:47.146696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5e415e867e06'
down_revision: Union[str, Sequence[str], None] = 'c5d9f2a1b3e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Additive columns with server defaults so existing rows backfill to the base
    currency (TWD / rate 1.0). Estate carries its own currency; the estate/loan
    snapshots store the resolved currency + FX rate at settlement time.
    """
    op.add_column(
        'Estate',
        sa.Column('fx_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='TWD'),
    )
    op.add_column(
        'Estate_Net_Value_History',
        sa.Column('fx_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='TWD'),
    )
    op.add_column(
        'Estate_Net_Value_History',
        sa.Column('fx_rate', sa.Float(), nullable=False, server_default='1.0'),
    )
    op.add_column(
        'Loan_Balance',
        sa.Column('fx_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='TWD'),
    )
    op.add_column(
        'Loan_Balance',
        sa.Column('fx_rate', sa.Float(), nullable=False, server_default='1.0'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('Loan_Balance', 'fx_rate')
    op.drop_column('Loan_Balance', 'fx_code')
    op.drop_column('Estate_Net_Value_History', 'fx_rate')
    op.drop_column('Estate_Net_Value_History', 'fx_code')
    op.drop_column('Estate', 'fx_code')
