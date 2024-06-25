import json
import os
import boto3
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.models import Ticker

engine = create_engine(DATABASE_URL)

def fetch_nasdaq_ticker_symbols(market='US'):
    Session = sessionmaker(bind=engine)
    session = Session()
    print("fetch symbols")
    exchange = 'NASDAQ' if market == 'US' else 'LSE'
    try:
        # Assuming the Stock model has a 'symbol' column and an 'exchange' column
        ticker_symbols = session.query(Ticker.ticker_symbol).filter(Ticker.exchange == exchange).all()
        print(ticker_symbols)
        return [symbol for (symbol,) in ticker_symbols]
    except Exception as e:
        print(f"Error fetching NASDAQ ticker symbols: {e}")
        return []
    finally:
        session.close()


def split_list(lst, n):
    """Splits a list into n-sized chunks."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def handler(event, context):
    step_functions_client = boto3.client('stepfunctions')
    state_machine_arn = os.getenv('STATE_MACHINE_ARN')
    
    if not state_machine_arn:
        raise ValueError("State machine ARN is not set")
    
    print(f"Using state machine ARN: {state_machine_arn}")
    market = event.get('market', 'US')

    
    # Fetch ticker symbols from your database
    ticker_symbols = fetch_nasdaq_ticker_symbols(market)
    batch_size = 500
    # Split the list into smaller batches
    batches = list(split_list(ticker_symbols, batch_size))
    
    return {
        'statusCode': 200,
        'body': {
            'tickers': batches,
            'market': market
        }
    }