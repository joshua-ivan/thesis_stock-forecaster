from sentiment import clean_posts
import unittest


class CleanPostsTests(unittest.TestCase):
    def test_strip_nonalphanumeric(self):
        self.assertEqual('abc123 ', clean_posts.strip_nonalphanumeric_characters('abc123 '))
        self.assertEqual('test \n', clean_posts.strip_nonalphanumeric_characters('test \n'))
        self.assertEqual('test \n\n\n', clean_posts.strip_nonalphanumeric_characters('test \n\n\n'))
        self.assertEqual('https abc123 ', clean_posts.strip_nonalphanumeric_characters('https://abc123 '))
        self.assertEqual(' test ', clean_posts.strip_nonalphanumeric_characters('(test)'))
