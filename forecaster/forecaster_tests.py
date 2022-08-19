from forecaster import forecaster
from datetime import datetime
import unittest
import pandas
import numpy


class ForecasterTests(unittest.TestCase):
    MOCK_DIR = 'mock_data/forecaster'

    def test_read_stock_prices(self):
        data = [336.320007, 334.75, 329.01001, 316.380005, 313.880005, 313.649994]
        index = ['2021-12-31', '2022-01-03', '2022-01-04', '2022-01-05', '2022-01-06', '2022-01-07']
        expected = pandas.DataFrame(data, columns=['Adj Close'], index=pandas.Index(index, name='Date'))
        actual = forecaster.read_stock_prices(self.MOCK_DIR, 'MOCK')
        self.assertTrue(expected.equals(actual))

    def test_read_stock_prices_csv_not_found(self):
        try:
            forecaster.read_stock_prices(self.MOCK_DIR, 'TEST')
            self.fail()
        except FileNotFoundError as error:
            self.assertEqual(str(error), 'No price history found for TEST')

    def test_fill_missing_dates(self):
        data = [336.320007, 336.320007, 336.320007, 334.75,
                329.01001, 316.380005, 313.880005, 313.649994]
        index = ['2021-12-31', '2022-01-01', '2022-01-02', '2022-01-03',
                 '2022-01-04', '2022-01-05', '2022-01-06', '2022-01-07']
        expected = pandas.DataFrame(data, columns=['Adj Close'], index=pandas.Index(index, name='Date'))
        expected.index = pandas.to_datetime(expected.index, format='%Y-%m-%d')
        actual = forecaster.fill_missing_dates(forecaster.read_stock_prices(self.MOCK_DIR, 'MOCK'))
        self.assertTrue(expected.equals(actual))

    def test_calculate_percent_error(self):
        self.assertEqual(1, forecaster.calculate_percent_error(99, 100))
        self.assertEqual(5, forecaster.calculate_percent_error(95, 100))

    def test_calculate_percent_error_non_numeric_args(self):
        expected, actual = 'fish', 'chips'
        try:
            forecaster.calculate_percent_error(expected, 2)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), f'calculate_percent_error: \'{expected}\' is not a floating-point number')

        try:
            forecaster.calculate_percent_error(2, actual)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), f'calculate_percent_error: \'{actual}\' is not a floating-point number')

    def test_price_history_bin_to_series(self):
        expected = [313.880005, 313.649994]
        prices = forecaster.fill_missing_dates(forecaster.read_stock_prices(self.MOCK_DIR, 'MOCK'))
        _bin = {'start': '2022-01-06', 'end': '2022-01-07'}
        actual = forecaster.price_history_bin_to_series(prices, _bin)
        self.assertTrue((expected == actual).all())
