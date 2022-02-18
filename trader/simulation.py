from utilities.pandas_util import extract_cell
import utilities.input_validation as input_validation
import utilities.date_util as date_util
import pandas
import numpy
import config
import math


def lookup_price(ticker, date):
    history = pandas.read_csv(f'prices/{ticker}.csv', usecols=['Date', 'Adj Close'])
    action_date = date_util.get_stock_action_date(history, date)
    return extract_cell(history, 'Date', action_date, 'Adj Close')


class Portfolio:
    def __init__(self, starting_funds, funds_per_buy, managed_stocks):
        self.liquidity = starting_funds
        self.funds_per_buy = funds_per_buy
        self.holdings = {}
        for stock in managed_stocks:
            self.holdings[stock['ticker']] = 0

    def buy(self, ticker, date):
        input_validation.check_nonempty_string(ticker, 'Portfolio.buy')
        input_validation.check_isoformat_date_string(date, 'Portfolio.buy')

        stock_price = lookup_price(ticker, date)
        self.liquidity = self.liquidity - self.funds_per_buy
        self.holdings[ticker] = self.holdings[ticker] + (self.funds_per_buy / stock_price)

    def sell(self, ticker, date):
        input_validation.check_nonempty_string(ticker, 'Portfolio.sell')
        input_validation.check_isoformat_date_string(date, 'Portfolio.sell')

        stock_price = lookup_price(ticker, date)
        self.liquidity = self.liquidity + (self.holdings[ticker] * stock_price)
        self.holdings[ticker] = 0

    def value(self, date):
        value = self.liquidity
        for ticker in self.holdings.keys():
            price = lookup_price(ticker, date)
            value = value + (self.holdings[ticker] * price)
        return value


def percent_returns(new_value, old_value):
    input_validation.check_float(new_value, 'percent_returns')
    input_validation.check_float(old_value, 'percent_returns')
    return ((new_value / old_value) - 1) * 100


def annual_to_weekly_compound_interest_rate(annual_rate):
    input_validation.check_float(annual_rate, 'annual_to_weekly_compound_interest_rate')
    return math.pow(1 + annual_rate, (1 / 52)) - 1


def sharpe_ratio(mean_returns, riskless_returns, stdev_returns):
    input_validation.check_float(mean_returns, 'sharpe_ratio')
    input_validation.check_float(riskless_returns, 'sharpe_ratio')
    input_validation.check_float(stdev_returns, 'sharpe_ratio')
    return (mean_returns - riskless_returns) / stdev_returns


def execute():
    portfolio = Portfolio(starting_funds=50000, funds_per_buy=1000, managed_stocks=config.stocks)
    decisions = pandas.read_csv('decision.csv')
    values = [50000]
    returns = [0.0]

    for date in decisions.columns[1:]:
        for stock in config.stocks:
            decision = extract_cell(decisions, 'Ticker', stock['ticker'], date)
            if decision == 'BUY':
                portfolio.buy(stock['ticker'], date)
            elif decision == 'SELL':
                portfolio.sell(stock['ticker'], date)

        value = portfolio.value(date)
        values.append(value)
        percent_return = percent_returns(values[-1], values[-2])
        returns.append(percent_return)
        print(f'{date}: Value - {value} Returns - {percent_return}')

    mean = numpy.mean(returns[1:])
    print(f'Average weekly portfolio returns: {mean}')
    stdev = numpy.std(returns[1:])
    print(f'Stdev weekly portfolio returns: {stdev}')
    weekly_savings_rate = 100 * annual_to_weekly_compound_interest_rate(0.02)
    _sharpe_ratio = sharpe_ratio(mean, weekly_savings_rate, stdev)
    print(f'Sharpe ratio vs. 2% interest savings: {_sharpe_ratio}')
