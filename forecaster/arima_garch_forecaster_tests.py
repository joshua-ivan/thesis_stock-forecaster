from forecaster.arima_garch_forecaster import ARIMAGARCHForecaster
from datetime import datetime
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
        agf = ARIMAGARCHForecaster()
        agf.evaluate_model()
        pass

    def test_generate_forecast(self):
        start_time = datetime.now()
        agf = ARIMAGARCHForecaster()
        print(agf.generate_forecast('BBBY', '2022-09-07 09:30:00-04:00', 360))
        print(agf.generate_forecast('BBBY', '2022-09-07 09:31:00-04:00', 360))
        print(agf.generate_forecast('BBBY', '2022-09-07 09:32:00-04:00', 360))
        end_time = datetime.now()
        print(end_time - start_time)
