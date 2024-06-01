"""remove industry from ticker

Revision ID: d1bf025b9bb6
Revises: da944bfc8e62
Create Date: 2024-06-01 14:34:55.023415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1bf025b9bb6'
down_revision: Union[str, None] = 'da944bfc8e62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('nebulight_tickers_industry_id_fkey', 'nebulight_tickers', type_='foreignkey')
    op.drop_column('nebulight_tickers', 'industry_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('nebulight_tickers', sa.Column('industry_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('nebulight_tickers_industry_id_fkey', 'nebulight_tickers', 'nebulight_industries', ['industry_id'], ['id'])
    # ### end Alembic commands ###
