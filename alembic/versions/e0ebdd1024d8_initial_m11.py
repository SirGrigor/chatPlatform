"""Initial m11

Revision ID: e0ebdd1024d8
Revises: d5689789b05e
Create Date: 2024-02-05 22:55:12.832991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0ebdd1024d8'
down_revision: Union[str, None] = 'd5689789b05e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chat_sessions', 'conversation_history',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chat_sessions', 'conversation_history',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    # ### end Alembic commands ###