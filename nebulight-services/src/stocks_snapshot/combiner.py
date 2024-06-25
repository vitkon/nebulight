import boto3
import pandas as pd
from io import BytesIO
import os
from datetime import datetime as dt
from src.metrics.metrics_momentum import momentum_metrics_keys
from tempfile import NamedTemporaryFile

def handler(event, context):
    print(1)
    s3_bucket = os.getenv('S3_DATA_BUCKET')
    s3_client = boto3.client('s3')
    
    print(event)
    
    response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix='intermediate_results/')
    files = [item['Key'] for item in response.get('Contents', [])]
    print(files)
    
    combined_data = []
    final_date: str
    
    for file_key in files:
        obj = s3_client.get_object(Bucket=s3_bucket, Key=file_key)
        df = pd.read_parquet(BytesIO(obj['Body'].read()))
        combined_data.append(df)
        final_date = df.index[0]
        print(final_date)
    
    if not combined_data:
        print("No data to combine.")
        return
    
    print(final_date)
    combined_df = pd.concat(combined_data)
    
    for metric in momentum_metrics_keys:
        if metric in combined_df.columns:
            combined_df[f'{metric}_rank'] = combined_df[metric].rank(ascending=False)
            combined_df[f'{metric}_percentile'] = combined_df[metric].rank(pct=True) * 100

    market = event.get('market', 'US')
    print(event.get('date'))
    final_date = dt.fromisoformat(event.get('date'))
    
    combined_df.reset_index(drop=True, inplace=True)
    
    combined_df['Date'] = final_date
    
    final_file_key = f"market-data/market={market}/year={final_date.year}/month={final_date.month}/day={final_date.day}/data.parquet"
    
    with NamedTemporaryFile(delete=False) as temp_file:
        combined_df.to_parquet(temp_file.name)
        s3_client.upload_file(temp_file.name, s3_bucket, final_file_key)
        os.remove(temp_file.name)   
    
    # Clean up intermediate files
    for file_key in files:
        s3_client.delete_object(Bucket=s3_bucket, Key=file_key)

