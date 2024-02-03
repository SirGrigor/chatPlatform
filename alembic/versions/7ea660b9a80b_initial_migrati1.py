"""Initial migrati1

Revision ID: 7ea660b9a80b
Revises: 0c14d3f02c55
Create Date: 2024-02-02 20:28:50.824112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ea660b9a80b'
down_revision: Union[str, None] = '0c14d3f02c55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin_users', sa.Column('user_type', sa.String(length=255), nullable=False))
    op.add_column('external_users', sa.Column('user_type', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('external_users', 'user_type')
    op.drop_column('admin_users', 'user_type')
    # ### end Alembic commands ###
