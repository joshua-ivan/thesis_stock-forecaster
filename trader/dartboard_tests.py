from trader.dartboard import DartboardInvestor, Position
from unittest.mock import Mock, call
import unittest
import pandas


class DartboardTests(unittest.TestCase):
    def test_check_open_positions(self):
        mock_rng = Mock()
        dbi = DartboardInvestor(start_date='2022-08-15', end_date='2022-08-16', rng=mock_rng)
        dbi.open_positions = [Mock()]
        dbi.close_position = Mock()
        rng_test_cases = [0, 49, 50, 99]
        expected_calls = [
            [call(0, '2022-08-15 10:00:00-04:00')],
            [call(0, '2022-08-15 10:00:00-04:00')],
            [],
            [],
        ]

        for i in range(0, len(rng_test_cases)):
            dbi.close_position.reset_mock()
            mock_rng.randint.return_value = rng_test_cases[i]
            dbi.check_open_positions('2022-08-15 10:00:00-04:00')
            dbi.close_position.assert_has_calls(expected_calls[i])

        dbi.open_positions = [Mock(), Mock(), Mock()]
        mock_rng.randint.side_effect = iter([0, 0, 99])
        dbi.check_open_positions('2022-08-15 10:00:00-04:00')
        dbi.close_position.assert_has_calls(
            [call(2, '2022-08-15 10:00:00-04:00'), call(1, '2022-08-15 10:00:00-04:00')])

    def test_close_position(self):
        dbi = DartboardInvestor(start_date='2022-08-15', end_date='2022-08-16')
        dbi.open_positions = [
            Position('MOCK', 'SHORT', 5, 10000.00, '2022-08-15 10:00:00-04:00'),
            Position('MOCK', 'LONG', 5, 1000.00, '2022-08-15 11:00:00-04:00')
        ]
        dbi.get_price = Mock()
        dbi.get_price.return_value = 100.00

        dbi.close_position(0, '2022-08-15 11:00:00-04:00')
        self.assertEqual(dbi.portfolio_value, 49500.00)
        dbi.close_position(0, '2022-08-15 11:00:00-04:00')
        self.assertEqual(dbi.portfolio_value, 45000.00)

    def test_get_price(self):
        mock_os = Mock()
        dbi = DartboardInvestor(
            tickers=pandas.read_csv('mock_data/tickers.csv'), start_date=None, end_date=None, op_sys=mock_os,
            stock_dir='mock_data/trader/prices')
        dbi.get_stock_history = Mock()

        mock_os.path.exists.return_value = False
        price = dbi.get_price('GME', '2022-08-15 10:00:00-04:00')
        self.assertEqual(price, 38.900001525878906)
        dbi.get_stock_history.assert_called_with('GME')

        dbi.get_stock_history.reset_mock()
        mock_os.path.exists.return_value = True
        dbi.get_price('GME', '2022-08-15 10:00:00-04:00')
        dbi.get_stock_history.assert_not_called()

    def test_get_price_no_prices_returned(self):
        mock_os = Mock()
        mock_pandas = Mock()
        dbi = DartboardInvestor(
            tickers=pandas.read_csv('mock_data/tickers.csv'), start_date=None, end_date=None, op_sys=mock_os,
            pd=mock_pandas, stock_dir='mock_data/trader/prices')

        mock_os.path.exists.return_value = True
        mock_pandas.read_csv.return_value = pandas.DataFrame(
            columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'])
        price = dbi.get_price('GME', '2022-08-15 10:00:00-04:00')
        self.assertEqual(-1, price)

        mock_pandas.read_csv.return_value = pandas.DataFrame(
            columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        price = dbi.get_price('GME', '2022-08-15 10:00:00-04:00')
        self.assertEqual(-1, price)

    def test_get_stock_history(self):
        mock_yfinance = Mock()
        mock_ticker = Mock()
        mock_yfinance.Ticker.return_value = mock_ticker
        mock_history = Mock()
        mock_ticker.history.return_value = mock_history
        dbi = DartboardInvestor(start_date='2022-08-15', end_date='2022-08-16', yf=mock_yfinance)

        dbi.get_stock_history('MOCK')
        mock_yfinance.Ticker.assert_called_with('MOCK')
        mock_ticker.history.assert_called_with( start=dbi.start_date, end=dbi.end_date, period='1d', interval='1m')
        mock_history.to_csv.assert_called_with('intermediate_data/prices/MOCK.csv')

    def test_new_open_position(self):
        mock_rng = Mock()
        dbi = DartboardInvestor(tickers=pandas.read_csv('mock_data/tickers.csv'),
                                start_date='2022-08-15', end_date='2022-08-16', rng=mock_rng)
        dbi.get_price = Mock()

        mock_rng.randint.side_effect = iter([2, 0])
        dbi.get_price.return_value = 600.00
        dbi.new_open_position('2022-08-15 10:00:00-04:00')
        expected_position = Position('HOOD', 'SHORT', 17, 600.00, '2022-08-15 10:00:00-04:00')
        self.assertEqual(expected_position, dbi.open_positions[0])

        mock_rng.randint.side_effect = iter([4, 99])
        dbi.get_price.return_value = 500.00
        dbi.new_open_position('2022-08-15 11:00:00-04:00')
        expected_position = Position('TSLA', 'LONG', 20, 500.00, '2022-08-15 11:00:00-04:00')
        self.assertEqual(expected_position, dbi.open_positions[1])

        mock_rng.randint.side_effect = iter([3, 3, 0])
        dbi.get_price.side_effect = iter([-1, 500])
        dbi.new_open_position('2022-08-15 11:00:00-04:00')
        expected_position = Position('COIN', 'SHORT', 20, 500.00, '2022-08-15 11:00:00-04:00')
        self.assertEqual(expected_position, dbi.open_positions[2])

    def test_live(self):
        dbi = DartboardInvestor(start_date='2022-08-15', end_date='2022-08-16')
        dbi.run_simulation()
        print(dbi.portfolio_value)
        for position in dbi.open_positions:
            print(position)
