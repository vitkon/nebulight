import yfinance as yf
from datetime import datetime, timedelta


def calculate_relative_strength(stock_ticker, index_ticker, periods):
    end_date = datetime.today().strftime('%Y-%m-%d')

    stock_data = yf.download(stock_ticker, end=end_date)
    index_data = yf.download(index_ticker, end=end_date)

    results = {}
    for period in periods:
        if period == 1:
            start_date = (datetime.today() - timedelta(days=30)
                          ).strftime('%Y-%m-%d')
        elif period == 3:
            start_date = (datetime.today() - timedelta(days=90)
                          ).strftime('%Y-%m-%d')
        elif period == 6:
            start_date = (datetime.today() - timedelta(days=180)
                          ).strftime('%Y-%m-%d')
        elif period == 12:
            start_date = (datetime.today() - timedelta(days=365)
                          ).strftime('%Y-%m-%d')

        # Fetching the exact start prices
        stock_start_price = stock_data.loc[stock_data.index >=
                                           start_date].iloc[0]['Adj Close']
        stock_end_price = stock_data.iloc[-1]['Adj Close']

        index_start_price = index_data.loc[index_data.index >=
                                           start_date].iloc[0]['Adj Close']
        index_end_price = index_data.iloc[-1]['Adj Close']

        stock_change = stock_end_price / stock_start_price
        index_change = index_end_price / index_start_price

        relative_strength = 100 * (stock_change / index_change - 1)
        results[f'relative_strength_{period}m'] = relative_strength

    return results


def calculate_volume_ratio_10d_3m(stock_ticker):
    end_date = datetime.today()
    start_date_3m = end_date - timedelta(days=90)  # Approximate 3 months

    # Fetch stock data
    stock_data = yf.download(stock_ticker, start=start_date_3m.strftime(
        '%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    # Calculate average volume over the last 10 trading days
    avg_volume_10d = stock_data['Volume'][-10:].mean()

    # Calculate average volume over the last 3 months
    avg_volume_3m = stock_data['Volume'].mean()

    # Calculate the volume ratio as a percentage
    volume_ratio_10d_3m = ((avg_volume_10d - avg_volume_3m) / avg_volume_3m) * 100

    return volume_ratio_10d_3m


def calculate_volume_ratio_1d_2d(stock_ticker):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=10)  # Fetch last 10 days to ensure we have at least 2 trading days

    stock_data = yf.download(stock_ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    # Ensure we have enough data
    if len(stock_data) < 2:
        raise ValueError("Not enough data to calculate volume surge")
    
    current_volume = stock_data['Volume'][-1]
    previous_day_volume = stock_data['Volume'][-2]
    volume_ratio_1d_2d = ((current_volume - previous_day_volume) / previous_day_volume) * 100

    return volume_ratio_1d_2d

def calculate_price_vs_52_week_high(stock_ticker):
    end_date = datetime.today()
    start_date_52w = end_date - timedelta(days=365)  # 52 weeks approximately

    # Fetch stock data
    stock_data = yf.download(stock_ticker, start=start_date_52w.strftime(
        '%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    # Calculate the 52 week high
    high_52w = stock_data['High'].max()

    # Get the current price (most recent closing price)
    current_price = stock_data['Close'][-1]

    # Calculate the Price vs. 52 Week High indicator
    price_vs_52w_high = (current_price - high_52w) / high_52w * 100

    return price_vs_52w_high


def calculate_price_vs_50_day_ma(stock_ticker):
    end_date = datetime.today()
    # Fetch 100 days of data to cover at least 50 trading days
    start_date_100d = end_date - timedelta(days=100)

    # Fetch stock data
    stock_data = yf.download(stock_ticker, start=start_date_100d.strftime(
        '%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    # Ensure we have enough data points
    if len(stock_data) < 50:
        raise ValueError(
            "Not enough data to calculate the 50-day moving average")

    # Calculate the 50 day moving average
    stock_data['50d_MA'] = stock_data['Close'].rolling(window=50).mean()

    # Get the most recent data point with a valid 50-day moving average
    latest_data = stock_data.dropna(subset=['50d_MA']).iloc[-1]

    # Get the current price (most recent closing price)
    current_price = latest_data['Close']

    # Get the 50-day moving average
    ma_50d = latest_data['50d_MA']

    # Calculate the Price vs. 50 Day MA indicator
    price_vs_50d_ma = (current_price - ma_50d) / ma_50d * 100

    return price_vs_50d_ma


def calculate_price_vs_200_day_ma(stock_ticker):
    end_date = datetime.today()
    # Fetch 300 days of data to cover at least 200 trading days
    start_date_300d = end_date - timedelta(days=300)

    # Fetch stock data
    stock_data = yf.download(stock_ticker, start=start_date_300d.strftime(
        '%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    # Ensure we have enough data points
    if len(stock_data) < 200:
        raise ValueError(
            "Not enough data to calculate the 200-day moving average")

    # Calculate the 200 day moving average
    stock_data['200d_MA'] = stock_data['Close'].rolling(window=200).mean()

    # Get the most recent data point with a valid 200-day moving average
    latest_data = stock_data.dropna(subset=['200d_MA']).iloc[-1]

    # Get the current price (most recent closing price)
    current_price = latest_data['Close']

    # Get the 200-day moving average
    ma_200d = latest_data['200d_MA']

    # Calculate the Price vs. 200 Day MA indicator
    price_vs_200d_ma = (current_price - ma_200d) / ma_200d * 100

    return price_vs_200d_ma

def calculate_momentum_metrics(stock_ticker, exchange = 'Nasdaq'):
    index_ticker = '^GSPC' if exchange == 'Nasdaq' else 'ASX'
    momentum_metrics = {}
    
    periods = [1, 3, 6, 12]
    relative_strength_results = calculate_relative_strength(
        stock_ticker, index_ticker, periods)
    
    momentum_metrics.update(relative_strength_results)
    momentum_metrics['volume_ratio_10d_3m'] = calculate_volume_ratio_10d_3m(stock_ticker)
    momentum_metrics['volume_ratio_1d_2d'] = calculate_volume_ratio_1d_2d(stock_ticker)
    momentum_metrics['price_52w_high'] = calculate_price_vs_52_week_high(stock_ticker)
    momentum_metrics['price_50d_ma'] = calculate_price_vs_50_day_ma(stock_ticker)
    momentum_metrics['price_200d_ma'] = calculate_price_vs_200_day_ma(stock_ticker)
    
    return momentum_metrics

momentum_metrics_keys = [
    "relative_strength_1m",
    "relative_strength_3m",
    "relative_strength_6m",
    "relative_strength_12m",
    "volume_ratio_10d_3m",
    "volume_ratio_1d_2d"
    "price_52w_high",
    "price_50d_ma",
    "price_200d_ma"
]