from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from datetime import datetime
from .database import Base
import uuid

class Portfolio(Base):
    __tablename__ = 'nebulight_portfolios'

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True)
    currency = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    entitlements = relationship("PortfolioEntitlement", back_populates="portfolio")

class PortfolioEntitlement(Base):
    __tablename__ = 'nebulight_portfolio_entitlements'
    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    portfolio_id = Column(SA_UUID(as_uuid=True), ForeignKey('nebulight_portfolios.id'))
    user_id = Column(String)  
    
    permission = Column(Enum('view', 'edit', name='permission_types'))

    portfolio = relationship("Portfolio", back_populates="entitlements")
