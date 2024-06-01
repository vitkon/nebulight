import yfinance as yf
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from scipy.stats import rankdata
import os

load_dotenv()

# Your Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Function to fetch S&P 500 tickers


def get_sp500_tickers():
    table = pd.read_html(
        'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500_tickers = table[0]['Symbol'].tolist()
    return sp500_tickers


def convert_market_cap(value):
    """
    Convert a numerical value into a readable string with suffix (K, M, B, T).

    :param value: Numerical value to convert.
    :return: String representation with appropriate suffix.
    """
    if value is None:
        return "N/A"
    elif value < 1e3:
        return f"{value:.0f}"
    elif value < 1e6:
        return f"{value / 1e3:.1f}K"
    elif value < 1e9:
        return f"{value / 1e6:.1f}M"
    elif value < 1e12:
        return f"{value / 1e9:.1f}B"
    else:
        return f"{value / 1e12:.1f}T"


def get_market_caps(tickers):
    market_caps = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        market_cap = stock.info.get('marketCap')
        print('Fetched marketCap for ' + ticker +
              ' - ' + convert_market_cap(market_cap))
        if market_cap:
            market_caps[ticker] = market_cap
    return market_caps


def calculate_price_momentum(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    spy = yf.Ticker("SPY")
    spy_hist = spy.history(period="1y")

    if len(hist) < 132 or len(spy_hist) < 132:
        return None

    price_strength_1m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-22]) / \
        (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-22])
    price_strength_3m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-66]) / \
        (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-66])
    price_strength_6m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-132]) / \
        (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-132])
    price_strength_12m = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) / \
        (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0])

    ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
    moving_average_ratio = ma_50 / ma_200

    rsi = compute_rsi(hist['Close'])

    high_52week = hist['Close'].max()
    proximity_52week_high = hist['Close'].iloc[-1] / high_52week

    current_volume = hist['Volume'].iloc[-1]
    avg_volume = hist['Volume'].rolling(window=50).mean().iloc[-1]
    volume_trend = current_volume / avg_volume

    return [price_strength_1m, price_strength_3m, price_strength_6m, price_strength_12m, moving_average_ratio, proximity_52week_high, rsi, volume_trend]


def compute_rsi(series, period=14):
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def fetch_earnings_forecast(ticker):
    url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={
        ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'quarterlyEarnings' in data:
        forecast_data = data['quarterlyEarnings']
        forecast_earnings = [float(item['estimatedEPS']) for item in forecast_data if item.get(
            'estimatedEPS') and item['estimatedEPS'] != 'None']
        actual_earnings = [float(item['reportedEPS']) for item in forecast_data if item.get(
            'reportedEPS') and item['reportedEPS'] != 'None']
        return forecast_earnings, actual_earnings
    else:
        return [], []


def calculate_earnings_momentum(ticker):
    forecast_earnings, actual_earnings = fetch_earnings_forecast(ticker)

    if forecast_earnings and actual_earnings:
        earnings_surprise = np.mean([(actual - forecast) / forecast for actual,
                                    forecast in zip(actual_earnings, forecast_earnings) if forecast != 0])
    else:
        earnings_surprise = 0

    stock = yf.Ticker(ticker)
    recommendations = stock.recommendations

    if recommendations is not None and not recommendations.empty:
        latest_recs = recommendations.groupby(recommendations.index).tail(1)
        if 'To Grade' in latest_recs.columns:
            recommendation_change = latest_recs['To Grade'].replace(
                {'Buy': 1, 'Hold': 0, 'Sell': -1}).mean()
        else:
            recommendation_change = 0
    else:
        recommendation_change = 0

    return [earnings_surprise, recommendation_change]


def rank_metrics(metrics):
    return [rankdata(metric, method='ordinal') for metric in metrics]


def calculate_composite_score(price_ranks, earnings_ranks):
    if all(v == 0 for v in earnings_ranks):
        composite_score = np.mean(price_ranks)
    else:
        composite_score = np.mean(price_ranks + earnings_ranks)
    return composite_score


# Fetch S&P 500 tickers
tickers = get_sp500_tickers()
market_caps = get_market_caps(tickers)
top_n_tickers = sorted(market_caps, key=market_caps.get, reverse=True)[:100]

# top_n_tickers = ['QCOM', 'AMD', 'NVDA']

price_metrics = []
earnings_metrics = []

for ticker in top_n_tickers:
    price_data = calculate_price_momentum(ticker)
    if price_data is not None:
        price_metrics.append(price_data)
        earnings_metrics.append(calculate_earnings_momentum(ticker))
    else:
        print(f"Skipping {ticker} due to insufficient data.")

price_metrics = np.array(price_metrics).T
earnings_metrics = np.array(earnings_metrics).T

price_ranks = rank_metrics(price_metrics)
earnings_ranks = rank_metrics(earnings_metrics)

momentum_ranks = {}
for i, ticker in enumerate(top_n_tickers):
    if i < len(price_ranks[0]):  # Ensure index is within bounds
        price_ranks_for_ticker = [price_ranks[j][i]
                                  for j in range(len(price_ranks))]
        earnings_ranks_for_ticker = [earnings_ranks[j][i]
                                     for j in range(len(earnings_ranks))]
        composite_score = calculate_composite_score(
            price_ranks_for_ticker, earnings_ranks_for_ticker)
        momentum_ranks[ticker] = composite_score

momentum_ranks_df = pd.DataFrame.from_dict(
    momentum_ranks, orient='index', columns=['CompositeScore'])

min_rank = momentum_ranks_df['CompositeScore'].min()
max_rank = momentum_ranks_df['CompositeScore'].max()
momentum_ranks_df['NormalizedMomentumRank'] = 100 * \
    (momentum_ranks_df['CompositeScore'] - min_rank) / (max_rank - min_rank)

momentum_ranks_df.sort_values(
    by='NormalizedMomentumRank', ascending=False, inplace=True)

# Display top 20 stocks
top_20_stocks = momentum_ranks_df.head(30)
print(top_20_stocks)
