from unittest.mock import patch, call
import unittest
from sentiment.reddit.api import RedditAPI
from sentiment.reddit.scraper import RedditScraper
from datetime import timedelta
import time


class RedditScraperTests(unittest.TestCase):
    def get_item_mock(self, timestamps):
        mock = []
        index = 0
        for timestamp in timestamps:
            mock.append(self.MockSubmission(timestamp, f't3_test{index}', 'test title', 'test contents'))
            index += 1
        return mock

    def generate_timestamps(self, deltas):
        timestamps = []
        for delta in deltas:
            timestamps.append(self.current_time - timedelta(days=delta).total_seconds())
        return timestamps

    class MockSubmission:
        def __init__(self, created_utc, fullname, title, selftext):
            self.created_utc = created_utc
            self.fullname = fullname
            self.title = title
            self.selftext = selftext

    def setUp(self):
        self.current_time = time.time()
        self.last_week_time = self.current_time - timedelta(days=7).total_seconds()

    @patch.object(RedditAPI, 'search')
    @patch('sentiment.reddit.scraper.write_submission')
    def test_scrape_empty_submissions(self, mock_write, mock_search):
        mock_search.return_value = iter(())
        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape(query='test', start_date=self.last_week_time, end_date=time.time(), after='')
            self.assertEqual(scrape_spy.call_count, 1)
        mock_write.assert_not_called()

    @patch.object(RedditAPI, 'search')
    @patch('sentiment.reddit.scraper.write_submission')
    def test_scrape_one_submission(self, mock_write, mock_search):
        timestamps = self.generate_timestamps([1])
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape(query='test', start_date=self.last_week_time, end_date=self.current_time, after='')
            self.assertEqual(scrape_spy.call_count, 2)
        mock_write.assert_has_calls([
            call('posts/test', f'{timestamps[0]} - t3_test0', f'test title\n\n\ntest contents')
        ])

    @patch.object(RedditAPI, 'search')
    @patch('sentiment.reddit.scraper.write_submission')
    def test_scrape_many_submissions(self, mock_write, mock_search):
        timestamps = self.generate_timestamps([1, 2, 3])
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape(query='test', start_date=self.last_week_time, end_date=self.current_time, after='')
            self.assertEqual(scrape_spy.call_count, 2)
        mock_write.assert_has_calls([
            call('posts/test', f'{timestamps[0]} - t3_test0', f'test title\n\n\ntest contents'),
            call('posts/test', f'{timestamps[1]} - t3_test1', f'test title\n\n\ntest contents'),
            call('posts/test', f'{timestamps[2]} - t3_test2', f'test title\n\n\ntest contents'),
        ])

    @patch.object(RedditAPI, 'search')
    @patch('sentiment.reddit.scraper.write_submission')
    def test_scrape_skip_submissions_past_end_date(self, mock_write, mock_search):
        timestamps = self.generate_timestamps([-1, 0, 1])
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape(query='test', start_date=self.last_week_time, end_date=self.current_time, after='')
            self.assertEqual(scrape_spy.call_count, 2)
        mock_write.assert_has_calls([
            call('posts/test', f'{timestamps[2]} - t3_test2', f'test title\n\n\ntest contents')
        ])

    @patch.object(RedditAPI, 'search')
    @patch('sentiment.reddit.scraper.write_submission')
    def test_scrape_stop_before_start_date(self, mock_write, mock_search):
        timestamps = self.generate_timestamps([1, 8])
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape(query='test', start_date=self.last_week_time, end_date=self.current_time, after='')
            self.assertEqual(scrape_spy.call_count, 1)
        mock_write.assert_has_calls([
            call('posts/test', f'{timestamps[0]} - t3_test0', f'test title\n\n\ntest contents')
        ])

    if __name__ == '__main__':
        unittest.main()
