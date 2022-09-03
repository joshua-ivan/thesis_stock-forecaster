from sentiment.post_sentiment import PostSentiment
from sentiment.analyzer import RedditAnalyzer
from unittest.mock import Mock
import unittest
import datetime
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
            ['abr', 'text'],
            ['ABR', 'text'],
            ['$ABR', 'text'],
            ['ABR^D', 'text'],
            ['$ABR^D', 'text'],
            ['ABR', 'TEXT']
        ]
        expected_values = [
            [],
            [],
            ['$ABR'],
            [],
            ['$ABR^D'],
            []
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

    def test_process_post(self):
        ra = RedditAnalyzer()
        post_dir = 'mock_data/sentiment/analyzer/process_post'
        mock_scaler = Mock()

        scaler_values = [1, 2, -2]
        expected_values = [
            [-0.1965, -0.3612],
            [-0.393, -0.7224],
            [0.393, 0.7224]
        ]

        for i in range(0, len(scaler_values)):
            mock_scaler.transform.return_value = scaler_values[i]

            comment_filename = '1660971180.0 - il14kjj'
            comment_sentiment = ra.process_post(post_dir, comment_filename, mock_scaler)
            expected_comment_sentiment = PostSentiment(comment_filename, ['$GCT'], expected_values[i][0])
            self.assertEqual(comment_sentiment.filename, expected_comment_sentiment.filename)
            self.assertEqual(comment_sentiment.tickers, expected_comment_sentiment.tickers)
            self.assertEqual(comment_sentiment.sentiment, expected_comment_sentiment.sentiment)

            submission_filename = '1660970721.0 - t3_wsygps'
            submission_sentiment = ra.process_post(post_dir, submission_filename, mock_scaler)
            expected_submission_sentiment = PostSentiment(submission_filename, ['$GCT'], expected_values[i][1])
            self.assertEqual(submission_sentiment.filename, expected_submission_sentiment.filename)
            self.assertEqual(submission_sentiment.tickers, expected_submission_sentiment.tickers)
            self.assertEqual(submission_sentiment.sentiment, expected_submission_sentiment.sentiment)

    def test_build_sentiment_dataframe(self):
        ra = RedditAnalyzer()
        post_sentiments = [
            PostSentiment('mock_file', ['$MOCK'], 1.0),
            PostSentiment('test_file', ['$TEST'], 1.0),
            PostSentiment('mock_test_file', ['$MOCK', '$TEST'], 1.0),
        ]
        expected_df = pandas.DataFrame({
            'filename': ['mock_file', 'test_file', 'mock_test_file'],
            'sentiment': [1.0, 1.0, 1.0],
            '$MOCK': [1, 0, 1],
            '$TEST': [0, 1, 1]
        })
        binarized_df = ra.build_sentiment_dataframe(post_sentiments)
        pandas.testing.assert_frame_equal(expected_df, binarized_df)

    def test_extract_frequency(self):
        ra = RedditAnalyzer()
        post_sentiments = [
            PostSentiment('mock_file_1', ['$MOCK'], 1.0),
            PostSentiment('mock_file_2', ['$MOCK'], 1.0),
            PostSentiment('mock_file_3', ['$MOCK'], 1.0),
            PostSentiment('test_file', ['$TEST'], 1.0),
            PostSentiment('mock_test_file', ['$MOCK', '$TEST'], 1.0),
        ]
        expected = pandas.Series({'$MOCK': 4, '$TEST': 2})
        actual = ra.extract_frequency(post_sentiments)
        pandas.testing.assert_series_equal(expected, actual)

    def test_extract_sentiment(self):
        ra = RedditAnalyzer()
        hottest_stock = ra.extract_sentiment(
            int(datetime.datetime(2022, 8, 23, 0, 0, 0).timestamp()),
            int(datetime.datetime(2022, 8, 23, 0, 30, 0).timestamp())
        )
        # print(hottest_stock)

    def test_twenty_four_hour_freqency(self):
        # ra = RedditAnalyzer()
        # start_time = int(datetime.datetime(2022, 8, 22, 0, 0, 0).timestamp())
        # end_time = int(datetime.datetime(2022, 8, 23, 0, 0, 0).timestamp())
        # for time in range(start_time, end_time, 60):
        #     ra.extract_sentiment(time, time + (60 * 60))
        pass