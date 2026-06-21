"""Add Budget.annual_amount and Code_Data.is_annual_event

Revision ID: f2c8a4719b3e
Revises: d4f1e7a2c8b9
Create Date: 2026-05-27 10:00:00.000000

Two-tier budget support:
  - Code_Data.is_annual_event flags a category to be budgeted as a single
    annual envelope instead of 12 monthly amounts.
  - Budget.annual_amount stores that envelope for flagged categories
    (null for ordinary categories, which keep expected01..12).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f2c8a4719b3e'
down_revision: Union[str, Sequence[str], None] = 'd4f1e7a2c8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'Code_Data',
        sa.Column('is_annual_event', sa.Boolean(), nullable=False, server_default=sa.text('0')),
    )
    op.add_column('Budget', sa.Column('annual_amount', sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('Budget') as batch_op:
        batch_op.drop_column('annual_amount')
    with op.batch_alter_table('Code_Data') as batch_op:
        batch_op.drop_column('is_annual_event')
