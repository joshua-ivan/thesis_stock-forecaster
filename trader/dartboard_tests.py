from trader.dartboard import DartboardInvestor
from trader.position import Position
from unittest.mock import Mock
import unittest
import pandas


class DartboardTests(unittest.TestCase):
    def test_new_open_position(self):
        mock_price_fetcher = Mock()
        mock_rng = Mock()
        dbi = DartboardInvestor(tickers=pandas.read_csv('mock_data/tickers.csv'), start_date='2022-08-15',
                                end_date='2022-08-16', pf=mock_price_fetcher, rng=mock_rng)

        mock_rng.randint.side_effect = iter([2, 0])
        mock_price_fetcher.get_price.return_value = 600.00
        dbi.new_open_position('2022-08-15 10:00:00-04:00')
        expected_position = Position('HOOD', 'SHORT', 17, 600.00, '2022-08-15 10:00:00-04:00')
        self.assertEqual(expected_position, dbi.open_positions[0])

        mock_rng.randint.side_effect = iter([4, 99])
        mock_price_fetcher.get_price.return_value = 500.00
        dbi.new_open_position('2022-08-15 11:00:00-04:00')
        expected_position = Position('TSLA', 'LONG', 20, 500.00, '2022-08-15 11:00:00-04:00')
        self.assertEqual(expected_position, dbi.open_positions[1])

        mock_rng.randint.side_effect = iter([3, 3, 0])
        mock_price_fetcher.get_price.side_effect = iter([-1, 500])
        dbi.new_open_position('2022-08-15 11:00:00-04:00')
        expected_position = Position('COIN', 'SHORT', 20, 500.00, '2022-08-15 11:00:00-04:00')
        self.assertEqual(expected_position, dbi.open_positions[2])

    def test_live(self):
        dbi = DartboardInvestor(start_date='2022-08-15', end_date='2022-08-20')
        # dbi.run_simulation()
        # print(dbi.portfolio_value)
        for position in dbi.open_positions:
            print(position)
