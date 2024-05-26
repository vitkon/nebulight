from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timezone
from datetime import datetime
from .database import Base

class Portfolio(Base):
    __tablename__ = "nebulight_portfolios"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    currency = Column(String)
    owner = Column(String, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
