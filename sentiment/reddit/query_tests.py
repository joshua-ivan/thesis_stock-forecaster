from sentiment.reddit import query
import unittest


class RedditQueryTests(unittest.TestCase):
    def test_reddit_query_single_keyword(self):
        keyword = ['test']
        self.assertEqual(query.build(keyword), '"test"')

    def test_reddit_query_multiple_keywords(self):
        keywords = ['foo', 'bar', 'baz']
        self.assertEqual(query.build(keywords), '"foo" OR "bar" OR "baz"')

    def test_reddit_query_phrases(self):
        keywords = ['foo', 'bar baz']
        self.assertEqual(query.build(keywords), '"foo" OR "bar baz"')

    if __name__ == '__main__':
        unittest.main()
