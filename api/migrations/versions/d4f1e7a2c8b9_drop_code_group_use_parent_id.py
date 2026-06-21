"""Drop code_group / code_group_name, backfill parent_id

Revision ID: d4f1e7a2c8b9
Revises: 537401e5a7b2
Create Date: 2026-05-24 12:00:00.000000

Aligns Code_Data hierarchy with the new project's `parent_id` design.

The legacy table tracked parent/child via `code_group` (FK to parent's code_id)
and denormalized the parent's display name into `code_group_name`. The new
project added `parent_id` as the self-FK but never migrated existing data, so
all rows had parent_id IS NULL while the real hierarchy lived in code_group.

This migration:
  1. Copies code_group values into parent_id.
  2. Drops code_group and the denormalized code_group_name (derivable by join).
"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd4f1e7a2c8b9'
down_revision: Union[str, Sequence[str], None] = '537401e5a7b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE Code_Data SET parent_id = code_group "
        "WHERE code_group IS NOT NULL AND parent_id IS NULL"
    )
    with op.batch_alter_table('Code_Data') as batch_op:
        batch_op.drop_column('code_group_name')
        batch_op.drop_column('code_group')


def downgrade() -> None:
    with op.batch_alter_table('Code_Data') as batch_op:
        batch_op.add_column(
            sa.Column('code_group', sqlmodel.sql.sqltypes.AutoString(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('code_group_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True)
        )
    op.execute(
        "UPDATE Code_Data SET code_group = parent_id WHERE parent_id IS NOT NULL"
    )
    op.execute(
        "UPDATE Code_Data AS child SET code_group_name = ("
        "SELECT parent.name FROM Code_Data AS parent WHERE parent.code_id = child.code_group"
        ") WHERE child.code_group IS NOT NULL"
    )
