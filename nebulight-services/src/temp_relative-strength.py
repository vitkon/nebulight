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
        results[f'{period}m'] = relative_strength

    return results


def calculate_volume_ratio(stock_ticker):
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
    volume_ratio = ((avg_volume_10d - avg_volume_3m) / avg_volume_3m) * 100

    return volume_ratio


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


# Define the ticker symbols and periods
stock_ticker = 'GOOGL'
index_ticker = '^GSPC'
periods = [1, 3, 6, 12]

# Calculate the relative strength
relative_strength_results = calculate_relative_strength(
    stock_ticker, index_ticker, periods)
volume_ratio = calculate_volume_ratio(stock_ticker)
price_52w_high = calculate_price_vs_52_week_high(stock_ticker)
price_50d_ma = calculate_price_vs_50_day_ma(stock_ticker)
price_200d_ma = calculate_price_vs_200_day_ma(stock_ticker)

print(relative_strength_results)
print('--- Volume 10d/3m')
print(volume_ratio)
print('--- 52w High')
print(price_52w_high)
print('--- 50d MA')
print(price_50d_ma)
print('--- 200d MA')
print(price_200d_ma)

# relative strength traffic
# 1m -11% r, -8% o, -5% o, -2% y, -1% y, 3.3% lg, $.39% lg,  8% g
# 3m -25% r, -21% o, -17% o, -4% y, 1% lg, 17%+ g
# 6m  -13% o, -11% y, -5.7% y, -2.5% lg, 8% lg, 13%+ g
# 1y -14% y, -10% lg, -4.8% lg, 20%+ g
#

# volume_ratio traffic
# -10%, -18%, -21% - y
# 6% lg
# -33% o, -27% o
# -47% r
#

#  prices vs %
# 52w -26% y, 22% y, -8% lg, -8% lg, -5% g, -3% g, -1% g
# 50d, -11% r, -5% o, 5% lg, 0% y, 9% g 12% g
# 200d, -4% o, 4.6% y, 8% lg, 16% lg, 20%+ g
#
#
