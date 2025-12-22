"""create users table

Revision ID: 6c2478a228a1
Revises: 0d1dff8375ba
Create Date: 2025-12-22 14:52:51.073081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c2478a228a1'
down_revision: Union[str, Sequence[str], None] = '0d1dff8375ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, unique=True, nullable=False),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "admin", name="userrole"),
            nullable=False,
            server_default="user"
        ),
    )


def downgrade():
    op.drop_table("users")
    op.execute("DROP TYPE userrole")
