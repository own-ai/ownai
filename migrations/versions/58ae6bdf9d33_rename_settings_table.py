"""Rename settings table

Revision ID: 58ae6bdf9d33
Revises: 1328ef37e5dc
Create Date: 2023-09-05 21:09:36.337574

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "58ae6bdf9d33"
down_revision = "1328ef37e5dc"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("settings", "setting")


def downgrade():
    op.rename_table("setting", "settings")
