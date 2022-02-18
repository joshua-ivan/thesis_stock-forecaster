from unittest.mock import patch
from trader.simulation import Portfolio
import trader.simulation as simulation
import unittest
import config


class SimulationTests(unittest.TestCase):
    @patch('trader.simulation.lookup_price')
    def test_portfolio_buy(self, mock_lookup):
        portfolio = Portfolio(starting_funds=50000, funds_per_buy=1000, managed_stocks=config.stocks)

        mock_lookup.return_value = 500
        portfolio.buy('AAPL', '2022-02-09')
        self.assertEqual(portfolio.holdings['AAPL'], 2)
        self.assertEqual(portfolio.liquidity, 49000)
        portfolio.buy('MSFT', '2022-02-09')
        self.assertEqual(portfolio.holdings['MSFT'], 2)
        self.assertEqual(portfolio.liquidity, 48000)

        mock_lookup.return_value = 1000
        portfolio.buy('AAPL', '2022-02-16')
        self.assertEqual(portfolio.holdings['AAPL'], 3)
        self.assertEqual(portfolio.holdings['MSFT'], 2)
        self.assertEqual(portfolio.liquidity, 47000)

    @patch('trader.simulation.lookup_price')
    def test_portfolio_sell(self, mock_lookup):
        portfolio = Portfolio(starting_funds=50000, funds_per_buy=1000, managed_stocks=config.stocks)
        portfolio.holdings['AAPL'] = 10

        mock_lookup.return_value = 2000
        portfolio.sell('AAPL', '2022-02-16')
        self.assertEqual(portfolio.holdings['AAPL'], 0)
        self.assertEqual(portfolio.liquidity, 70000)

        portfolio.sell('AAPL', '2022-02-16')
        self.assertEqual(portfolio.holdings['AAPL'], 0)
        self.assertEqual(portfolio.liquidity, 70000)

    @patch('trader.simulation.lookup_price')
    def test_portfolio_value(self, mock_lookup):
        portfolio = Portfolio(starting_funds=50000, funds_per_buy=1000, managed_stocks=config.stocks)
        portfolio.holdings['AAPL'] = 10
        portfolio.holdings['MSFT'] = 20
        mock_lookup.return_value = 1500
        self.assertEqual(portfolio.value('2022-02-16'), 95000)

    def test_percent_returns(self):
        self.assertEqual(round(simulation.percent_returns(105, 100), 2), 5.00)
        self.assertEqual(round(simulation.percent_returns(95, 100), 2), -5.00)

    def test_annual_to_weekly_compound_interest_rate(self):
        self.assertEqual(round(simulation.annual_to_weekly_compound_interest_rate(0.05), 5), 0.00094)

    def test_sharpe_ratio(self):
        self.assertEqual(round(simulation.sharpe_ratio(0.12, 0.05, 0.1), 3), 0.7)
