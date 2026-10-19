"""create initial database tables

Revision ID: 8843b0b44625
Revises:
Create Date: 2026-10-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8843b0b44625"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial database schema."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("handle", sa.String(length=50), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("max_rating", sa.Integer(), nullable=True),
        sa.Column("rank", sa.String(length=30), nullable=True),
        sa.Column("max_rank", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("handle"),
    )

    op.create_index(
        "ix_users_handle",
        "users",
        ["handle"],
        unique=False,
    )

    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("contest_id", sa.Integer(), nullable=False),
        sa.Column("contest_name", sa.String(length=200), nullable=False),
        sa.Column("old_rating", sa.Integer(), nullable=False),
        sa.Column("new_rating", sa.Integer(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("contest_id", sa.Integer(), nullable=True),
        sa.Column("problem_index", sa.String(length=20), nullable=False),
        sa.Column("problem_name", sa.String(length=300), nullable=False),
        sa.Column("verdict", sa.String(length=50), nullable=False),
        sa.Column(
            "programming_language",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column("submission_time", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contest_id", sa.Integer(), nullable=True),
        sa.Column("problem_index", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("tags", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop the initial database schema."""

    op.drop_table("problems")
    op.drop_table("submissions")
    op.drop_table("ratings")

    op.drop_index(
        "ix_users_handle",
        table_name="users",
    )

    op.drop_table("users")