from sentiment.scaler import ScoreScaler
from unittest.mock import Mock, call
import unittest
import numpy


class ScoreScalerTests(unittest.TestCase):
    def test_fit_transform(self):
        ss = ScoreScaler()
        ss.pos_scaler = Mock()
        ss.neg_scaler = Mock()

        ss.fit_transform([-10, -5, 0, 5, 10])
        self.assertTrue(numpy.array_equal([[5], [10], [0]], ss.pos_scaler.fit_transform.call_args[0][0]))
        self.assertTrue(numpy.array_equal([[-10], [-5], [0]], ss.neg_scaler.fit_transform.call_args[0][0]))

    def test_transform(self):
        ss = ScoreScaler()
        ss.fit_transform([-10, 10, 1000])
        self.assertEqual(ss.transform(-10), -2)
        self.assertEqual(ss.transform(10), 1.01)
        self.assertEqual(ss.transform(1000), 2)
        self.assertEqual(ss.transform(0), 1)
