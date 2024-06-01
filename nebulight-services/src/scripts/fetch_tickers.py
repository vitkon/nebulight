from typing import Literal
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from src.database import engine
from src.models import Industry, Sector, Ticker

Session = sessionmaker(bind=engine)
session = Session()


def get_or_create_industry(industry_name):
    industry = session.query(Industry).filter_by(name=industry_name).first()
    if not industry:
        industry = Industry(name=industry_name)
        session.add(industry)
        session.commit()
    return industry.id


def get_or_create_sector(sector_name):
    sector = session.query(Sector).filter_by(name=sector_name).first()
    if not sector:
        sector = Sector(name=sector_name)
        session.add(sector)
        session.commit()
    return sector.id


def scrape_tickers_from_nasdaq():
    url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
    response = requests.get(url)
    lines = response.text.splitlines()
    tickers = []
    for line in lines[1:]:  # Skip header
        parts = line.split('|')
        if len(parts) > 1:
            ticker_symbol = parts[0].strip()
            tickers.append(ticker_symbol)
    return tickers


def scrape_tickers_from_ftse100():
    url = "https://en.wikipedia.org/wiki/FTSE_100_Index"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the FTSE 100 tickers
    table = soup.find("table", {"id": "constituents"})

    # Extract tickers from the table
    tickers = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        ticker = row.find_all("td")[1].text.strip()
        tickers.append(ticker)

    return tickers


def scrape_tickers_from_ftse250():
    url = "https://en.wikipedia.org/wiki/FTSE_250_Index"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the FTSE 100 tickers
    table = soup.find("table", {"id": "constituents"})

    # Extract tickers from the table
    tickers = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        ticker = row.find_all("td")[1].text.strip()
        tickers.append(ticker)

    return tickers


Exchange = Literal['OQ', 'N', 'A', 'P', 'L', 'PA', 'F', 'T', 'HK']


def get_ticker_details(ticker_symbol, exchange: Exchange = None):
    print(ticker_symbol)
    # Format ticker symbol for yfinance with exchange information
    formatted_ticker = f"{ticker_symbol}.{
        exchange}" if exchange != None else ticker_symbol
    ticker = yf.Ticker(formatted_ticker)
    try:
        info = ticker.info
        if 'longName' in info:
            company_name = info.get('longName', 'Unknown')
            industry = info.get('industry', 'Unknown')
            instrument_type = info.get('quoteType', 'Unknown')
            print(company_name)
            print('---')
            return formatted_ticker, company_name, industry, instrument_type
        else:
            return None
    except Exception as e:
        print(f"Error processing ticker {formatted_ticker}: {e}")
        return None


def store_ticker(ticker_symbol, company_name, exchange, industry_name, instrument_type):
    industry_id = get_or_create_industry(industry_name)
    existing = session.query(Ticker).filter_by(
        ticker_symbol=ticker_symbol, exchange=exchange).first()
    if not existing:
        new_ticker = Ticker(
            ticker_symbol=ticker_symbol,
            company_name=company_name,
            exchange=exchange,
            type=instrument_type,
            industry_id=industry_id
        )
        session.add(new_ticker)
        session.commit()

# Main logic
# exchange_name = "NASDAQ"
# tickers = scrape_tickers_from_nasdaq()


# Scrape tickers of FTSE 100 companies from the Wikipedia page
exchange_name = "LSE"
exchange_suffix = "L"
tickers = scrape_tickers_from_ftse250()

for ticker_symbol in tickers:
    print(ticker_symbol)
    if len(ticker_symbol) > 10:
        break
    existing = session.query(Ticker).filter_by(
        ticker_symbol=ticker_symbol, exchange=exchange_name).first()
    if not existing:
        details = get_ticker_details(ticker_symbol, exchange_suffix)
        print(details)
        if details:
            formatted_ticker, company_name, industry_name, instrument_type = details
            print(f"Found: {
                  formatted_ticker} - {company_name} - {industry_name} - {instrument_type}")
            store_ticker(ticker_symbol, company_name,
                         exchange_name, industry_name, instrument_type)
        else:
            print(f"Skipping ticker {ticker_symbol} due to error.")

# https://community.developers.refinitiv.com/questions/92114/how-to-find-the-list-with-the-exchange-for-which-t.html
