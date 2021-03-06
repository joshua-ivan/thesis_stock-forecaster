import config
from sentiment.calculate import SentimentCalculator, construct_post_paths, query_to_ticker, generate_aggregate_dataframe
from multiprocessing import Manager
from unittest.mock import patch
import unittest
import warnings
import pandas


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

    def test_append_dataframe(self):
        columns = ['Filename', 'Date', 'Length', 'Negative', 'Positive', 'Sentiment']
        data = [['test', '02-08-2022', 8, 0, 0, 0]]
        expected = pandas.DataFrame(data, columns=columns)
        self.calculator.append_dataframe(
            'test', '02-08-2022', {'length': 8, 'negative': 0, 'positive': 0, 'sentiment': 0})
        self.assertTrue(expected.loc[0].equals(self.calculator.dataframe.loc[0]))

    def test_aggregate_sentiment_bins(self):
        self.calculator.dataframe = pandas.read_csv('mock_data/sentiment/MOCK.csv')
        expected = ['TEST', 0.0043189439447462626, 0.00015967394926260045, 0.0026306249983937004]
        actual = self.calculator.aggregate_by_bin('TEST', '2021-02-08', data_size=7, bin_size=2)
        self.assertEqual(expected, actual)

    def test_aggregate_sentiment_bins_empty_bin(self):
        self.calculator.dataframe = pandas.read_csv('mock_data/sentiment/MOCK.csv')
        expected = ['TEST', 0]
        actual = self.calculator.aggregate_by_bin('TEST', '2021-02-09', data_size=1, bin_size=1)
        self.assertEqual(expected, actual)

    @patch('utilities.date_util.generate_bin_boundaries')
    def test_aggregate_sentiment_bins_no_bins(self, mock_boundaries):
        self.calculator.dataframe = pandas.read_csv('mock_data/sentiment/MOCK.csv')
        mock_boundaries.return_value = []
        expected = ['TEST']
        actual = self.calculator.aggregate_by_bin('TEST', '2021-02-09', data_size=1, bin_size=1)
        self.assertEqual(expected, actual)

    def test_generate_aggregate_dataframe(self):
        columns = ['Ticker', '02-08-2022', '02-08-2022']
        data = [
            ['TSTA', '0.5', '-0.5'],
            ['TSTB', '-0.5', '0.5'],
            ['TSTC', '0.5', '0.5'],
            ['TSTD', '-0.5', '-0.5']
        ]
        queue = Manager().Queue()
        for row in data:
            queue.put(row)

        expected = pandas.DataFrame(data, columns=columns)
        self.assertTrue(generate_aggregate_dataframe(columns, queue).equals(expected))

    def test_generate_aggregate_dataframe_empty_queue(self):
        columns = ['Ticker', '02-08-2022', '02-08-2022']
        queue = Manager().Queue()

        expected = pandas.DataFrame(columns=columns)
        self.assertTrue(generate_aggregate_dataframe(columns, queue).equals(expected))

    def test_generate_aggregate_dataframe_non_queue(self):
        columns = ['Ticker', '02-08-2022', '02-08-2022']
        queue = []

        with self.assertRaises(TypeError) as assertion:
            generate_aggregate_dataframe(columns, queue)
        expected_msg = 'generate_aggregate_dataframe: given data is not a multiprocessing.Manager.Queue'
        self.assertEqual(str(assertion.exception), expected_msg)
