from fastapi import FastAPI, Query
from mangum import Mangum
import yfinance as yf
import pandas as pd
from supabase import create_client, Client
from .models import Base
from .database import engine
from .auth import router as auth_router
from .portfolios import router as portfolio_router
from .symbol_search import router as symbol_search_router
from .config import SUPABASE_URL, SUPABASE_KEY
import os

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


Base.metadata.create_all(bind=engine)

api_prefix="/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(portfolio_router, prefix=api_prefix)
app.include_router(symbol_search_router, prefix=api_prefix)

@app.get("/")
def root():
    return {'message': 'Nebulight API'}

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f'Hello from FastAPI, {name}!'}

@app.get("/historical/{symbol}")
def fin(symbol: str):
    # Calculate end_date as the last business day
    end_date = datetime.now() - BDay(0)  # Adjusts to the previous business day
    start_date = end_date - pd.DateOffset(months=3)  # 3 months before end_date
    
    try:
        # Download historical stock data
        data = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

        # Check if data is empty
        if data.empty:
            return {"error": f"No data found for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}."}

        data = data.iloc[::-1]
        
        # Prepare an array of dictionaries, each containing date and close price
        close_prices = [
            {"date": idx.strftime('%Y-%m-%d'), "close_price": row['Close']}
            for idx, row in data.iterrows()
        ]

        # Return a dictionary containing the symbol and the array of close prices
        return {"symbol": symbol, "close_prices": close_prices}
    except Exception as e:
        return {"error": "Failed to fetch data", "message": str(e)}



handler = Mangum(app)