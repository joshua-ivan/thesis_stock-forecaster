from forecaster import forecaster
import unittest


class ForecasterTests(unittest.TestCase):
    def test_extract_stock_prices(self):
        expected = [336.320007, 334.75, 329.01001, 316.380005, 313.880005, 313.649994]
        actual = forecaster.extract_stock_prices('__test/MOCK')
        self.assertTrue((expected == actual).all())
