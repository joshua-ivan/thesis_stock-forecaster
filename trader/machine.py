from sentiment.analyzer import RedditAnalyzer
from forecaster.lstm_forecaster import LSTMForecaster
from trader.price_fetcher import PriceFetcher
from trader.position import Position
from utilities.date_util import datetime_string_to_posix, datetime_string_to_yfinance_dates
from datetime import datetime


class MachineInvestor:
    def __init__(self, start_date, end_date, pf=PriceFetcher(), ra=RedditAnalyzer(), lstm_fc=LSTMForecaster()):
        self.open_positions = []
        self.portfolio_value = 0.0
        self.loss_threshold = 0.01
        self.start_date = start_date
        self.end_date = end_date
        self.price_fetcher = pf
        self.reddit_analyzer = ra
        self.lstm_forecaster = lstm_fc

    def check_open_positions(self, closing_datetime):
        for i in range(len(self.open_positions) - 1, -1, -1):
            position = self.open_positions[i]
            current_price = self.price_fetcher.get_price(position.ticker, closing_datetime,
                                                         self.start_date, self.end_date)

            opening_value = position.price * position.quantity
            closing_value = current_price * position.quantity
            raw_profit, profit_percent = 0.0, 0.0
            if position.leverage_type == 'SHORT':
                raw_profit = opening_value - closing_value
                profit_percent = raw_profit / closing_value
            elif position.leverage_type == 'LONG':
                raw_profit = closing_value - opening_value
                profit_percent = raw_profit / opening_value

            if profit_percent > (2 * self.loss_threshold) or profit_percent < (-1 * self.loss_threshold):
                self.close_position(raw_profit, i)

    def close_position(self, raw_profit, index):
        self.portfolio_value += raw_profit
        position = self.open_positions.pop(index)
        print(f'Closed position: {position}\nPortfolio value: {self.portfolio_value}')

    def get_sentiment(self, position_datetime):
        posix_timestamp = datetime_string_to_posix(position_datetime)
        return self.reddit_analyzer.extract_sentiment(int(posix_timestamp - (60 * 60)), int(posix_timestamp))

    def get_price(self, ticker, position_datetime):
        input_dates = datetime_string_to_yfinance_dates(position_datetime)
        return self.price_fetcher.get_price(ticker, position_datetime, input_dates[0], input_dates[1])

    def get_forecast(self, ticker, position_datetime):
        return self.lstm_forecaster.generate_forecast(ticker, position_datetime, 360, 60)

    def new_open_position(self, position_datetime):
        sentiment = self.get_sentiment(position_datetime)
        print(sentiment)

        ticker = sentiment[0].replace('$', '')
        price = self.get_price(ticker, position_datetime)
        print(price)
        forecast = self.get_forecast(ticker, position_datetime)
        print(forecast)

        min_cash_to_spend = 10000.00
        shares = int(min_cash_to_spend / price) + (min_cash_to_spend % price > 0)
        position = None
        sentiment_rating = sentiment[1]
        if (sentiment_rating > 0) and (forecast < 0):
            position = Position(ticker, 'SHORT', shares, price, position_datetime)
        elif (sentiment_rating < 0) and (forecast > 0):
            position = Position(ticker, 'LONG', shares, price, position_datetime)

        if position is not None:
            self.open_positions.append(position)
            print(f'New position: {position}')
        else:
            print(f'No new position on {position_datetime}')
