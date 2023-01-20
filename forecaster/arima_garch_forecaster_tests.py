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
        # agf = ARIMAGARCHForecaster()
        # agf.evaluate_model()
        pass

    def test_generate_forecast(self):
        agf = ARIMAGARCHForecaster()
        start_time = datetime.now()
        print(agf.generate_forecast('BBBY', '2022-09-12 14:30:00-04:00', 60))
        print(agf.generate_forecast('BBBY', '2022-09-12 14:35:00-04:00', 60))
        print(agf.generate_forecast('BBBY', '2022-09-12 14:40:00-04:00', 60))
        print(agf.generate_forecast('BBBY', '2022-09-12 14:45:00-04:00', 60))
        print(agf.generate_forecast('BBBY', '2022-09-12 14:50:00-04:00', 60))
        end_time = datetime.now()
        print(end_time - start_time)
