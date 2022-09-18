from forecaster.utils import load_stock_prices, plot_predictions
from unittest.mock import Mock
import unittest
import numpy


class ForecasterUtilsTests(unittest.TestCase):
    def test_load_stock_prices(self):
        actual_prices = load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 11:30:00-04:00', 5)
        expected_prices = numpy.array([40.67789841, 41.95000076, 41.72999954, 41.92990112, 42.86299896])
        self.assertTrue(numpy.allclose(actual_prices, expected_prices))

    def test_load_stock_prices_invalid_timestamp(self):
        expected_prices = numpy.array([])

        actual_prices = load_stock_prices('mock_data/forecaster/GME.csv', '2022-08-16 16:01:00-04:00', 5)
        self.assertTrue(numpy.allclose(actual_prices, expected_prices))

        actual_prices = load_stock_prices('mock_data/forecaster/GME.csv', 'BLANK', 5)
        self.assertTrue(numpy.allclose(actual_prices, expected_prices))

    def test_plot_predictions(self):
        mock_pyplot = Mock()
        mock_pyplot.savefig = Mock()
        mock_os = Mock()
        mock_os.path = Mock()
        mock_os.path.isdir = Mock()
        mock_os.makedirs = Mock()
        mock_path = 'mock/dir'
        mock_ticker = 'MOCK'

        mock_os.path.isdir.return_value = True
        plot_predictions(Mock(), Mock(), mock_ticker, mock_pyplot, mock_path, mock_os)
        mock_os.makedirs.assert_not_called()
        mock_pyplot.savefig.assert_called_with(f'{mock_path}/{mock_ticker}.png')

        mock_os.path.isdir.return_value = False
        plot_predictions(Mock(), Mock(), mock_ticker, mock_pyplot, mock_path, mock_os)
        mock_os.makedirs.assert_called_with(mock_path)
        mock_pyplot.savefig.assert_called_with(f'{mock_path}/{mock_ticker}.png')
