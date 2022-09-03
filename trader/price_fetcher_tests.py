from trader.price_fetcher import PriceFetcher
from unittest.mock import Mock
import unittest
import pandas


class PriceFetcherTests(unittest.TestCase):
    def test_get_price(self):
        mock_os = Mock()
        pf = PriceFetcher(op_sys=mock_os, stock_dir='mock_data/trader/prices')
        pf.get_stock_history = Mock()
        start_date, end_date = '2022-08-15', '2022-08-16'

        mock_os.path.exists.return_value = False
        price = pf.get_price('GME', '2022-08-15 10:00:00-04:00', start_date, end_date)
        self.assertEqual(price, 38.900001525878906)
        pf.get_stock_history.assert_called_with('GME', start_date, end_date)

        pf.get_stock_history.reset_mock()
        mock_os.path.exists.return_value = True
        pf.get_price('GME', '2022-08-15 10:00:00-04:00', start_date, end_date)
        pf.get_stock_history.assert_not_called()

    def test_get_price_no_prices_returned(self):
        mock_os = Mock()
        mock_pandas = Mock()
        pf = PriceFetcher(op_sys=mock_os, pd=mock_pandas, stock_dir='mock_data/trader/prices')
        start_date, end_date = '2022-08-15', '2022-08-16'

        mock_os.path.exists.return_value = True
        mock_pandas.read_csv.return_value = pandas.DataFrame(
            columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'])
        price = pf.get_price('GME', '2022-08-15 10:00:00-04:00', start_date, end_date)
        self.assertEqual(-1, price)

        mock_pandas.read_csv.return_value = pandas.DataFrame(
            columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        price = pf.get_price('GME', '2022-08-15 10:00:00-04:00', start_date, end_date)
        self.assertEqual(-1, price)

    def test_get_stock_history(self):
        mock_yfinance = Mock()
        mock_ticker = Mock()
        mock_yfinance.Ticker.return_value = mock_ticker
        mock_history = Mock()
        mock_ticker.history.return_value = mock_history
        pf = PriceFetcher(yf=mock_yfinance)

        start_date, end_date = '2022-08-15', '2022-08-16'
        pf.get_stock_history('MOCK', start_date, end_date)
        mock_yfinance.Ticker.assert_called_with('MOCK')
        mock_ticker.history.assert_called_with(start=start_date, end=end_date, period='1d', interval='1m')
        mock_history.to_csv.assert_called_with('intermediate_data/prices/MOCK.csv')
