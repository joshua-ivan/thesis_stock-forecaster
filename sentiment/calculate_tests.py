from sentiment.calculate import SentimentCalculator, construct_post_paths, query_to_ticker, generate_aggregate_columns
from unittest.mock import patch
import datetime
import unittest
import warnings


class RedditScraperTests(unittest.TestCase):
    def setUp(self):
        self.calculator = SentimentCalculator()

    def test_count_words(self):
        post = 'greatest protest prospered prosecute'
        expected = {'length': 4, 'negative': 2, 'positive': 2, 'sentiment': 0}
        self.assertEqual(expected, self.calculator.count_words(post, 'test'))

    def test_count_words_case_insensitive(self):
        post = 'GREATEST protest pRoSpErEd'
        expected = {'length': 3, 'negative': 1, 'positive': 2, 'sentiment': (1 / 3)}
        self.assertEqual(expected, self.calculator.count_words(post, 'test'))

    def test_count_words_extra_whitespace(self):
        post = 'greatest \n\t protest  prosecute'
        expected = {'length': 3, 'negative': 2, 'positive': 1, 'sentiment': (-1 / 3)}
        self.assertEqual(expected, self.calculator.count_words(post, 'test'))

    def test_count_words_nonfinancial_terms(self):
        post = 'test furious burner'
        expected = {'length': 3, 'negative': 0, 'positive': 0, 'sentiment': 0}
        self.assertEqual(expected, self.calculator.count_words(post, 'test'))

    @patch('warnings.warn')
    def test_count_words_dirty_string(self, mock_warn):
        warnings.filterwarnings('ignore', 'Post.*')
        post = 'super-charger test@example.com fire_burner'
        expected = {'length': 3, 'negative': 0, 'positive': 0, 'sentiment': 0}
        self.assertEqual(expected, self.calculator.count_words(post, 'test'))
        mock_warn.assert_called_once_with('Post \'test\' has not been properly cleaned')

    def test_count_words_nonstring_input(self):
        try:
            self.calculator.count_words(['test'], 'test')
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), 'SentimentCalculator.count_words expects an input string')

    @patch('os.listdir')
    def test_construct_post_paths(self, mock_listdir):
        mock_listdir.return_value = ['foo', 'bar', 'baz']
        self.assertEqual(construct_post_paths('test'), ['test/foo', 'test/bar', 'test/baz'])

    def test_query_to_ticker(self):
        self.assertEqual('TEST', query_to_ticker('"TEST" OR "TestQuery"'))

    @patch('warnings.warn')
    def test_query_to_ticker_malformed_query_format(self, mock_warn):
        warnings.filterwarnings('ignore', 'Query.*')
        queries = ['test', 'test"', 'test"  ']
        for query in queries:
            self.assertEqual(query_to_ticker(query), 'test')
            mock_warn.assert_called_with(f'Query {query} is malformed')

    def test_generate_aggregate_columns(self):
        expected = ['Ticker', '2022-01-15', '2022-01-22', '2022-01-29', '2022-02-05']
        actual = generate_aggregate_columns(end_date='2022-02-05', timeframe_days=28, interval=7)
        self.assertEqual(expected, actual)

    def test_generate_aggregate_columns_input_constraints(self):
        def end_date_check(end_date):
            with self.assertRaises(TypeError) as assertion:
                generate_aggregate_columns(end_date=end_date, timeframe_days=28, interval=7)
            self.assertEqual(
                str(assertion.exception),
                f'generate_aggregate_columns: \'{end_date}\' (end_date) is not an ISO format date string')
        end_date_check('')
        end_date_check('foobar')
        end_date_check(54)

        def timeframe_days_check(timeframe_days):
            with self.assertRaises(TypeError) as assertion:
                generate_aggregate_columns(end_date='2022-02-05', timeframe_days=timeframe_days, interval=7)
            self.assertEqual(
                str(assertion.exception),
                f'generate_aggregate_columns: \'{timeframe_days}\' (timeframe_days) is not a positive integer')
        timeframe_days_check(0)
        timeframe_days_check(-4)
        timeframe_days_check('foobar')

        def interval_check(interval):
            with self.assertRaises(TypeError) as assertion:
                generate_aggregate_columns(end_date='2022-02-05', timeframe_days=28, interval=interval)
            self.assertEqual(
                str(assertion.exception),
                f'generate_aggregate_columns: \'{interval}\' (interval) is not a positive integer')
        interval_check(0)
        interval_check(-4)
        interval_check('foobar')

    def test_generate_aggregate_columns_extra_days_in_first_interval(self):
        expected = ['Ticker', '2022-01-15', '2022-01-22', '2022-01-29', '2022-02-05']
        actual = generate_aggregate_columns(end_date='2022-02-05', timeframe_days=30, interval=7)
        self.assertEqual(expected, actual)
