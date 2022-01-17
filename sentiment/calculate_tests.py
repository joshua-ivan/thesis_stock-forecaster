from sentiment.calculate import SentimentCalculator
from unittest.mock import patch
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
