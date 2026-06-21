"""normalize Alarm.alarm_date to MMDD/DD

Revision ID: 537401e5a7b2
Revises: 87622acdcc6c
Create Date: 2026-05-23 21:15:01.149907

Truncates `Alarm.alarm_date` to its recurring anchor portion:
  * `alarm_type='Y'` rows: any 8-char `YYYYMMDD` becomes the trailing 4-char `MMDD`.
  * `alarm_type='M'` rows: any 4+ char value becomes the trailing 2-char `DD`.

Idempotent: rows that are already at the canonical length are skipped.
Downgrade is lossy (the original year/month info is not recoverable), so we
prepend a placeholder year/month based on the current date to restore the
8-char format if a roll-back is requested. This is best-effort only.
"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '537401e5a7b2'
down_revision: Union[str, Sequence[str], None] = '87622acdcc6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Truncate alarm_date to recurring anchor."""
    # Y rows stored as YYYYMMDD → keep trailing MMDD
    op.execute(
        sa.text(
            "UPDATE Alarm SET alarm_date = SUBSTR(alarm_date, 5, 4) "
            "WHERE alarm_type = 'Y' AND LENGTH(alarm_date) = 8"
        )
    )
    # M rows stored as YYYYMMDD → keep trailing DD
    op.execute(
        sa.text(
            "UPDATE Alarm SET alarm_date = SUBSTR(alarm_date, 7, 2) "
            "WHERE alarm_type = 'M' AND LENGTH(alarm_date) = 8"
        )
    )
    # M rows stored as MMDD (4 char) → keep trailing DD
    op.execute(
        sa.text(
            "UPDATE Alarm SET alarm_date = SUBSTR(alarm_date, 3, 2) "
            "WHERE alarm_type = 'M' AND LENGTH(alarm_date) = 4"
        )
    )


def downgrade() -> None:
    """Best-effort restore to YYYYMMDD using the current year (lossy)."""
    placeholder_year = datetime.now().strftime("%Y")
    placeholder_month = "01"
    op.execute(
        sa.text(
            "UPDATE Alarm SET alarm_date = :year || alarm_date "
            "WHERE alarm_type = 'Y' AND LENGTH(alarm_date) = 4"
        ).bindparams(year=placeholder_year)
    )
    op.execute(
        sa.text(
            "UPDATE Alarm SET alarm_date = :year || :month || alarm_date "
            "WHERE alarm_type = 'M' AND LENGTH(alarm_date) = 2"
        ).bindparams(year=placeholder_year, month=placeholder_month)
    )
