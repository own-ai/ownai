"""Add greeting and input_labels columns

Revision ID: 16c3aa6e11aa
Revises: 58ae6bdf9d33
Create Date: 2023-09-13 12:08:56.515625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "16c3aa6e11aa"
down_revision = "58ae6bdf9d33"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("ai", schema=None) as batch_op:
        batch_op.add_column(sa.Column("input_labels", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("greeting", sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("ai", schema=None) as batch_op:
        batch_op.drop_column("greeting")
        batch_op.drop_column("input_labels")
