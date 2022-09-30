from trader.price_fetcher import PriceFetcher
from trader.position import Position
from utilities.file_io import write_file
from datetime import datetime, timezone, timedelta
import pandas
import random


default_ticker_csv = '../forecaster_data/tickers.csv'


class DartboardInvestor:
    def __init__(self, start_date, end_date, tickers=pandas.read_csv(default_ticker_csv),
                 rng=random, pf=PriceFetcher()):
        self.open_positions = []
        self.portfolio_value = 0.0
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = tickers
        self.rng = rng
        self.price_fetcher = pf
        self.log = []

    def check_open_positions(self, closing_datetime):
        for i in range(len(self.open_positions) - 1, -1, -1):
            if self.rng.randint(0, 99) < 50:
                self.close_position(i, closing_datetime)

    def close_position(self, index, closing_datetime):
        position = self.open_positions[index]
        opening_value = position.price * position.quantity
        current_price = self.price_fetcher.get_price(position.ticker, closing_datetime, self.start_date, self.end_date)
        closing_value = current_price * position.quantity

        if position.leverage_type == 'SHORT':
            self.portfolio_value += (opening_value - closing_value)
        elif position.leverage_type == 'LONG':
            self.portfolio_value += (closing_value - opening_value)

        position = self.open_positions.pop(index)

        log_str = f'Closed position: {position}\nPortfolio value: {self.portfolio_value}'
        self.log.append(log_str)
        print(log_str)

    def new_open_position(self, date_time):
        stock, price = '', -1
        while price < 0:
            stock = self.tickers.iloc[self.rng.randint(0, len(self.tickers) - 1)]['Symbol'].replace('$', '')
            price = self.price_fetcher.get_price(stock, date_time, self.start_date, self.end_date)

        min_cash_to_spend = 10000.00
        shares = int(min_cash_to_spend / price) + (min_cash_to_spend % price > 0)
        leverage_type = 'SHORT' if self.rng.randint(0, 99) < 50 else 'LONG'
        position = Position(stock, leverage_type, shares, price, date_time)
        self.open_positions.append(position)

        log_str = f'New position: {position}'
        self.log.append(log_str)
        print(log_str)

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

            current_datetime = current_datetime + timedelta(minutes=5)
            if current_datetime.hour >= 16:
                current_datetime = current_datetime + timedelta(hours=17, minutes=30)

        write_file('.', 'dartboard.log', ''.join([(lambda st: f'{st}\n')(st) for st in self.log]))
