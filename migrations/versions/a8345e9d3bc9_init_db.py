"""init db

Revision ID: a8345e9d3bc9
Revises: 756ae0aa945c
Create Date: 2023-06-01 11:02:07.751615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8345e9d3bc9'
down_revision = '756ae0aa945c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_id', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'users', ['user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'user_id')
    # ### end Alembic commands ###