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
