from utilities.pandas_util import extract_cell
import unittest
import pandas


class PandasUtilTests(unittest.TestCase):
    MOCKS_DIR = 'mock_data/utilities'

    def test_extract_cell(self):
        data = pandas.read_csv(f'{self.MOCKS_DIR}/extract_cell.csv')
        self.assertEqual(extract_cell(data, 'Food', 'Beef', 'Drink'), 'Wine')
        self.assertEqual(extract_cell(data, 'Drink', 'Rum', 'Food'), 'Fish')

    def test_extract_cell_no_match(self):
        data = pandas.read_csv(f'{self.MOCKS_DIR}/extract_cell.csv')
        self.assertEqual(extract_cell(data, 'Food', 'Chicken', 'Drink'), None)

