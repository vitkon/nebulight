import os
import json
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import text
from .utils import nanoseconds_to_iso

# Athena configuration
ATHENA_DATABASE = os.getenv('ATHENA_DATABASE')
ATHENA_OUTPUT_LOCATION = os.getenv('ATHENA_OUTPUT_LOCATION')
ATHENA_REGION = os.getenv('ATHENA_REGION')

router = APIRouter()

# # Create SQLAlchemy engine
# engine = create_engine(
#     f'awsathena+rest://:@athena.{ATHENA_REGION}.amazonaws.com:443/{ATHENA_DATABASE}?s3_staging_dir={ATHENA_OUTPUT_LOCATION}'
# )

# def format_response(result):
#     market_data = [
#         "high",
#         "low",
#         "open",
#         "close",
#         "dividends",
#         "volume",
#         "stock splits"
#     ]
    
#     momentum_metrics = [
#         "relative_strength_1m",
#         "relative_strength_3m",
#         "relative_strength_6m",
#         "relative_strength_12m",
#         "volume_ratio_10d_3m",
#         "volume_ratio_1d_2d"
#         "price_52w_high",
#         "price_50d_ma",
#         "price_200d_ma"
#     ]
    
#     rank_suffix = "_rank"
#     percentile_suffix = "_percentile"
    
#     response = {
#         "symbol": result["symbol"],
#         "market_data": {},
#         "momentum_metrics": {},
#         "date": nanoseconds_to_iso(result["date"]),
#     }
    
#     for metric in market_data:
#         response["market_data"][metric] = round(result[metric], 2)
    
#     for metric in momentum_metrics:
#         metric_value = result.get(metric)
#         metric_percentile = result.get(metric + percentile_suffix)
#         metric_rank = result.get(metric + rank_suffix)
        
#         if metric_value is not None and metric_percentile is not None and metric_rank is not None:
#             response["momentum_metrics"][metric] = {
#                 "value": round(result[metric], 2),
#                 "market": {
#                     "percentile": round(result[metric + percentile_suffix], 2),
#                     "rank": result[metric + rank_suffix]
#                 }
#             }
    
#     return response

# router = APIRouter()

# @router.get('/stock/{symbol}')
# def get_stock_report(symbol):
#     query = text("""
#         SELECT * FROM nebulight_data
#         WHERE symbol = :symbol
#         ORDER BY date DESC
#         LIMIT 1
#     """)
#     with engine.connect() as conn:
#         result = conn.execute(query, {'symbol': symbol}).fetchone()
    
#     if result:
#         result_dict = result._asdict()
#         return format_response(result_dict)
#     else:
#         return {'error': 'Stock symbol not found'}, 404
