"""Add Used Space to Project.

Revision ID: 6ed3d1dc2c99
Revises: 8da678641556
Create Date: 2023-07-27 12:40:04.985350

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6ed3d1dc2c99"
down_revision = "8da678641556"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("project", sa.Column("used_space", sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("project", "used_space")
    # ### end Alembic commands ###