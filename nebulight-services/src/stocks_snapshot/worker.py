import os
import json
import time
import boto3
import pandas as pd
import yfinance as yf
from tempfile import NamedTemporaryFile
from src.metrics.metrics_momentum import calculate_momentum_metrics
from src.metrics.metrics_financial_summary import calculate_financial_summary_metrics

def fetch_stock_data(ticker_symbol, market = 'US'):
    ticker_symbol_formatted = ticker_symbol if market == 'US' else f'{ticker_symbol}.L'
    try:
        ticker = yf.Ticker(ticker_symbol_formatted)
        df = ticker.history(period='1d')
        if df.empty:
            return None
        df['symbol'] = ticker_symbol
        momentum_metrics = calculate_momentum_metrics(stock_ticker=ticker_symbol)
        momentum_metrics_df = pd.DataFrame(momentum_metrics, index=df.index)
        time.sleep(0.5)
        financial_summary_metrics = calculate_financial_summary_metrics(stock_ticker=ticker_symbol_formatted)
        financial_summary_df = pd.DataFrame(financial_summary_metrics, index=df.index)
    
        df = pd.concat([df, momentum_metrics_df, financial_summary_df], axis=1)

        return df
    except Exception as e:
        print(f"Failed to download data for {ticker_symbol}: {e}")
        return None

def handler(event, context):
    s3_bucket = os.getenv('S3_DATA_BUCKET')
    s3_client = boto3.client('s3')
    tickers = event.get('tickers')
    market = event.get('market', 'US')
    
    combined_data = []
    
    index = 0
    
    for ticker in tickers:
        index = index + 1
        print(f">>> Symbol {ticker}: {index} out of {len(tickers)}")
        data = fetch_stock_data(ticker, market)
        if data is not None:
            combined_data.append(data)
        time.sleep(0.5)  # Rate limit compliance
    
    if not combined_data:
        return
    
    combined_df = pd.concat(combined_data)
    current_timestamp_ms = str(time.time())
    file_key = f"intermediate_results/batch_{current_timestamp_ms}.parquet"
    
    with NamedTemporaryFile(delete=False) as temp_file:
        combined_df.to_parquet(temp_file.name)
        s3_client.upload_file(temp_file.name, s3_bucket, file_key)
        os.remove(temp_file.name)
        
    return {
        'market': market,
        'date': combined_df.index[0].isoformat()
    }

