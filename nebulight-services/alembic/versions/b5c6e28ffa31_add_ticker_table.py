"""add ticker table

Revision ID: b5c6e28ffa31
Revises: 41b4c1466e3d
Create Date: 2024-05-30 23:16:49.204853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c6e28ffa31'
down_revision: Union[str, None] = '41b4c1466e3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nebulight_industries',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_nebulight_industries_id'), 'nebulight_industries', ['id'], unique=False)
    op.create_table('nebulight_tickers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('ticker_symbol', sa.String(length=10), nullable=False),
    sa.Column('exchange', sa.String(length=10), nullable=False),
    sa.Column('company_name', sa.String(length=255), nullable=True),
    sa.Column('industry_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['industry_id'], ['nebulight_industries.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ticker_symbol', 'exchange', name='unique_ticker_exchange')
    )
    op.create_index(op.f('ix_nebulight_tickers_id'), 'nebulight_tickers', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_nebulight_tickers_id'), table_name='nebulight_tickers')
    op.drop_table('nebulight_tickers')
    op.drop_index(op.f('ix_nebulight_industries_id'), table_name='nebulight_industries')
    op.drop_table('nebulight_industries')
    # ### end Alembic commands ###
