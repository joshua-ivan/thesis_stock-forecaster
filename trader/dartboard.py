import yfinance
import pandas
import random
import os
from datetime import datetime, timezone, timedelta


default_stock_dir = 'intermediate_data/prices'
default_ticker_csv = 'intermediate_data/tickers.csv'


class Position:
    def __init__(self, ticker, leverage_type, quantity, price, date_time):
        self.ticker = ticker
        self.leverage_type = leverage_type
        self.price = price
        self.quantity = quantity
        self.date_time = date_time

    def __eq__(self, other):
        return self.ticker == other.ticker and\
            self.leverage_type == other.leverage_type and\
            self.price == other.price and\
            self.quantity == other.quantity and\
            self.date_time == other.date_time

    def __str__(self):
        return f'Position: {self.ticker} {self.leverage_type} - {self.quantity} @ {self.price} on {self.date_time}'


class DartboardInvestor:
    def __init__(self, start_date, end_date, tickers=pandas.read_csv(default_ticker_csv),
                 stock_dir=default_stock_dir, yf=yfinance, pd=pandas, rng=random, op_sys=os):
        self.open_positions = []
        self.portfolio_value = 0.0
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = tickers
        self.stock_dir = stock_dir
        self.yfinance = yf
        self.pandas = pd
        self.rng = rng
        self.os = op_sys

    def check_open_positions(self, closing_datetime):
        for i in range(len(self.open_positions) - 1, -1, -1):
            if self.rng.randint(0, 99) < 50:
                self.close_position(i, closing_datetime)

    def close_position(self, index, closing_datetime):
        position = self.open_positions[index]
        opening_value = position.price * position.quantity
        current_price = self.get_price(position.ticker, closing_datetime)
        closing_value = current_price * position.quantity

        if position.leverage_type == 'SHORT':
            self.portfolio_value += (opening_value - closing_value)
        elif position.leverage_type == 'LONG':
            self.portfolio_value += (closing_value - opening_value)

        position = self.open_positions.pop(index)
        print(f'Closed position: {position}\nPortfolio value: {self.portfolio_value}')

    def get_price(self, ticker, time):
        file = f'{self.stock_dir}/{ticker}.csv'
        if not self.os.path.exists(file):
            self.get_stock_history(ticker)
        stock_prices = self.pandas.read_csv(file)
        if 'Datetime' not in stock_prices.columns:
            return -1
        price = stock_prices.loc[stock_prices['Datetime'] == time]
        if len(price) > 0:
            return price['Close'].values[0]
        else:
            return -1

    def get_stock_history(self, ticker):
        history = self.yfinance.Ticker(ticker).history(
            start=self.start_date, end=self.end_date, period='1d', interval='1m')
        history.to_csv(f'{self.stock_dir}/{ticker}.csv')

    def new_open_position(self, date_time):
        stock, price = '', -1
        while price < 0:
            stock = self.tickers.iloc[self.rng.randint(0, len(self.tickers) - 1)]['Symbol'].replace('$', '')
            price = self.get_price(stock, date_time)

        min_cash_to_spend = 10000.00
        shares = int(min_cash_to_spend / price) + (min_cash_to_spend % price > 0)
        leverage_type = 'SHORT' if self.rng.randint(0, 99) < 50 else 'LONG'
        position = Position(stock, leverage_type, shares, price, date_time)
        self.open_positions.append(position)
        print(f'New position: {position}')

    def run_simulation(self):
        start_datetime = datetime.strptime(self.start_date, '%Y-%m-%d')
        start_datetime = start_datetime.replace(hour=9, minute=30, second=0, tzinfo=timezone(-timedelta(hours=4)))
        end_datetime = datetime.strptime(self.end_date, '%Y-%m-%d')
        end_datetime = end_datetime.replace(
            day=(end_datetime.day - 1), hour=16, minute=0, second=0, tzinfo=timezone(-timedelta(hours=4)))

        current_datetime = start_datetime
        while current_datetime < end_datetime:
            current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S-04:00')
            self.check_open_positions(current_datetime_str)
            self.new_open_position(current_datetime_str)
            current_datetime = current_datetime + timedelta(minutes=1)
