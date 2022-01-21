from forecaster import forecaster
import unittest


class ForecasterTests(unittest.TestCase):
    def test_extract_stock_prices(self):
        expected = [336.320007, 334.75, 329.01001, 316.380005, 313.880005, 313.649994]
        actual = forecaster.extract_stock_prices('__test/MOCK')
        self.assertTrue((expected == actual).all())

    def test_extract_stock_images_csv_not_found(self):
        try:
            forecaster.extract_stock_prices('TEST')
            self.fail()
        except FileNotFoundError as error:
            self.assertEqual(str(error), 'No price history found for TEST')

    def test_calculate_percent_error(self):
        self.assertEqual(1, forecaster.calculate_percent_error(99, 100))
        self.assertEqual(5, forecaster.calculate_percent_error(95, 100))

    def test_calculate_percent_error_non_numeric_args(self):
        expected, actual = 'fish', 'chips'
        try:
            forecaster.calculate_percent_error(expected, 2)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), f'calculate_percent_error: \'{expected}\' is not a real number')

        try:
            forecaster.calculate_percent_error(2, actual)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), f'calculate_percent_error: \'{actual}\' is not a real number')
