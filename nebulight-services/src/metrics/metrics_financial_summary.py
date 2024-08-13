import yfinance as yf
import pandas as pd
import numpy as np
import yfinance as yf
from dotenv import load_dotenv
import os
import requests
import json
load_dotenv()

# Your Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

def fetch_stock_price(symbol):
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[0]
    history = stock.history(period="1d")
    if history.empty:
        print(f"No data fetched for {symbol}")
        return None
    try:
        price = history['Close'].iloc[0]
        return price
    except IndexError:
        print(f"Failed to access closing price for {symbol}")
        return None

def fetch_quarterly_earnings(symbol):
    url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'quarterlyEarnings' in data:
            return data['quarterlyEarnings']
        else:
            print(f"No quarterly earnings data found for {symbol}")
            return None
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
    
def calculate_trailing_eps(earnings_data):
    if not earnings_data or len(earnings_data) < 4:
        print("Not enough data to calculate trailing EPS")
        return None
    
    try:
        # Get the EPS values for the last four quarters
        print(earnings_data[0])
        last_four_eps = [float(earnings_data[i]['reportedEPS']) for i in range(4)]
        # Calculate the trailing EPS
        trailing_eps = sum(last_four_eps)
        return trailing_eps
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error calculating trailing EPS: {e}")
        return None

def calculate_pe_ratio_ttm(symbol: str):
    earnings_data = fetch_quarterly_earnings(symbol)
    trailing_eps = calculate_trailing_eps(earnings_data)
    stock_price = fetch_stock_price(symbol)

    if stock_price is None or trailing_eps is None or trailing_eps <= 0:
        print(f"{symbol}: Invalid data for P/E calculation")
        return None
    
    try:
        pe_ratio = stock_price / trailing_eps
        return pe_ratio
    except ZeroDivisionError:
        print(f"{symbol}: Division by zero in P/E calculation")
        return None

def calculate_financial_summary_metrics(stock_ticker):
    financial_summary_metrics = {}   
    financial_summary_metrics['pe_ratio_ttm'] = calculate_pe_ratio_ttm(stock_ticker)
    return financial_summary_metrics

res = calculate_financial_summary_metrics('BZFD')
print(res)