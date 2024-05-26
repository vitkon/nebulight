# src/portfolio.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import create_client, Client
from .config import SUPABASE_URL, SUPABASE_KEY
from .auth import get_current_user
from .utils import to_iso_format, remove_sensitive_fields
from datetime import datetime
import logging

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioCreate(BaseModel):
    name: str
    currency: str

class Portfolio(BaseModel):
    id: str
    name: str
    currency: str
    created_at: datetime
    updated_at: datetime

@router.post("/portfolios/", response_model=Portfolio)
async def create_portfolio(portfolio: PortfolioCreate, user=Depends(get_current_user)):
    data = {
        "name": portfolio.name,
        "currency": portfolio.currency,
        "owner": user.id,
        "created_at": to_iso_format(datetime.now()),
        "updated_at": to_iso_format(datetime.now()),
    }


    try:
        response = supabase.table('nebulight_portfolios').insert(data).execute()
        return remove_sensitive_fields(response.data[0])
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred while creating portfolio")

@router.get("/portfolios/", response_model=list[Portfolio])
async def read_user_portfolios(user=Depends(get_current_user)):
    print(user.id)
    try:
        response = (
            supabase.table('nebulight_portfolios')
                .select('*')
                .eq('owner', user.id)
                .eq('is_active', True)
                .execute()
        )
        if not response.data:
            return []
        portfolios = response.data
        for portfolio in portfolios:
            portfolio = remove_sensitive_fields(portfolio)
        return portfolios
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred while reading user portfolios")


@router.get("/portfolios/{portfolio_id}", response_model=Portfolio)
async def read_portfolio(portfolio_id: str, user=Depends(get_current_user)):
    try:
        response = (
            supabase.table('nebulight_portfolios')
                .select('*')
                .eq('id', portfolio_id)
                .eq('is_active', True)
                .execute()
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred while reading user portfolios")
    if response.data[0]['owner'] != user.id:
        raise HTTPException(status_code=403, detail="Portfolio access is forbidden")
    if not response.data:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return remove_sensitive_fields(response.data[0])

@router.put("/portfolios/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(portfolio_id: str, portfolio: PortfolioCreate, user=Depends(get_current_user)):
    
    portfolio_to_update = (
        supabase.table('nebulight_portfolios')
            .select('*')
            .eq('id', portfolio_id)
            .eq('is_active', True)
            .execute()
    )
    if portfolio_to_update.data[0]['owner'] != user.id:
        raise HTTPException(status_code=403, detail="Portfolio update is forbidden")
    
    data = {
        "name": portfolio.name,
        "currency": portfolio.currency,
        "updated_at": to_iso_format(datetime.now()),
    }
    
    try: 
        response = (
            supabase.table('nebulight_portfolios')
                .update(data)
                .eq('id', portfolio_id)
                .eq('is_active', True)
                .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=response.error.message)
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return response.data[0]

@router.delete("/portfolios/{portfolio_id}")
async def delete_portfolio(portfolio_id: str, user=Depends(get_current_user)):
    portfolio_to_delete = (
        supabase.table('nebulight_portfolios')
            .select('*')
            .eq('id', portfolio_id)
            .eq('is_active', True)
            .execute()
    )

    if portfolio_to_delete.data and portfolio_to_delete.data[0]['owner'] != user.id:
        raise HTTPException(status_code=403, detail="Portfolio delete is forbidden")
    
    try:
        data = {
            "is_active": False
        }
        response = (
            supabase.table('nebulight_portfolios')
                .update(data)
                .eq('id', portfolio_id)
                .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=response.error.message)

    if not response.data:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"detail": "Portfolio deleted"}
