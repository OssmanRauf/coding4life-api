"""create header_img column in post table

Revision ID: 5c86fa3eb494
Revises: 
Create Date: 2022-10-24 20:31:41.393594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c86fa3eb494'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("header_img", sa.String(), nullable=True))
    pass


def downgrade():
    op.drop_column("posts", "header_img")
    pass
