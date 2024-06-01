from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import os

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
router = APIRouter()


class SymbolSearchResponse(BaseModel):
    ticker: str
    name: str
    exchange: str
    type: str


def fetch_symbols():
    url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={
        ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    response.raise_for_status()
    # Parse the CSV response
    lines = response.text.splitlines()
    symbols = []
    for line in lines[1:]:  # Skip header
        fields = line.split(',')
        symbols.append({
            "ticker": fields[0],
            "name": fields[1],
            "exchange": fields[2],
            "type": fields[3],
        })
    return symbols


@router.get("/search-symbols/", response_model=List[SymbolSearchResponse])
async def search_symbols(query: str):
    try:
        symbols = fetch_symbols()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching symbols data")

    matching_symbols = [symbol for symbol in symbols if query.lower(
    ) in symbol["ticker"].lower() or query.lower() in symbol["name"].lower()]

    if not matching_symbols:
        raise HTTPException(
            status_code=404, detail="No matching symbols found")

    return matching_symbols
