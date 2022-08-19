from forecaster.lstm_forecaster import LSTMForecaster
from unittest.mock import Mock
import unittest
import numpy


class LSTMForecasterTests(unittest.TestCase):
    def test_load_stock_prices(self):
        lstm_fcr = LSTMForecaster()
        actual_prices = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:30:00-04:00', 5)
        expected_prices = numpy.array([40.67789841, 41.95000076, 41.72999954, 41.92990112, 42.86299896])
        self.assertTrue(numpy.allclose(actual_prices, expected_prices))

    def test_load_stock_prices_invalid_timestamp(self):
        lstm_fcr = LSTMForecaster()
        expected_prices = numpy.array([])

        actual_prices = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 16:01:00-04:00', 5)
        self.assertTrue(numpy.allclose(actual_prices, expected_prices))

        actual_prices = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', 'BLANK', 5)
        self.assertTrue(numpy.allclose(actual_prices, expected_prices))

    def test_generate_training_set(self):
        lstm_fcr = LSTMForecaster()
        training_data = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:30:00-04:00', 5)
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

    def test_compile_model(self):
        lstm_fcr = LSTMForecaster()
        training_data = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:30:00-04:00', 5)
        training_set = lstm_fcr.generate_training_set(training_data, 2)
        mock_isdir = Mock()
        mock_load_model = Mock()
        mock_model_builder = Mock()
        mock_file_path = 'mock/path'

        mock_isdir.return_value = False
        lstm_fcr.compile_model(
            mock_isdir, mock_load_model, mock_model_builder, mock_file_path, training_set.feature_set)
        mock_load_model.assert_not_called()

        mock_isdir.return_value = True
        lstm_fcr.compile_model(
            mock_isdir, mock_load_model, mock_model_builder, mock_file_path, training_set.feature_set)
        mock_load_model.assert_called_with(mock_file_path)

    def test_fit_model(self):
        lstm_fcr = LSTMForecaster()
        mock_model = Mock()
        mock_model.save = Mock()
        mock_file_path = 'mock/path'
        mock_data = Mock()
        lstm_fcr.fit_model(mock_model, mock_file_path, mock_data)
        mock_model.save.assert_called_with(mock_file_path)

    def test_generate_test_set(self):
        lstm_fcr = LSTMForecaster()
        training_data = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:27:00-04:00', 7)
        lstm_fcr.scaler.fit_transform(training_data.reshape(-1, 1))
        test_data = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:30:00-04:00', 3)
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
        training_data = lstm_fcr.load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:27:00-04:00', 5)
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

    def test_generate_predictions(self):
        lstm_fcr = LSTMForecaster()

        lstm_fcr.scaler = Mock()
        mock_pyplot = Mock()
        mock_pyplot.savefig = Mock()
        mock_os = Mock()
        mock_os.path = Mock()
        mock_os.path.isdir = Mock()
        mock_os.makedirs = Mock()
        mock_path = 'mock/dir'
        mock_ticker = 'MOCK'

        mock_os.path.isdir.return_value = True
        lstm_fcr.test_predictions(Mock(), Mock(), Mock(), mock_pyplot, mock_os, mock_path, mock_ticker)
        mock_os.makedirs.assert_not_called()
        mock_pyplot.savefig.assert_called_with(f'{mock_path}/{mock_ticker}.png')

        mock_os.path.isdir.return_value = False
        lstm_fcr.test_predictions(Mock(), Mock(), Mock(), mock_pyplot, mock_os, mock_path, mock_ticker)
        mock_os.makedirs.assert_called_with(mock_path)
        mock_pyplot.savefig.assert_called_with(f'{mock_path}/{mock_ticker}.png')

    def test_evaluate_model(self):
        # lstm_fcr = LSTMForecaster()
        # lstm_fcr.evaluate_model('GME', '2022-08-15 15:29:00-04:00', 360, '2022-08-15 15:59:00-04:00', 30, 60)
        pass

    def test_generate_forecast(self):
        # lstm_fcr = LSTMForecaster()
        # print(lstm_fcr.generate_forecast('GME', '2022-08-15 15:30:00-04:00', 360, 60))
        pass
