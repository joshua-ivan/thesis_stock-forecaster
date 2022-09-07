import utilities.date_util as date_util
import unittest
import pandas


class RedditScraperTests(unittest.TestCase):
    def test_generate_aggregate_columns(self):
        expected = ['Ticker', '2022-01-15', '2022-01-22', '2022-01-29', '2022-02-05']
        actual = date_util.generate_aggregate_columns(end_date='2022-02-05', timeframe_days=28, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_aggregate_columns_extra_days_in_first_interval(self):
        expected = ['Ticker', '2022-01-15', '2022-01-22', '2022-01-29', '2022-02-05']
        actual = date_util.generate_aggregate_columns(end_date='2022-02-05', timeframe_days=30, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_aggregate_columns_interval_one(self):
        expected = ['Ticker', '2022-02-03', '2022-02-04', '2022-02-05']
        actual = date_util.generate_aggregate_columns(end_date='2022-02-05', timeframe_days=3, interval=1)
        self.assertEqual(expected, actual)

    def test_generate_aggregate_columns_timeframe_days_one(self):
        expected = ['Ticker', '2022-02-05']
        actual = date_util.generate_aggregate_columns(end_date='2022-02-05', timeframe_days=1, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_bin_boundaries(self):
        expected = [
            {'start': '2022-01-09', 'end': '2022-01-15'},
            {'start': '2022-01-16', 'end': '2022-01-22'},
            {'start': '2022-01-23', 'end': '2022-01-29'},
            {'start': '2022-01-30', 'end': '2022-02-05'}]
        actual = date_util.generate_bin_boundaries(end_date='2022-02-05', timeframe_days=28, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_bin_boundaries_extra_days_in_first_interval(self):
        expected = [
            {'start': '2022-01-07', 'end': '2022-01-15'},
            {'start': '2022-01-16', 'end': '2022-01-22'},
            {'start': '2022-01-23', 'end': '2022-01-29'},
            {'start': '2022-01-30', 'end': '2022-02-05'}]
        actual = date_util.generate_bin_boundaries(end_date='2022-02-05', timeframe_days=30, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_bin_boundaries_interval_one(self):
        expected = [
            {'start': '2022-02-03', 'end': '2022-02-03'},
            {'start': '2022-02-04', 'end': '2022-02-04'},
            {'start': '2022-02-05', 'end': '2022-02-05'}]
        actual = date_util.generate_bin_boundaries(end_date='2022-02-05', timeframe_days=3, interval=1)
        self.assertEqual(expected, actual)

    def test_generate_bin_boundaries_timeframe_days_one(self):
        expected = [
            {'start': '2022-02-05', 'end': '2022-02-05'}]
        actual = date_util.generate_bin_boundaries(end_date='2022-02-05', timeframe_days=1, interval=7)
        self.assertEqual(expected, actual)

    def test_check_date_bin_utility_inputs(self):
        def end_date_check(end_date):
            with self.assertRaises(TypeError) as assertion:
                date_util.check_date_bin_utility_inputs('test', end_date=end_date, timeframe_days=28, interval=7)
            self.assertEqual(
                str(assertion.exception),
                f'test: \'{end_date}\' is not an ISO format date string')
        end_date_check('')
        end_date_check('foobar')
        end_date_check(54)

        def timeframe_days_check(timeframe_days):
            with self.assertRaises(TypeError) as assertion:
                date_util.check_date_bin_utility_inputs(
                    'test', end_date='2022-02-05', timeframe_days=timeframe_days, interval=7)
            self.assertEqual(
                str(assertion.exception),
                f'test: \'{timeframe_days}\' (timeframe_days) is not a positive integer')
        timeframe_days_check(0)
        timeframe_days_check(-4)
        timeframe_days_check('foobar')

        def interval_check(interval):
            with self.assertRaises(TypeError) as assertion:
                date_util.check_date_bin_utility_inputs(
                    'test', end_date='2022-02-05', timeframe_days=28, interval=interval)
            self.assertEqual(
                str(assertion.exception),
                f'test: \'{interval}\' (interval) is not a positive integer')
        interval_check(0)
        interval_check(-4)
        interval_check('foobar')

    def test_get_stock_action_date(self):
        history = pandas.read_csv('mock_data/forecaster/MOCK.csv')
        self.assertEqual(date_util.get_stock_action_date(history, '2021-12-31'), '2021-12-31')
        self.assertEqual(date_util.get_stock_action_date(history, '2022-01-01'), '2021-12-31')

    def test_datetime_string_to_posix(self):
        expected = 1661301000.0
        self.assertEqual(expected, date_util.datetime_string_to_posix('2022-08-23 13:30:00-04:00'))

    def test_datetime_string_to_yfinance_dates(self):
        expected = '2022-08-22', '2022-08-24'
        self.assertEqual(expected, date_util.datetime_string_to_yfinance_dates('2022-08-23 13:30:00-04:00'))
