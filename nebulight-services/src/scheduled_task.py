from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os
from tempfile import NamedTemporaryFile
import boto3
import pandas as pd
import fastparquet as fp
from io import BytesIO
import yfinance as yf
from .models import Industry, Ticker
from .database import engine
from .metrics.metrics_momentum import calculate_momentum_metrics
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance.utils")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*treating keys as positions is deprecated.*")

# def upload_stock_data_old(ticker_symbols, market, exchange=None):
#     s3_bucket = os.getenv('S3_DATA_BUCKET')
#     s3_client = boto3.client('s3')
    
#     combined_data = []
    
#     print(ticker_symbols)

#     for ticker_symbol in ticker_symbols:
#         try:
#             ticker = yf.Ticker(ticker_symbol)
#             df = ticker.history(period='1d')
            
#             print(df)
            
#             if df.empty:
#                 print(f"No data found for ticker symbol: {ticker_symbol}")
#                 continue

#             df['symbol'] = ticker_symbol

#             # Add momentum metrics to the DataFrame
#             momentum_metrics = calculate_momentum_metrics(stock_ticker=ticker_symbol)
            
#             print(momentum_metrics)
            
#             metrics_df = pd.DataFrame(momentum_metrics, index=df.index)
#             # metrics_df.columns = pd.MultiIndex.from_product([['momentum_metrics'], metrics_df.columns])

#             df = pd.concat([df, metrics_df], axis=1)
#             combined_data.append(df)
#             print(combined_data)
#         except Exception as e:
#             print(f"Failed to download data for {ticker_symbol}: {e}")

#     if not combined_data:
#         print("No data to upload.")
#         return

#     # Combine all data into a single DataFrame
#     combined_df = pd.concat(combined_data)
    
#     # Compute ranks and percentiles for each metric
#     for metric in metrics_df.columns:
#         combined_df[f'{metric}_rank'] = combined_df[metric].rank(ascending=False)
#         combined_df[f'{metric}_percentile'] = combined_df[metric].rank(pct=True)  * 100

#     # Create temporary file to store the data in Parquet format
#     with NamedTemporaryFile(delete=False) as temp_file:
#         temp_file_path = temp_file.name
#         combined_df.to_parquet(temp_file_path)

#     # Upload the Parquet file to S3 with partitioned directory structure
#     try:
#         for _, row in combined_df.iterrows():
#             file_name = f"market-data/market={market}/year={combined_df.index.year[0]}/month={combined_df.index.month[0]}/day={combined_df.index.day[0]}/data.parquet"

#             with open(temp_file_path, 'rb') as file_data:
#                 s3_client.put_object(Bucket=s3_bucket, Key=file_name, Body=file_data)

#         print(f"File uploaded successfully to bucket '{s3_bucket}' with partitioned structure.")
#     except Exception as e:
#         print(f"Error uploading file to S3: {e}")
#     finally:
#         os.remove(temp_file_path)  # Clean up the temporary file

def fetch_stock_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period='1d')

        if df.empty:
            print(f"No data found for ticker symbol: {ticker_symbol}")
            return None

        df['symbol'] = ticker_symbol

        # Add momentum metrics to the DataFrame
        momentum_metrics = calculate_momentum_metrics(stock_ticker=ticker_symbol)
        metrics_df = pd.DataFrame(momentum_metrics, index=df.index)

        df = pd.concat([df, metrics_df], axis=1)
        return df
    except Exception as e:
        print(f"Failed to download data for {ticker_symbol}: {e}")
        return None

def upload_stock_data(ticker_symbols, market, exchange=None):
    s3_bucket = os.getenv('S3_DATA_BUCKET')
    s3_client = boto3.client('s3')

    combined_data = []

    batch_size = 100  # Adjust batch size as needed
    for i in range(0, len(ticker_symbols), batch_size):
        batch_symbols = ticker_symbols[i:i + batch_size]
        
        for symbol in batch_symbols:
            data = fetch_stock_data(symbol)
            if data is not None:
                combined_data.append(data)
                print(f"Data fetched successfully for symbol: {symbol}")
            time.sleep(0.5)  # Introducing a delay of 1 second between requests

    if not combined_data:
        print("No data to upload.")
        return

    # Combine all data into a single DataFrame
    combined_df = pd.concat(combined_data)

    # Ensure there are metrics to process
    if not combined_df.empty and any(col.startswith('momentum_metrics') for col in combined_df.columns):
        metrics_df = combined_df[[col for col in combined_df.columns if col.startswith('momentum_metrics')]]
        # Compute ranks and percentiles for each metric
        for metric in metrics_df.columns:
            combined_df[f'{metric}_rank'] = combined_df[metric].rank(ascending=False)
            combined_df[f'{metric}_percentile'] = combined_df[metric].rank(pct=True) * 100

    # Create temporary file to store the data in Parquet format
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        combined_df.to_parquet(temp_file_path)

    # Upload the Parquet file to S3 with partitioned directory structure
    try:
        if not combined_df.empty:
            for _, row in combined_df.iterrows():
                file_name = f"market-data/market={market}/year={combined_df.index.year[0]}/month={combined_df.index.month[0]}/day={combined_df.index.day[0]}/data.parquet"

                with open(temp_file_path, 'rb') as file_data:
                    s3_client.put_object(Bucket=s3_bucket, Key=file_name, Body=file_data)

            print(f"File uploaded successfully to bucket '{s3_bucket}' with partitioned structure.")
        else:
            print("No data to upload to S3.")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
    finally:
        os.remove(temp_file_path)  # Clean up the temporary file


        
def fetch_nasdaq_ticker_symbols():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Assuming the Stock model has a 'symbol' column and an 'exchange' column
        ticker_symbols = session.query(Ticker.ticker_symbol).filter(Ticker.exchange == 'NASDAQ').all()
        print(ticker_symbols)
        return [symbol for (symbol,) in ticker_symbols]
    except Exception as e:
        print(f"Error fetching NASDAQ ticker symbols: {e}")
        return []
    finally:
        session.close()



def scheduled_task_handler(event, context):
    try:
        print('scheduled task launched')
        ticker_symbols = fetch_nasdaq_ticker_symbols()
        upload_stock_data(ticker_symbols=ticker_symbols, market='US')
    except Exception as e:
        print(f"Error in scheduled task: {e}")