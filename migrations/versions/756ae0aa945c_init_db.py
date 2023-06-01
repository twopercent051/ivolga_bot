"""init db

Revision ID: 756ae0aa945c
Revises: f20c1172a184
Create Date: 2023-06-01 11:01:32.453840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '756ae0aa945c'
down_revision = 'f20c1172a184'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'user_id')
    op.drop_column('users', 'first_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'name')
    # ### end Alembic commands ###
