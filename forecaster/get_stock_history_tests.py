from forecaster import get_stock_history
from unittest.mock import Mock
import unittest
import time
import os


class GetStockHistoryTests(unittest.TestCase):
    def test_build_query_params(self):
        end_timestamp = time.time()
        interval_days = 7
        expected_query_params = {
            'period1': int(end_timestamp - (interval_days * 24 * 60 * 60)),
            'period2': int(end_timestamp),
            'interval': '1d',
            'events': 'history',
            'includeAdjustedClose': 'true'
        }
        actual_query_params = get_stock_history.build_query_params(end_timestamp, interval_days)
        self.assertEqual(expected_query_params, actual_query_params)

    def test_get_stocks(self):
        mock_api = Mock()
        mock_ticker = Mock()
        mock_api.Ticker.return_value = mock_ticker

        get_stock_history.get_stocks(ticker='MOCK', period='2d', api=mock_api)

        mock_api.Ticker.assert_called_with('MOCK')
        mock_ticker.history.assert_called_with(period='2d', interval='1m')

        # os.makedirs('../forecaster_data/prices')
        # get_stock_history.get_stocks(ticker='GME', period='2d').to_csv('../forecaster_data/prices/GME.csv')
