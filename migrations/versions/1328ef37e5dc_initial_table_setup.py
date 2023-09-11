"""Initial table setup

Revision ID: 1328ef37e5dc
Revises: None
Create Date: 2023-09-05 20:21:47.676245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1328ef37e5dc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "ai",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("input_keys", sa.JSON(), nullable=False),
        sa.Column("chain", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "knowledge",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("embeddings", sa.String(), nullable=False),
        sa.Column("chunk_size", sa.Integer(), nullable=False),
        sa.Column("persist_directory", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("passhash", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "settings",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "domain", "name"),
        sa.UniqueConstraint(
            "user_id", "domain", "name", name="settings_user_domain_name"
        ),
    )


def downgrade():
    op.drop_table("settings")
    op.drop_table("user")
    op.drop_table("knowledge")
    op.drop_table("ai")
