import yfinance as yf


def get_ticker_details(ticker_symbol, exchange=None):
    print(ticker_symbol)
    # Format ticker symbol for yfinance with exchange information
    formatted_ticker = f"{ticker_symbol}.{
        exchange}" if exchange != None else ticker_symbol
    ticker = yf.Ticker(formatted_ticker)
    print(ticker.info)
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


res = get_ticker_details('ABNB')
