"""add app options

Revision ID: 6d43758e4cb3
Revises: 2094603e316e
Create Date: 2026-04-23 22:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6d43758e4cb3"
down_revision: str | Sequence[str] | None = "2094603e316e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_options",
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("value", sa.String(length=5000), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_app_options")),
    )
    op.execute(sa.text("INSERT INTO app_options (code, value) VALUES ('app_unavailable', 'false')"))


def downgrade() -> None:
    op.drop_table("app_options")
