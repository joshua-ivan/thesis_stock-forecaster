from sentiment.analyzer import RedditAnalyzer
from unittest.mock import Mock
import unittest


class RedditScraperTests(unittest.TestCase):
    def test_raw_score(self):
        ra = RedditAnalyzer()
        ra.tokenizer = Mock()
        ra.tokenizer.sent_tokenize.return_value = ['mock', 'text']
        ra.sid = Mock()
        ra.sid.polarity_scores.side_effect = [{'compound': 1.0}, {'compound': -0.5}]

        sentiment = ra.raw_score('mock text')
        ra.tokenizer.sent_tokenize.assert_called_once()
        ra.sid.polarity_scores.assert_has_calls([])
        self.assertEqual(sentiment, 0.5)

    def test_parse_tickers(self):
        ra = RedditAnalyzer()
        ra.tokenizer = Mock()

        test_cases = [
            ['mock', 'text'],
            ['MOCK', 'text'],
            ['$MOCK', 'text'],
            ['MOCK^A', 'text'],
            ['$MOCK^A', 'text'],
            ['MOCK', 'TEXT']
        ]
        expected_values = [
            [],
            ['MOCK'],
            ['MOCK'],
            ['MOCK'],
            ['MOCK'],
            ['MOCK', 'TEXT']
        ]
        for i in range(0, len(test_cases)):
            ra.tokenizer.reset_mock()
            ra.tokenizer.word_tokenize.return_value = test_cases[i]
            tickers = ra.parse_tickers('')
            self.assertCountEqual(tickers, expected_values[i])
