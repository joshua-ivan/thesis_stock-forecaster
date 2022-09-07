from trader.price_fetcher import PriceFetcher
from unittest.mock import Mock
import unittest
import pandas


class PriceFetcherTests(unittest.TestCase):
    def test_get_price(self):
        pf = PriceFetcher(stock_dir='mock_data/trader/prices')
        pf.get_stock_history = Mock()
        pf.get_stock_history.return_value = pandas.read_csv('mock_data/trader/prices/GME.csv')
        start_date, end_date = '2022-08-15', '2022-08-16'

        price = pf.get_price('GME', '2022-08-15 10:00:00-04:00', start_date, end_date)
        pf.get_stock_history.assert_called_with('GME', start_date, end_date)
        self.assertEqual(price, 38.900001525878906)

    def test_get_price_no_prices_returned(self):
        mock_pandas = Mock()
        pf = PriceFetcher(pd=mock_pandas, stock_dir='mock_data/trader/prices')
        pf.get_stock_history = Mock()
        start_date, end_date = '2022-08-15', '2022-08-16'

        pf.get_stock_history.return_value = pandas.DataFrame(
            columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'])
        price = pf.get_price('GME', '2022-08-15 10:00:00-04:00', start_date, end_date)
        self.assertEqual(-1, price)

        pf.get_stock_history.return_value = pandas.DataFrame(
            columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        price = pf.get_price('GME', '2022-08-15 10:00:00-04:00', start_date, end_date)
        self.assertEqual(-1, price)

    def test_get_stock_history(self):
        mock_yfinance, mock_ticker, mock_history, mock_pandas, mock_os = Mock(), Mock(), Mock(), Mock(), Mock()
        mock_yfinance.Ticker.return_value = mock_ticker
        mock_ticker.history.return_value = mock_history
        pf = PriceFetcher(yf=mock_yfinance, pd=mock_pandas, op_sys=mock_os)

        mock_os.path.exists.return_value = False
        start_date, end_date = '2022-08-15', '2022-08-16'
        filename = 'intermediate_data/prices/MOCK.csv'
        pf.get_stock_history('MOCK', start_date, end_date)
        mock_ticker.history.assert_called_with(start=start_date, end=end_date, period='1d', interval='1m')
        mock_pandas.read_csv.assert_not_called()
        mock_pandas.concat.assert_not_called()
        mock_history.to_csv.assert_called_with(filename)

        mock_ticker.reset_mock()
        mock_history.reset_mock()
        mock_os.path.exists.return_value = True
        mock_df = Mock()
        mock_pandas.read_csv.return_value = mock_df
        merge_df = Mock()
        pf.merge_stock_data = Mock()
        pf.merge_stock_data.return_value = merge_df
        pf.get_stock_history('MOCK', start_date, end_date)
        mock_ticker.history.assert_called_with(start=start_date, end=end_date, period='1d', interval='1m')
        mock_pandas.read_csv.assert_called_with(filename, index_col=0, parse_dates=True)
        pf.merge_stock_data.assert_called_with(mock_history, mock_df)
        merge_df.to_csv.assert_called_with('intermediate_data/prices/MOCK.csv')

    def test_merge_stock_data(self):
        test_cases = ['all_difference', 'no_difference', 'more_old_than_new', 'more_new_than_old']
        case_dir = 'mock_data/trader/price_fetcher/merge_stock_data'
        pf = PriceFetcher()

        for case in test_cases:
            old_data = pandas.read_csv(f'{case_dir}/{case}/old.csv', index_col=0, parse_dates=True)
            new_data = pandas.read_csv(f'{case_dir}/{case}/new.csv', index_col=0, parse_dates=True)
            expected = pandas.read_csv(f'{case_dir}/expected.csv', index_col=0, parse_dates=True)
            merge_data = pf.merge_stock_data(new_data, old_data)
            pandas.testing.assert_frame_equal(merge_data, expected)
