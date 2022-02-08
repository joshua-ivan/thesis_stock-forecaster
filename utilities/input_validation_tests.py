from utilities import input_validation
import unittest


class InputValidationTests(unittest.TestCase):
    def test_check_nonempty_string(self):
        with self.assertRaises(TypeError) as none_assertion:
            input_validation.check_nonempty_string(None, 'None check')
        self.assertEqual(str(none_assertion.exception), 'None check')

        with self.assertRaises(TypeError) as non_string_assertion:
            input_validation.check_nonempty_string(60, 'Non-string check')
        self.assertEqual(str(non_string_assertion.exception), 'Non-string check')

        with self.assertRaises(TypeError) as empty_string_assertion:
            input_validation.check_nonempty_string('', 'Empty string check')
        self.assertEqual(str(empty_string_assertion.exception), 'Empty string check')
