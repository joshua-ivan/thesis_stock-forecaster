from sentiment.analyzer import RedditAnalyzer
from unittest.mock import Mock
import unittest
import pandas
import numpy


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

    def test_build_time_file_tuples(self):
        ra = RedditAnalyzer()
        filenames = [
            '1660970721.0 - t3_wsygps',
            '1660970724.0 - il13uj6',
            '1660970764.0 - il13wu8'
        ]
        expected_tuples = [
            ('1660970721', '1660970721.0 - t3_wsygps'),
            ('1660970724', '1660970724.0 - il13uj6'),
            ('1660970764', '1660970764.0 - il13wu8')
        ]
        self.assertEqual(expected_tuples, ra.build_time_file_tuples(filenames))

    def test_build_posts_dataframe(self):
        ra = RedditAnalyzer()
        ra.os = Mock()
        ra.os.listdir.return_value = [
            '1660970721.0 - t3_wsygps',
            '1660970724.0 - il13uj6',
            '1660970764.0 - il13wu8'
        ]

        expected_df = pandas.DataFrame([
            ('1660970721', '1660970721.0 - t3_wsygps'),
            ('1660970724', '1660970724.0 - il13uj6'),
            ('1660970764', '1660970764.0 - il13wu8')
        ], columns=['timestamp', 'filename'])
        expected_df.set_index('timestamp')
        expected_df['timestamp'] = expected_df['timestamp'].astype('int64')

        pandas.testing.assert_frame_equal(expected_df, ra.build_posts_dataframe(''))

    def test_filter_dataframe(self):
        ra = RedditAnalyzer()

        input_df = pandas.DataFrame([
            ('1660970721', '1660970721.0 - t3_wsygps'),
            ('1660970724', '1660970724.0 - il13uj6'),
            ('1660970764', '1660970764.0 - il13wu8')
        ], columns=['timestamp', 'filename'])
        input_df.set_index('timestamp')
        input_df['timestamp'] = input_df['timestamp'].astype('int64')

        expected_df = pandas.DataFrame([
            ('1660970721', '1660970721.0 - t3_wsygps'),
            ('1660970724', '1660970724.0 - il13uj6')
        ], columns=['timestamp', 'filename'])
        expected_df.set_index('timestamp')
        expected_df['timestamp'] = expected_df['timestamp'].astype('int64')

        pandas.testing.assert_frame_equal(expected_df, ra.filter_dataframe(
            input_df, 1660970720, 1660970725
        ))

    def test_extract_post_scores(self):
        ra = RedditAnalyzer()
        expected_arr = numpy.array([10, 1, -1])
        self.assertTrue(numpy.array_equal(expected_arr, ra.extract_post_scores(
            'mock_data/sentiment/analyzer/extract_post_scores', [
                '1660970721.0 - t3_wsygps',
                '1660970724.0 - il13uj6',
                '1660970764.0 - il13wu8'
            ])))

    def test_train_score_scaler(self):
        ra = RedditAnalyzer()
        # ra.train_score_scaler()
