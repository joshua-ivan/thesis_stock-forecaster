from sentiment import build_database
import unittest


class BuildDatabaseTests(unittest.TestCase):
    def test_build_query_single_keyword(self):
        keyword = ['test']
        query = build_database.build_query(keyword)
        self.assertEqual(query, '"test"')

    def test_build_query_multiple_keywords(self):
        keywords = ['foo', 'bar', 'baz']
        query = build_database.build_query(keywords)
        self.assertEqual(query, '"foo" OR "bar" OR "baz"')

    def test_build_query_phrases(self):
        keywords = ['foo', 'bar baz']
        query = build_database.build_query(keywords)
        self.assertEqual(query, '"foo" OR "bar baz"')

    if __name__ == '__main__':
        unittest.main()
