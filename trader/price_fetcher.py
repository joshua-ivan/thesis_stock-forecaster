from datetime import datetime, timedelta
import yfinance
import pandas
import os


default_stock_dir = '../forecaster_data/prices'


class PriceFetcher:
    def __init__(self, stock_dir=default_stock_dir, yf=yfinance, pd=pandas, op_sys=os):
        self.stock_dir = stock_dir
        self.yfinance = yf
        self.pandas = pd
        self.os = op_sys

    def get_price(self, ticker, time, start_date, end_date):
        stock_history = self.get_stock_history(ticker, start_date, end_date)
        if stock_history.index.name != 'Datetime':
            return -1
        if len(stock_history) <= 0:
            return -1

        timestamp = time
        price = -1
        while price <= 0:
            try:
                index = list(stock_history.index.astype('string')).index(timestamp)
                price = stock_history.iloc[index]['Close']
            except ValueError:
                datetime_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S-04:00')
                datetime_obj -= timedelta(minutes=1)
                if datetime_obj.hour <= 9 and datetime_obj.minute < 30:
                    datetime_obj -= timedelta(hours=17, minutes=30)
                timestamp = datetime_obj.strftime('%Y-%m-%d %H:%M:%S-04:00')
                price = -1
        return price

    def get_stock_history(self, ticker, start_date, end_date):
        history = self.yfinance.Ticker(ticker).history(start=start_date, end=end_date, period='1d', interval='1m')
        file = f'{self.stock_dir}/{ticker}.csv'
        if self.os.path.exists(file):
            cached = self.pandas.read_csv(file, index_col=0, parse_dates=True)
            history = self.merge_stock_data(history, cached)
        history.index.name = 'Datetime'
        history.to_csv(file)
        return history

    def merge_stock_data(self, new_data, old_data):
        diff_data = self.pandas.concat([old_data, new_data])
        diff_data = diff_data[~diff_data.index.duplicated(keep='last')]
        return diff_data.sort_index()
