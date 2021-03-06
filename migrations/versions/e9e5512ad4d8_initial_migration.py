"""initial migration

Revision ID: e9e5512ad4d8
Revises: 
Create Date: 2019-09-16 16:27:02.500626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9e5512ad4d8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('companies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_name', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('about', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_company_name'), 'companies', ['company_name'], unique=True)
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('boilers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('boiler_name', sa.String(length=64), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_boilers_boiler_name'), 'boilers', ['boiler_name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('contact_number', sa.String(length=64), nullable=True),
    sa.Column('position', sa.String(length=64), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_table('nodes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('boiler_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('index', sa.Integer(), nullable=True),
    sa.Column('node_name', sa.String(length=64), nullable=True),
    sa.Column('picture', sa.LargeBinary(), nullable=True),
    sa.ForeignKeyConstraint(['boiler_id'], ['boilers.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['nodes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('measurements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inspector_id', sa.Integer(), nullable=True),
    sa.Column('node_id', sa.Integer(), nullable=True),
    sa.Column('measure_date', sa.DateTime(), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['inspector_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['node_id'], ['nodes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('norms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('default', sa.Float(), nullable=True),
    sa.Column('minor', sa.Float(), nullable=True),
    sa.Column('major', sa.Float(), nullable=True),
    sa.Column('defect', sa.Float(), nullable=True),
    sa.Column('node_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['node_id'], ['nodes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('norms')
    op.drop_table('measurements')
    op.drop_table('nodes')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_boilers_boiler_name'), table_name='boilers')
    op.drop_table('boilers')
    op.drop_table('roles')
    op.drop_index(op.f('ix_companies_company_name'), table_name='companies')
    op.drop_table('companies')
    # ### end Alembic commands ###
