from config import stocks
import requests
import os
import time


def write_stock_history(directory, filename, content):
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(f'{directory}/{filename}', 'w', encoding='utf-8') as file:
            file.write(content)
            file.close()
    except OSError as error:
        print(error)


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
                                     headers=headers, params=build_query_params(time.time(), 7))

        write_stock_history('prices', f'{ticker}.csv', stock_history.text)
