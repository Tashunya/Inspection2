"""empty message

Revision ID: 8b98bbdccfa8
Revises: 2dea0c060f4a
Create Date: 2019-09-02 19:13:28.348011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b98bbdccfa8'
down_revision = '2dea0c060f4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('measurements_boiler_id_fkey', 'measurements', type_='foreignkey')
    op.drop_column('measurements', 'boiler_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('measurements', sa.Column('boiler_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('measurements_boiler_id_fkey', 'measurements', 'boilers', ['boiler_id'], ['id'])
    # ### end Alembic commands ###
