"""Add public AIs and Knowledge

Revision ID: 3dba1ccfa13d
Revises: 16c3aa6e11aa
Create Date: 2023-09-14 13:30:34.551156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3dba1ccfa13d"
down_revision = "16c3aa6e11aa"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("ai", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_public", sa.Boolean(), nullable=False, server_default=sa.false()
            )
        )

    with op.batch_alter_table("knowledge", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_public", sa.Boolean(), nullable=False, server_default=sa.false()
            )
        )


def downgrade():
    with op.batch_alter_table("knowledge", schema=None) as batch_op:
        batch_op.drop_column("is_public")

    with op.batch_alter_table("ai", schema=None) as batch_op:
        batch_op.drop_column("is_public")
