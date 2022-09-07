from sentiment.analyzer import RedditAnalyzer
from forecaster.lstm_forecaster import LSTMForecaster
from trader.price_fetcher import PriceFetcher
from trader.position import Position
from datetime import datetime


class MachineInvestor:
    def __init__(self, start_date, end_date, pf=PriceFetcher()):
        self.open_positions = []
        self.portfolio_value = 0.0
        self.loss_threshold = 0.01
        self.start_date = start_date
        self.end_date = end_date
        self.price_fetcher = pf

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

    def new_open_position(self):
        position_datetime = '2022-08-23 13:30:00-04:00'

        ra = RedditAnalyzer()
        sentiment = ra.extract_sentiment(
            int(datetime(2022, 8, 23, 12, 30, 0).timestamp()),
            int(datetime(2022, 8, 23, 13, 30, 0).timestamp())
        )
        print(sentiment)

        ticker = sentiment[0].replace('$', '')
        price = self.price_fetcher.get_price(ticker, position_datetime, '2022-08-22', '2022-08-24')
        lstm_fcr = LSTMForecaster()
        forecast = lstm_fcr.generate_forecast(ticker, position_datetime, 360, 60)
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
