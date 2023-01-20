from sentiment.analyzer import RedditAnalyzer
from forecaster.arima_garch_forecaster import ARIMAGARCHForecaster
from forecaster.lstm_forecaster import LSTMForecaster
from trader.investor import Investor
from trader.price_fetcher import PriceFetcher
from trader.position import Position
from utilities.date_util import datetime_string_to_posix, datetime_string_to_yfinance_dates
from utilities.file_io import write_file
from datetime import datetime, timezone, timedelta


class MachineInvestor(Investor):
    def __init__(self, start_date, end_date, pf=PriceFetcher(), ra=RedditAnalyzer(), fc=ARIMAGARCHForecaster()):
        super().__init__(start_date, end_date, pf)
        self.reddit_analyzer = ra
        self.forecaster = fc

    def get_sentiment(self, position_datetime):
        posix_timestamp = datetime_string_to_posix(position_datetime)
        return self.reddit_analyzer.extract_sentiment(int(posix_timestamp - (60 * 60)), int(posix_timestamp))

    def get_price(self, ticker, position_datetime):
        input_dates = datetime_string_to_yfinance_dates(position_datetime)
        return self.price_fetcher.get_price(ticker, position_datetime, input_dates[0], input_dates[1])

    def get_forecast(self, ticker, position_datetime):
        # return self.forecaster.generate_forecast(ticker, position_datetime, 360, 60)
        return self.forecaster.generate_forecast(ticker, position_datetime, 60)

    def new_open_position(self, ticker, sentiment, price, forecast, position_datetime):
        min_cash_to_spend = 10000.00
        shares = int(min_cash_to_spend / price) + (min_cash_to_spend % price > 0)
        position = None
        if (sentiment > 0.05) and (forecast < -0.01):
            position = Position(ticker, 'SHORT', shares, price, position_datetime)
        elif (sentiment < -0.05) and (forecast > 0.01):
            position = Position(ticker, 'LONG', shares, price, position_datetime)

        if position is not None:
            self.open_positions.append(position)
            log_str = f'New position: {position}'
        else:
            log_str = f'No new position on {position_datetime}'
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

            sentiment = self.get_sentiment(current_datetime_str)
            ticker = sentiment[0].replace('$', '')
            price = self.get_price(ticker, current_datetime_str)
            forecast = self.get_forecast(ticker, current_datetime_str)
            log_str = f'sentiment: {sentiment} | price: {price} | forecast: {forecast}'
            self.log.append(log_str)
            print(log_str)

            self.new_open_position(ticker, sentiment[1], price, forecast, current_datetime_str)

            current_datetime = current_datetime + timedelta(minutes=1)
            if current_datetime.hour >= 16:
                current_datetime = current_datetime + timedelta(hours=17, minutes=30)

        log_timestamp = datetime.now().strftime('%m%d%Y_%H%M')
        write_file('.', f'machine_{log_timestamp}.log', ''.join([(lambda st: f'{st}\n')(st) for st in self.log]))
