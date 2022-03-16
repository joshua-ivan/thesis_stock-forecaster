from utilities import input_validation
import unittest


class InputValidationTests(unittest.TestCase):
    def test_check_nonempty_string(self):
        def get_test_error_message(s):
            return f'test_check_nonempty_string: \'{s}\' is not a nonempty string'

        with self.assertRaises(TypeError) as none_assertion:
            input_validation.check_nonempty_string(None, 'test_check_nonempty_string')
        self.assertEqual(str(none_assertion.exception), get_test_error_message(None))

        with self.assertRaises(TypeError) as non_string_assertion:
            input_validation.check_nonempty_string(60, 'test_check_nonempty_string')
        self.assertEqual(str(non_string_assertion.exception), get_test_error_message(60))

        with self.assertRaises(TypeError) as empty_string_assertion:
            input_validation.check_nonempty_string('', 'test_check_nonempty_string')
        self.assertEqual(str(empty_string_assertion.exception), get_test_error_message(''))

    def test_check_float(self):
        with self.assertRaises(TypeError):
            input_validation.check_float(None, 'test_check_float')

        with self.assertRaises(TypeError):
            input_validation.check_float('fish', 'test_check_float')

    def test_check_positive_int(self):
        with self.assertRaises(TypeError):
            input_validation.check_positive_int(None, 'test_check_positive_int')

        with self.assertRaises(TypeError):
            input_validation.check_positive_int(-1, 'test_check_positive_int')
