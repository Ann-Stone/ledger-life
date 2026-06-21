"""Aggregate all domain model packages so SQLModel.metadata is fully populated.

Alembic's ``env.py`` imports this module; every domain sub-package must be
re-exported here for autogenerate to discover the table classes.
"""
from app.models import settings  # noqa: F401
from app.models import monthly_report  # noqa: F401
from app.models import assets  # noqa: F401
from app.models import dashboard  # noqa: F401
from app.models import reports  # noqa: F401
from app.models import utilities  # noqa: F401
