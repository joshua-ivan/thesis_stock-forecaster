from utilities.date_util import generate_aggregate_columns, generate_bin_boundaries, check_date_utility_inputs
import unittest


class RedditScraperTests(unittest.TestCase):
    def test_generate_aggregate_columns(self):
        expected = ['Ticker', '2022-01-15', '2022-01-22', '2022-01-29', '2022-02-05']
        actual = generate_aggregate_columns(end_date='2022-02-05', timeframe_days=28, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_aggregate_columns_extra_days_in_first_interval(self):
        expected = ['Ticker', '2022-01-15', '2022-01-22', '2022-01-29', '2022-02-05']
        actual = generate_aggregate_columns(end_date='2022-02-05', timeframe_days=30, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_bin_boundaries(self):
        expected = [
            {'start': '2022-01-09', 'end': '2022-01-15'},
            {'start': '2022-01-16', 'end': '2022-01-22'},
            {'start': '2022-01-23', 'end': '2022-01-29'},
            {'start': '2022-01-30', 'end': '2022-02-05'}]
        actual = generate_bin_boundaries(end_date='2022-02-05', timeframe_days=28, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_bin_boundaries_extra_days_in_first_interval(self):
        expected = [
            {'start': '2022-01-07', 'end': '2022-01-15'},
            {'start': '2022-01-16', 'end': '2022-01-22'},
            {'start': '2022-01-23', 'end': '2022-01-29'},
            {'start': '2022-01-30', 'end': '2022-02-05'}]
        actual = generate_bin_boundaries(end_date='2022-02-05', timeframe_days=30, interval=7)
        self.assertEqual(expected, actual)

    def test_check_date_utility_inputs(self):
        def end_date_check(end_date):
            with self.assertRaises(TypeError) as assertion:
                check_date_utility_inputs('test', end_date=end_date, timeframe_days=28, interval=7)
            self.assertEqual(
                str(assertion.exception),
                f'test: \'{end_date}\' (end_date) is not an ISO format date string')
        end_date_check('')
        end_date_check('foobar')
        end_date_check(54)

        def timeframe_days_check(timeframe_days):
            with self.assertRaises(TypeError) as assertion:
                check_date_utility_inputs('test', end_date='2022-02-05', timeframe_days=timeframe_days, interval=7)
            self.assertEqual(
                str(assertion.exception),
                f'test: \'{timeframe_days}\' (timeframe_days) is not a positive integer')
        timeframe_days_check(0)
        timeframe_days_check(-4)
        timeframe_days_check('foobar')

        def interval_check(interval):
            with self.assertRaises(TypeError) as assertion:
                check_date_utility_inputs('test', end_date='2022-02-05', timeframe_days=28, interval=interval)
            self.assertEqual(
                str(assertion.exception),
                f'test: \'{interval}\' (interval) is not a positive integer')
        interval_check(0)
        interval_check(-4)
        interval_check('foobar')
