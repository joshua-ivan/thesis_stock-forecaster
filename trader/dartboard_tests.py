from trader.dartboard import DartboardInvestor, Position
from unittest.mock import Mock, call
import unittest
import pandas


class DartboardTests(unittest.TestCase):
    def test_check_open_positions(self):
        mock_fetcher = Mock()
        mi = DartboardInvestor(start_date='2022-08-15', end_date='2022-08-16', pf=mock_fetcher)
        mi.close_position = Mock()
        mi.open_positions = [
            Position('MOCK', 'SHORT', quantity=5, price=1000.00, date_time='2022-08-15 10:00:00-04:00'),
            Position('MOCK', 'SHORT', quantity=5, price=1000.00, date_time='2022-08-15 11:00:00-04:00'),
            Position('MOCK', 'SHORT', quantity=5, price=1000.00, date_time='2022-08-15 12:00:00-04:00'),
            Position('MOCK', 'LONG', quantity=5, price=1000.00, date_time='2022-08-15 13:00:00-04:00'),
            Position('MOCK', 'LONG', quantity=5, price=1000.00, date_time='2022-08-15 14:00:00-04:00'),
            Position('MOCK', 'LONG', quantity=5, price=1000.00, date_time='2022-08-15 15:00:00-04:00')
        ]
        mock_fetcher.get_price.side_effect = iter([2000.00, 1000.00, 500.00, 500.00, 1000.00, 2000.00])

        mi.check_open_positions('2022-08-15 16:00:00-04:00')
        mi.close_position.assert_has_calls([
            call(5000, 5), call(-2500, 3), call(2500, 2), call(-5000, 0)
        ])

    def test_close_position(self):
        mi = DartboardInvestor(start_date='2022-08-15', end_date='2022-08-16')
        mi.open_positions = [
            Position('MOCK', 'SHORT', 5, 10000.00, '2022-08-15 10:00:00-04:00'),
            Position('MOCK', 'LONG', 5, 1000.00, '2022-08-15 11:00:00-04:00')
        ]

        expected_values = [49500.00, 45000.00]
        for i in range(0, len(expected_values)):
            opening_value = mi.open_positions[0].quantity * mi.open_positions[0].price
            closing_value = mi.open_positions[0].quantity * 100.00
            position = mi.open_positions[0]

            raw_profit = 0.0
            if position.leverage_type == 'SHORT':
                raw_profit = opening_value - closing_value
            elif position.leverage_type == 'LONG':
                raw_profit = closing_value - opening_value

            mi.close_position(raw_profit, 0)
            self.assertEqual(mi.portfolio_value, expected_values[i])

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
        dbi.run_simulation()
        # print(dbi.portfolio_value)
        for position in dbi.open_positions:
            print(position)
