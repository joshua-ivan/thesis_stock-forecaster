import yfinance
import pandas
import os


default_stock_dir = 'intermediate_data/prices'


class PriceFetcher:
    def __init__(self, stock_dir=default_stock_dir, yf=yfinance, pd=pandas, op_sys=os):
        self.stock_dir = stock_dir
        self.yfinance = yf
        self.pandas = pd
        self.os = op_sys

    def get_price(self, ticker, time, start_date, end_date):
        file = f'{self.stock_dir}/{ticker}.csv'
        if not self.os.path.exists(file):
            self.get_stock_history(ticker, start_date, end_date)
        stock_prices = self.pandas.read_csv(file)
        if 'Datetime' not in stock_prices.columns:
            return -1
        price = stock_prices.loc[stock_prices['Datetime'] == time]
        if len(price) > 0:
            return price['Close'].values[0]
        else:
            return -1

    def get_stock_history(self, ticker, start_date, end_date):
        history = self.yfinance.Ticker(ticker).history( start=start_date, end=end_date, period='1d', interval='1m')
        history.to_csv(f'{self.stock_dir}/{ticker}.csv')
