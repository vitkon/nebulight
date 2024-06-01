import yfinance as yf
from sqlalchemy.orm import sessionmaker
from src.database import engine
from src.models import Sector, Ticker

Session = sessionmaker(bind=engine)
session = Session()


def get_or_create_sector(sector_name):
    # Check if the sector already exists in the database
    sector = session.query(Sector).filter_by(name=sector_name).first()

    if not sector:
        # If the sector doesn't exist, create a new one
        sector = Sector(name=sector_name)
        session.add(sector)
        session.commit()

    # Return the sector id
    return sector.id


# Fetch tickers from the database
tickers = session.query(Ticker).all()

for ticker in tickers:
    try:
        # Fetch sector information for the ticker from Yahoo Finance
        print(ticker.ticker_symbol)
        formatted_ticker = f"{
            ticker.ticker_symbol}.L" if ticker.exchange == 'LSE' else ticker.ticker_symbol
        info = yf.Ticker(formatted_ticker).info
        sector_name = info.get('sector', 'Unknown')

        # Get or create the sector in the database
        sector_id = get_or_create_sector(sector_name)

        # Update the ticker's sector_id field
        ticker.sector_id = sector_id

        # Commit changes to the database
        session.commit()

        print(f"Ticker: {ticker.ticker_symbol}, Sector: {sector_name}")
    except Exception as e:
        print(f"Error processing ticker {ticker.symbol}: {e}")

# Close the session when done
session.close()
