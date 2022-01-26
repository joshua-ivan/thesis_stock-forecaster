from sentiment.filter_master_dictionary import condense_dictionary, generate_filename
import unittest
import pandas


class FilterMasterDictionaryTests(unittest.TestCase):

    def test_condense_dictionary(self):
        test_dict = pandas.read_csv('mock_data/sentiment/dictionary.csv')
        filtered_dict = condense_dictionary(test_dict)

        expected_columns = ['Word', 'Negative', 'Positive']
        self.assertTrue((filtered_dict.columns.to_numpy() == expected_columns).all())
        expected_words = ['GREATEST', 'PROSECUTE', 'PROSPERED', 'PROTEST']
        self.assertTrue((filtered_dict['Word'].to_numpy() == expected_words).all())
        expected_negatives = [0, 1, 0, 1]
        self.assertTrue((filtered_dict['Negative'].to_numpy() == expected_negatives).all())
        expected_positives = [1, 0, 1, 0]
        self.assertTrue((filtered_dict['Positive'].to_numpy() == expected_positives).all())

    def test_condense_dictionary_type_check(self):
        try:
            condense_dictionary('foo bar baz')
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), 'condensed_dictionary expects a pandas DataFrame')

    def test_generate_filename(self):
        self.assertEqual(generate_filename('test.csv'), 'test__condensed.csv')

    def test_generate_filename_type_check(self):
        try:
            generate_filename(303)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), 'generate_filename expects a string')
