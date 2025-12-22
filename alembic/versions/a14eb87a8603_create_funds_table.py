"""create funds table

Revision ID: a14eb87a8603
Revises: 
Create Date: 2025-12-22 14:52:21.606928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a14eb87a8603'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.create_table(
        "funds",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("total_collected", sa.Integer, default=0),
        sa.Column("phone", sa.String),
        sa.Column("url", sa.String),
    )

    op.create_table(
        "fund_tags",
        sa.Column(
            "fund_id",
            sa.Integer,
            sa.ForeignKey("funds.id"),
            primary_key=True,
        ),
        sa.Column(
            "tag",
            sa.Enum(
                "животные",
                "культура",
                "природа",
                name="fundtag",
            ),
            primary_key=True,
        ),
    )


def downgrade():
    op.drop_table("funds")
    op.drop_table("fund_tags")
    op.execute("DROP TYPE fundtag")