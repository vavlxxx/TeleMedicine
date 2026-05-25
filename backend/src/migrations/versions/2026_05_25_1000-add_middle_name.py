"""add middle_name

Revision ID: 5f3c2e9a8e22
Revises: 4f2c1e8a7d11
Create Date: 2026-05-25 10:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5f3c2e9a8e22"
down_revision: str | Sequence[str] | None = "4f2c1e8a7d11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("middle_name", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "middle_name")
