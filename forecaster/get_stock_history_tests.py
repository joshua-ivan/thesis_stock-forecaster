from forecaster import get_stock_history
import unittest
import time


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
