from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from datetime import datetime
from .database import Base
import uuid


class Portfolio(Base):
    __tablename__ = 'nebulight_portfolios'

    id = Column(SA_UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, index=True)
    currency = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    entitlements = relationship(
        "PortfolioEntitlement", back_populates="portfolio")


class PortfolioEntitlement(Base):
    __tablename__ = 'nebulight_portfolio_entitlements'
    id = Column(SA_UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    portfolio_id = Column(SA_UUID(as_uuid=True),
                          ForeignKey('nebulight_portfolios.id'))
    user_id = Column(String)

    permission = Column(Enum('view', 'edit', name='permission_types'))

    portfolio = relationship("Portfolio", back_populates="entitlements")


class Industry(Base):
    __tablename__ = 'nebulight_industries'
    id = Column(SA_UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True, nullable=False)


class Sector(Base):
    __tablename__ = 'nebulight_sectors'
    id = Column(SA_UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True, nullable=False)


class Ticker(Base):
    __tablename__ = 'nebulight_tickers'
    id = Column(SA_UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    ticker_symbol = Column(String(10), nullable=False)
    exchange = Column(String(10), nullable=False)
    company_name = Column(String(255))
    type = Column(String(255))
    industry_id = Column(SA_UUID(as_uuid=True),
                         ForeignKey('nebulight_industries.id'))
    sector_id = Column(SA_UUID(as_uuid=True),
                       ForeignKey('nebulight_sectors.id'))
    __table_args__ = (UniqueConstraint(
        'ticker_symbol', 'exchange', name='unique_ticker_exchange'),)
