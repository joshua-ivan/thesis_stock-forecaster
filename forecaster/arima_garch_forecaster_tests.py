from forecaster.arima_garch_forecaster import ARIMAGARCHForecaster
import unittest
import numpy


class ARIMAGARCHForecasterTests(unittest.TestCase):
    def test_generate_test_set(self):
        agf = ARIMAGARCHForecaster()
        expected = [
            [1, 2, 3],
            [2, 3, 4]
        ]
        numpy.testing.assert_array_equal(expected, agf.generate_test_set([1, 2, 3], [4, 5]))

    def test_evaluate_model(self):
        # agf = ARIMAGARCHForecaster()
        # agf.evaluate_model()
        pass
