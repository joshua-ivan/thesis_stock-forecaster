from forecaster.lstm_forecaster import LSTMForecaster
from forecaster.utils import load_stock_prices
from unittest.mock import Mock
from datetime import datetime
import unittest
import numpy


class LSTMForecasterTests(unittest.TestCase):
    def test_generate_training_set(self):
        lstm_fcr = LSTMForecaster()
        training_data = load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:30:00-04:00', 5)
        training_set = lstm_fcr.generate_training_set(training_data, 2)
        expected_feature_set = \
            numpy.array([
                numpy.array([
                    numpy.array([0.]),
                    numpy.array([0.58217108])
                ]),
                numpy.array([
                    numpy.array([0.58217108]),
                    numpy.array([0.48148866])
                ]),
                numpy.array([
                    numpy.array([0.48148866]),
                    numpy.array([0.57297259])
                ])
            ])
        expected_labels = [0.48148866, 0.57297259, 1.]
        for i in range(0, len(expected_feature_set)):
            self.assertTrue(numpy.allclose(expected_feature_set[i], training_set.feature_set[i]))
        self.assertTrue(numpy.allclose(expected_labels, training_set.labels))

    def test_generate_test_set(self):
        lstm_fcr = LSTMForecaster()
        training_data = load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:27:00-04:00', 7)
        lstm_fcr.scaler.fit_transform(training_data.reshape(-1, 1))
        test_data = load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:30:00-04:00', 3)
        test_set = lstm_fcr.generate_test_set(training_data, test_data, 3)
        expected_test_set = \
            numpy.array([
                numpy.array([
                    numpy.array([0.14368477]),
                    numpy.array([0.46601954]),
                    numpy.array([1.])
                ]),
                numpy.array([
                    numpy.array([0.46601954]),
                    numpy.array([1.]),
                    numpy.array([0.90765181])
                ]),
                numpy.array([
                    numpy.array([1.]),
                    numpy.array([0.90765181]),
                    numpy.array([0.99156293])
                ])
            ])
        for i in range(0, len(expected_test_set)):
            self.assertTrue(numpy.allclose(expected_test_set[i], test_set[i]))
        pass

    def test_generate_test_set_no_test_data_one_set(self):
        lstm_fcr = LSTMForecaster()
        training_data = load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:27:00-04:00', 5)
        lstm_fcr.scaler.fit_transform(training_data.reshape(-1, 1))
        test_data = numpy.array([])
        test_set = lstm_fcr.generate_test_set(training_data, test_data, 5)
        expected_test_set = \
            numpy.array([
                numpy.array([
                    numpy.array([0.01460834]),
                    numpy.array([0.]),
                    numpy.array([0.05990827]),
                    numpy.array([0.41377825]),
                    numpy.array([1.])
                ])
            ])
        for i in range(0, len(expected_test_set)):
            self.assertTrue(numpy.allclose(expected_test_set[i], test_set[i]))

    def test_evaluate_model(self):
        # lstm_fcr = LSTMForecaster()
        # lstm_fcr.evaluate_model('BBBY', '2022-09-12 15:29:00-04:00', 360, '2022-09-12 15:59:00-04:00', 30, 60)
        pass

    def test_generate_forecast(self):
        lstm_fcr = LSTMForecaster()
        start_time = datetime.now()
        print(lstm_fcr.generate_forecast('BBBY', '2022-09-16 13:30:00-04:00', 360, 60))
        print(lstm_fcr.generate_forecast('BBBY', '2022-09-16 13:35:00-04:00', 360, 60))
        print(lstm_fcr.generate_forecast('BBBY', '2022-09-16 13:40:00-04:00', 360, 60))
        print(lstm_fcr.generate_forecast('BBBY', '2022-09-16 13:45:00-04:00', 360, 60))
        print(lstm_fcr.generate_forecast('BBBY', '2022-09-16 13:50:00-04:00', 360, 60))
        end_time = datetime.now()
        print(end_time - start_time)
