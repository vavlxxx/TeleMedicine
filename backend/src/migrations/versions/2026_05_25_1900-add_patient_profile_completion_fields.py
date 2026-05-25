"""add patient profile completion fields

Revision ID: 9d4e8a71c2f3
Revises: 5f3c2e9a8e22
Create Date: 2026-05-25 19:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9d4e8a71c2f3"
down_revision: str | Sequence[str] | None = "5f3c2e9a8e22"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        user_gender_enum = postgresql.ENUM("male", "female", name="user_gender", create_type=False)
        user_gender_enum.create(bind, checkfirst=True)
    else:
        user_gender_enum = sa.Enum("male", "female", name="user_gender")

    op.add_column("users", sa.Column("gender", user_gender_enum, nullable=True))
    op.add_column("users", sa.Column("birth_date", sa.Date(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "birth_date_visible_to_doctors",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_column("users", "birth_date_visible_to_doctors")
    op.drop_column("users", "birth_date")
    op.drop_column("users", "gender")

    if bind.dialect.name == "postgresql":
        user_gender_enum = postgresql.ENUM("male", "female", name="user_gender", create_type=False)
        user_gender_enum.drop(bind, checkfirst=True)
