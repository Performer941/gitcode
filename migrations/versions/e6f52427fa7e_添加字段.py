"""'添加字段'

Revision ID: e6f52427fa7e
Revises: b839260c57b1
Create Date: 2020-10-09 08:49:03.160829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6f52427fa7e'
down_revision = 'b839260c57b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'comment', 'comment', ['parent_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_column('comment', 'parent_id')
    # ### end Alembic commands ###
