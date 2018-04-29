"""empty message

Revision ID: 9591e6a8c2f1
Revises: 4ce46ee217f8
Create Date: 2018-04-29 22:34:29.811501

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9591e6a8c2f1'
down_revision = '4ce46ee217f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('post_ibfk_3', 'post', type_='foreignkey')
    op.drop_column('post', 'tag_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('tag_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('post_ibfk_3', 'post', 'tag', ['tag_id'], ['id'])
    # ### end Alembic commands ###
