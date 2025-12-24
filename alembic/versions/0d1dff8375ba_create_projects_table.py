"""create projects table

Revision ID: 0d1dff8375ba
Revises: a14eb87a8603
Create Date: 2025-12-22 14:52:39.867410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d1dff8375ba'
down_revision: Union[str, Sequence[str], None] = 'a14eb87a8603'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("goal_amount", sa.Integer),
        sa.Column("collected_amount", sa.Integer, default=0),
        sa.Column("city", sa.String, nullable=True),
        sa.Column("end_date", sa.String, nullable=True),
        sa.Column("main_text", sa.String, nullable=True),
        sa.Column(
            "fund_id",
            sa.Integer,
            sa.ForeignKey("funds.id"),
            nullable=False
        ),
    )


def downgrade():
    op.drop_table("projects")
