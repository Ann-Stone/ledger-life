"""change Target_Setting.setting_value to str

Revision ID: 87622acdcc6c
Revises: cbe794bb79ba
Create Date: 2026-05-23 14:46:48.606655

SQLite doesn't support `ALTER COLUMN TYPE`. Use `batch_alter_table` so Alembic
recreates the table with the new column type and copies data over.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '87622acdcc6c'
down_revision: Union[str, Sequence[str], None] = 'cbe794bb79ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('Target_Setting') as batch_op:
        batch_op.alter_column(
            'setting_value',
            existing_type=sa.FLOAT(),
            type_=sqlmodel.sql.sqltypes.AutoString(length=45),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('Target_Setting') as batch_op:
        batch_op.alter_column(
            'setting_value',
            existing_type=sqlmodel.sql.sqltypes.AutoString(length=45),
            type_=sa.FLOAT(),
            existing_nullable=False,
        )
