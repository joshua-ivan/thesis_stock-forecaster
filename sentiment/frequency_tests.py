from sentiment.frequency import FrequencyAnalyzer
import unittest
import os


class FrequencyAnalyzerTests(unittest.TestCase):
    def test_process_posts(self):
        fa = FrequencyAnalyzer()
        base_dir = 'mock_data/sentiment/frequency'
        words = fa.process_posts(base_dir, os.listdir(base_dir))
        expected = {'comment': 4, 'caps': 1, 'submission': 1, 'downvote': 1}
        self.assertEqual(expected, words)

    def test_merge_frequency_dicts(self):
        fa = FrequencyAnalyzer()
        dict_a = {'comment': 500, 'https': 250}
        dict_b = {'comment': 500, 'img': 250}
        dict_c = {'https': 250, 'img': 250}
        expected = {'comment': 1000, 'https': 500, 'img': 500}
        self.assertEqual(expected, fa.merge_frequency_dicts([dict_a, dict_b, dict_c]))
        self.assertEqual(expected, fa.merge_frequency_dicts([None, dict_a, dict_b, dict_c]))
        self.assertEqual(expected, fa.merge_frequency_dicts([dict_a, None, dict_b, dict_c]))
        self.assertEqual(expected, fa.merge_frequency_dicts([dict_a, dict_b, None, dict_c]))
        self.assertEqual(expected, fa.merge_frequency_dicts([dict_a, dict_b, dict_c, None]))

    def test_merge_frequency_dicts_no_dicts(self):
        fa = FrequencyAnalyzer()
        self.assertEqual(fa.merge_frequency_dicts(None), {})
        self.assertEqual(fa.merge_frequency_dicts([]), {})
        self.assertEqual(fa.merge_frequency_dicts([None]), {})

    def test_merge_frequency_dicts_one_dict(self):
        fa = FrequencyAnalyzer()
        expected = {'mock': 500, 'test': 500}
        self.assertEqual(fa.merge_frequency_dicts([expected]), expected)
        self.assertEqual(fa.merge_frequency_dicts([None, expected]), expected)
        self.assertEqual(fa.merge_frequency_dicts([expected, None]), expected)

    def test_split_post_lists(self):
        fa = FrequencyAnalyzer()
        expected = [['foo'], ['bar']]
        self.assertEqual(fa.split_post_list(['foo', 'bar'], 2), expected)
        expected = [['foo'], ['bar'], ['fee', 'baz']]
        self.assertEqual(fa.split_post_list(['foo', 'bar', 'fee', 'baz'], 3), expected)

    def test_extract_word_frequency(self):
        fa = FrequencyAnalyzer()
        fa.extract_word_frequency()
