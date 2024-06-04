from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from tempfile import NamedTemporaryFile
import boto3
import pandas as pd
import fastparquet as fp
from io import BytesIO
import yfinance as yf
from .models import Industry
from .database import engine

def add_file(event=None, context=None):
    s3_bucket = os.getenv('S3_DATA_BUCKET')
    s3_client = boto3.client('s3')

    ticker_symbol1 = 'AAPL' 
    ticker1 = yf.Ticker(ticker_symbol1)
    df1 = ticker1.history(period='1d')
    
    ticker_symbol2 = 'MSFT' 
    ticker2 = yf.Ticker(ticker_symbol2)
    df2 = ticker2.history(period='1d')
    
    combined_data = pd.concat([df1, df2])
    
    file_name = f"stock-data-metrics-{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"

    # Convert the DataFrame to Parquet format and save it to a temporary file
    with NamedTemporaryFile(delete=False) as temp_file:
        combined_data.to_parquet(temp_file.name)
        temp_file_path = temp_file.name

    # Upload the Parquet file to S3
    try:
        with open(temp_file_path, 'rb') as file_data:
            s3_client.put_object(Bucket=s3_bucket, Key=file_name, Body=file_data)
        print(f"File '{file_name}' uploaded successfully to bucket '{s3_bucket}'")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
    finally:
        os.remove(temp_file_path)  # Clean up the temporary file
def scheduled_task_handler(event, context):
    print('launch scheduled task')
    try:
        print('scheduled task launched')
        # timestamp = datetime.utcnow()
        # add_industry("test " + str(timestamp))
        # add_file2()
    except Exception as e:
        print(f"Error in scheduled task: {e}")