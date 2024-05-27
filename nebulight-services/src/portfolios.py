from .auth import get_current_user
from .database import get_db
from .models import Portfolio as PortfolioModel, PortfolioEntitlement as PortfolioEntitlementModel
from .utils import to_iso_format
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
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

class PortfolioEntitlementCreate(BaseModel):
    permission: str

class PortfolioEntitlement(BaseModel):
    id: UUID
    portfolio_id: UUID
    user_id: str
    permission: str

    class Config:
        orm_mode = True

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
    owned_portfolios = db.query(PortfolioModel).filter_by(owner=user.id, is_active=True).all()
    shared_entitlements = db.query(PortfolioEntitlementModel).filter_by(user_id=user.id).all()
    shared_portfolio_ids = [ent.portfolio_id for ent in shared_entitlements]
    shared_portfolios = db.query(PortfolioModel).filter(PortfolioModel.id.in_(shared_portfolio_ids), PortfolioModel.is_active==True).all()
    
    portfolios = owned_portfolios + shared_portfolios
    return portfolios

@router.get("/portfolios/{portfolio_id}", response_model=Portfolio)
async def read_portfolio(portfolio_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = db.query(PortfolioModel).filter_by(id=portfolio_id, is_active=True).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    if portfolio.owner != user.id:
        entitlement = db.query(PortfolioEntitlementModel).filter_by(portfolio_id=portfolio_id, user_id=user.id).first()
        if not entitlement:
            raise HTTPException(status_code=403, detail="Not authorized to access this portfolio")
    
    return portfolio

@router.put("/portfolios/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(portfolio_id: str, portfolio: PortfolioCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_portfolio = db.query(PortfolioModel).filter_by(id=portfolio_id, is_active=True).first()
    if not db_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    if db_portfolio.owner != user.id:
        entitlement = db.query(PortfolioEntitlementModel).filter_by(portfolio_id=portfolio_id, user_id=user.id, permission='edit').first()
        if not entitlement:
            raise HTTPException(status_code=403, detail="Not authorized to edit this portfolio")
    
    db_portfolio.name = portfolio.name
    db_portfolio.currency = portfolio.currency
    db_portfolio.updated_at = datetime.now(timezone.utc)
    
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

@router.post("/portfolios/{portfolio_id}/entitlements/{user_id}", response_model=PortfolioEntitlement)
async def create_portfolio_entitlement(portfolio_id: str, user_id: str, entitlement_data: PortfolioEntitlementCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = db.query(PortfolioModel).filter_by(id=portfolio_id, owner=user.id).first()
    if not portfolio:
        raise HTTPException(status_code=403, detail="Only the owner can share the portfolio")
    
    existing_entitlement = db.query(PortfolioEntitlementModel).filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
    if existing_entitlement:
        existing_entitlement.permission = entitlement_data.permission
        db.commit()
        return existing_entitlement

    db_entitlement = PortfolioEntitlementModel(
        id=str(uuid4()),
        portfolio_id=portfolio_id,
        user_id=user_id,
        permission=entitlement_data.permission,
    )
    db.add(db_entitlement)
    db.commit()
    db.refresh(db_entitlement)
    return db_entitlement

@router.delete("/portfolios/{portfolio_id}/entitlements/{user_id}", response_model=dict)
async def revoke_portfolio_entitlement(portfolio_id: str, user_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    entitlement = db.query(PortfolioEntitlementModel).filter_by(portfolio_id=portfolio_id, user_id=user_id).first()
    if not entitlement:
        raise HTTPException(status_code=404, detail="Entitlement not found")
    
    portfolio = entitlement.portfolio
    if portfolio.owner != user.id:
        raise HTTPException(status_code=403, detail="Only the owner can revoke entitlements")
    
    db.delete(entitlement)
    db.commit()
    
    return {"detail": "Entitlement revoked"}