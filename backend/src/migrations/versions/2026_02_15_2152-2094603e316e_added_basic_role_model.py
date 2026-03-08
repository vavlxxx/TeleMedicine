"""reserved revision for compatibility

Revision ID: 2094603e316e
Revises: 8093419d4e91
Create Date: 2026-03-08 00:01:00

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "2094603e316e"
down_revision: Union[str, Sequence[str], None] = "8093419d4e91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
