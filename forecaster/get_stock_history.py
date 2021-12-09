from forecaster.tickers import tickers
import requests
import os


def write_stock_history(directory, filename, content):
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(f'{directory}/{filename}', 'w', encoding='utf-8') as file:
            file.write(content)
            file.close()
    except OSError as error:
        print(error)


def execute():
    headers = {
        'User-agent': 'Mozilla/5.0'
    }
    query_params = {
        'period1': '1598825722',
        'period2': '1630361722',
        'interval': '1d',
        'events': 'history',
        'includeAdjustedClose': 'true'
    }
    for ticker in tickers:
        stock_history = requests.get(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}',
                                     headers=headers, params=query_params)

        write_stock_history('prices', f'{ticker}.csv', stock_history.text)
