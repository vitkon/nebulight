from .auth import get_current_user
from .database import get_db
from .models import Portfolio as PortfolioModel
from .utils import to_iso_format
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID
from uuid import uuid4
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioCreate(BaseModel):
    name: str
    currency: str

class Portfolio(BaseModel):
    id: UUID
    name: str
    currency: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        exclude = {'owner', 'is_active'}

@router.post("/portfolios/", response_model=Portfolio)
async def create_portfolio(portfolio: PortfolioCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_portfolio = PortfolioModel(
        id=str(uuid4()),
        name=portfolio.name,
        currency=portfolio.currency,
        owner=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.get("/portfolios/", response_model=list[Portfolio])
async def read_user_portfolios(user=Depends(get_current_user), db: Session = Depends(get_db)):
    portfolios = db.query(PortfolioModel).filter_by(owner=user.id, is_active=True).all()
    return portfolios

@router.get("/portfolios/{portfolio_id}", response_model=Portfolio)
async def read_portfolio(portfolio_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = db.query(PortfolioModel).filter_by(id=portfolio_id, is_active=True).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.owner != user.id:
        raise HTTPException(status_code=403, detail="Portfolio access is forbidden")
    return portfolio

@router.put("/portfolios/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(portfolio_id: str, portfolio: PortfolioCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_portfolio = db.query(PortfolioModel).filter_by(id=portfolio_id, is_active=True).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if db_portfolio.owner != user.id:
        raise HTTPException(status_code=403, detail="Portfolio update is forbidden")
    
    db_portfolio.name = portfolio.name
    db_portfolio.currency = portfolio.currency
    db_portfolio.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.delete("/portfolios/{portfolio_id}")
async def delete_portfolio(portfolio_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_portfolio = db.query(PortfolioModel).filter_by(id=portfolio_id, is_active=True).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if db_portfolio.owner != user.id:
        raise HTTPException(status_code=403, detail="Portfolio delete is forbidden")
    
    db_portfolio.is_active = False
    db.commit()
    return {"detail": "Portfolio deleted"}
