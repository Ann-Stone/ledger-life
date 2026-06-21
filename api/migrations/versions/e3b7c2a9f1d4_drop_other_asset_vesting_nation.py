"""drop redundant Other_Asset.vesting_nation

Revision ID: e3b7c2a9f1d4
Revises: d1a6b3e9c7f2
Create Date: 2026-06-06 12:00:00.000000

The ``vesting_nation`` column was inert metadata — no settlement / report / FX
code ever read it, and every valued asset carries its own currency source
(Estate.fx_code, Stock via settling account, Insurance via in/out account).
Drop it rather than keep a second, unconsumed currency-ish field.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e3b7c2a9f1d4'
down_revision: Union[str, Sequence[str], None] = 'd1a6b3e9c7f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop Other_Asset.vesting_nation (SQLite-safe batch rebuild).

    Idempotent: a fresh DB built from the current model via ``create_all`` already
    omits the column, so skip the drop when it is no longer present.
    """
    bind = op.get_bind()
    cols = [c['name'] for c in sa.inspect(bind).get_columns('Other_Asset')]
    if 'vesting_nation' in cols:
        with op.batch_alter_table('Other_Asset') as batch_op:
            batch_op.drop_column('vesting_nation')


def downgrade() -> None:
    """Re-add the column (non-null with empty-string default, since the original
    was NOT NULL and historical values are not recoverable)."""
    bind = op.get_bind()
    cols = [c['name'] for c in sa.inspect(bind).get_columns('Other_Asset')]
    if 'vesting_nation' not in cols:
        with op.batch_alter_table('Other_Asset') as batch_op:
            batch_op.add_column(
                sa.Column(
                    'vesting_nation',
                    sqlmodel.sql.sqltypes.AutoString(),
                    nullable=False,
                    server_default='',
                ),
            )
