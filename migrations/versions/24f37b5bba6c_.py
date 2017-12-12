"""empty message

Revision ID: 24f37b5bba6c
Revises: 164f741b4f86
Create Date: 2017-12-11 16:46:22.614245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24f37b5bba6c'
down_revision = '164f741b4f86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tag', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tag', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tag', type_='foreignkey')
    op.drop_column('tag', 'user_id')
    # ### end Alembic commands ###