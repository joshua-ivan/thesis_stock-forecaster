from config import stocks
from utilities import file_io
import requests
import time


def build_query_params(end_timestamp, interval_days):
    start_timestamp = end_timestamp - (interval_days * 24 * 60 * 60)
    return {
        'period1': int(start_timestamp),
        'period2': int(end_timestamp),
        'interval': '1d',
        'events': 'history',
        'includeAdjustedClose': 'true'
    }


def execute():
    headers = {
        'User-agent': 'Mozilla/5.0'
    }
    for stock in stocks:
        ticker = stock['ticker']

        stock_history = requests.get(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}',
                                     headers=headers, params=build_query_params(time.time(), 365))

        file_io.write_file('prices', f'{ticker}.csv', stock_history.text)
