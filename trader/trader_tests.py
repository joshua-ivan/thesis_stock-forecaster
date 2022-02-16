import numpy as np

from trader.trader import zero_one_normalization, polarity_preserving_normalization, trade_decision
from config import thresholds
import unittest


class TraderTests(unittest.TestCase):
    MOCKS_DIR = 'mock_data/trader'

    def test_zero_one_normalization(self):
        minimum, maximum = 0, 10
        self.assertEqual(zero_one_normalization(minimum, maximum)(4), .4)
        self.assertEqual(zero_one_normalization(minimum, maximum)(0), 0)
        self.assertEqual(zero_one_normalization(minimum, maximum)(10), 1)

    def test_zero_one_normalization_non_number(self):
        minimum, maximum = 'fish', 'chips'

        try:
            zero_one_normalization(minimum, -1)(2)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), f'zero_one_normalization: \'{minimum}\' is not a floating-point number')

        try:
            zero_one_normalization(-1, maximum)(2)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), f'zero_one_normalization: \'{maximum}\' is not a floating-point number')

    def test_zero_one_normalization_out_of_bounds(self):
        minimum, maximum = 0, 10

        try:
            zero_one_normalization(minimum, maximum)(-1)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error), f'zero_one_normalization: \'-1\' is out of bounds [{minimum}, {maximum}]')

        try:
            zero_one_normalization(minimum, maximum)(11)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error), f'zero_one_normalization: \'11\' is out of bounds [{minimum}, {maximum}]')

    def test_polarity_preserving_normalization(self):
        expected = [0.05, 1.00, 0.90, -0.10, -1.00, -0.30]
        actual = polarity_preserving_normalization(
            f'{self.MOCKS_DIR}/polarity_preserving_normalization.csv', 'Value')['Value'].to_numpy()
        round_to_hundredths = np.vectorize(lambda x: round(x, 2))
        self.assertTrue((expected == round_to_hundredths(actual)).all())

    def test_trade_decision(self):
        self.assertEqual(trade_decision(1.0, -1.0), 'SELL')
        self.assertEqual(trade_decision(thresholds['positive'], thresholds['negative']), 'SELL')
        self.assertEqual(trade_decision(0.75, -0.75), 'SELL')

        self.assertEqual(trade_decision(-1.0, 1.0), 'BUY')
        self.assertEqual(trade_decision(thresholds['negative'], thresholds['positive']), 'BUY')
        self.assertEqual(trade_decision(-0.75, 0.75), 'BUY')

        self.assertEqual(trade_decision(0.0, 0.0), 'HOLD')
        self.assertEqual(trade_decision(thresholds['positive'] - 0.01, thresholds['negative'] + 0.01), 'HOLD')
        self.assertEqual(trade_decision(thresholds['negative'] + 0.01, thresholds['positive'] - 0.01), 'HOLD')

    def test_trade_decision_out_of_bounds(self):
        minimum, maximum = -1.0, 1.0

        score = 2.0
        try:
            trade_decision(score, 0.0)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error), f'trade_decision: \'{score}\' is out of bounds [{minimum}, {maximum}]')
        try:
            trade_decision(0.0, score)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error), f'trade_decision: \'{score}\' is out of bounds [{minimum}, {maximum}]')

        score = -2.0
        try:
            trade_decision(score, 0.0)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error), f'trade_decision: \'{score}\' is out of bounds [{minimum}, {maximum}]')
        try:
            trade_decision(0.0, score)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error), f'trade_decision: \'{score}\' is out of bounds [{minimum}, {maximum}]')
