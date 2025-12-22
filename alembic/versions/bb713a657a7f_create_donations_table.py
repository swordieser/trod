"""create donations table

Revision ID: bb713a657a7f
Revises: 6c2478a228a1
Create Date: 2025-12-22 14:53:05.006134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bb713a657a7f'
down_revision: Union[str, Sequence[str], None] = '6c2478a228a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "donations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.func.now()
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id"),
            nullable=False
        ),
        sa.Column(
            "fund_id",
            sa.Integer,
            sa.ForeignKey("funds.id"),
            nullable=False
        ),
        sa.Column(
            "project_id",
            sa.Integer,
            sa.ForeignKey("projects.id"),
            nullable=False
        ),
    )


def downgrade():
    op.drop_table("donations")
