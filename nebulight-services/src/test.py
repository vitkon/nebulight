from fastapi import FastAPI, Query
from mangum import Mangum
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

app = FastAPI()

def get_sp500_tickers():
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500 = table[0]  # The first table contains the ticker symbols
    tickers = sp500['Symbol'].tolist()
    return tickers

def get_market_caps(tickers):
    market_caps = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        market_cap = stock.info.get('marketCap')
        if market_cap:
            market_caps[ticker] = market_cap
    return market_caps

def get_volatility_percent(ticker_symbol, period='1y'):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)
    
    # Calculate daily returns
    daily_returns = hist['Close'].pct_change()
    
    # Calculate volatility (standard deviation of daily returns)
    volatility = daily_returns.std()
    
    # Convert to percentage
    volatility_percent = volatility * 100
    
    return volatility_percent

def get_trend_change(symbol: str, months: int):
    # Calculate the start and end dates
    end_date = datetime.now() - timedelta(days=1)  # Yesterday
    start_date = end_date - relativedelta(months=months)  # 3 months before end_date

    # Fetch historical data for the symbol
    data = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    
    if data.empty:
        raise ValueError(f"No data found for {symbol} between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")

    # Calculate the short-term (12-day) and long-term (26-day) EMAs
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
    
    # Identify crossovers and signal trend direction
    data['Signal'] = 0  # Default value
    data['Signal'][data['EMA_12'] > data['EMA_26']] = 1  # Upward trend signal
    data['Signal'][data['EMA_12'] < data['EMA_26']] = -1  # Downward trend signal
    
    # Detect signals (change in trend)
    data['Entry_Signal'] = data['Signal'].diff()
    
    # Filter for all signals and prepare the response
    signals = data[data['Entry_Signal'] != 0]
    trend_changes = [
        {
            "date": pd.to_datetime(signal.Index).strftime('%Y-%m-%d'),  # Corrected part
            "price": signal.Close,
            "direction": "upward" if signal.Entry_Signal > 0 else "downward"
        } 
        for signal in signals.itertuples()
    ]

    # Sort the trend changes by date in descending order
    trend_changes.sort(key=lambda x: x['date'], reverse=True)
    
    return trend_changes
@app.get("/")
def hello_world():
    return {'message': 'Hello from FastAPI'}


@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f'Hello from FastAPI, {name}!'}

@app.get("/trend-change")
def trend_change(symbol: str = Query(None, description="Stock symbol to check the trend for"), months: int = Query(3, description="Months ago")):
    if symbol is None:
        return {"error": "Symbol query parameter is required"}
    
    try:
        trend_info = get_trend_change(symbol, months)
        return trend_info
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/spx-trend")
def spx_trend():
    tickers = get_sp500_tickers()
    market_caps = get_market_caps(tickers)
    top_n_tickers = sorted(market_caps, key=market_caps.get, reverse=True)[:100]

    results = {}
    for ticker in top_n_tickers:
        try:
            vol = get_volatility_percent(ticker)
            if (vol > 2.2):
                trend_change_detected = get_trend_change(ticker, 24)
                results[ticker] = {"signals": trend_change_detected, "vol": vol}
            
        except:
            print('no info for ' + ticker)
    return results

handler = Mangum(app)