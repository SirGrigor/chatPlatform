"""Initial m1igrati111111

Revision ID: 8a3c707e8b05
Revises: c812ebe7712a
Create Date: 2024-02-04 11:50:33.270810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a3c707e8b05'
down_revision: Union[str, None] = 'c812ebe7712a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gpt_presets', sa.Column('course_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'gpt_presets', 'courses', ['course_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'gpt_presets', type_='foreignkey')
    op.drop_column('gpt_presets', 'course_id')
    # ### end Alembic commands ###
