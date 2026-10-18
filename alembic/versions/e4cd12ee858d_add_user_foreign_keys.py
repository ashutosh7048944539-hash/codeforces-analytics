"""add user foreign keys

Revision ID: e4cd12ee858d
Revises: 8843b0b44625
Create Date: 2026-10-19 01:35:25.926189

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e4cd12ee858d"
down_revision: Union[str, Sequence[str], None] = "8843b0b44625"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add foreign keys from ratings and submissions to users."""

    op.create_foreign_key(
        "fk_ratings_user_id_users",
        "ratings",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_submissions_user_id_users",
        "submissions",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove foreign keys from ratings and submissions."""

    op.drop_constraint(
        "fk_submissions_user_id_users",
        "submissions",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_ratings_user_id_users",
        "ratings",
        type_="foreignkey",
    )