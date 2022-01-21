from trader.trader import zero_one_normalization
import unittest


class TraderTests(unittest.TestCase):
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
            self.assertEqual(str(error), f'zero_one_normalization: \'{minimum}\' is not a real number')

        try:
            zero_one_normalization(-1, maximum)(2)
            self.fail()
        except TypeError as error:
            self.assertEqual(str(error), f'zero_one_normalization: \'{maximum}\' is not a real number')

    def test_zero_one_normalization_out_of_bounds(self):
        minimum, maximum = 0, 10

        try:
            zero_one_normalization(minimum, maximum)(-1)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error),
                             f'zero_one_normalization: \'-1\' is out of bounds [{minimum}, {maximum}]')

        try:
            zero_one_normalization(minimum, maximum)(11)
            self.fail()
        except ValueError as error:
            self.assertEqual(str(error),
                             f'zero_one_normalization: \'11\' is out of bounds [{minimum}, {maximum}]')
