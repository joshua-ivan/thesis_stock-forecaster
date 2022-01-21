from utilities.input_validation import check_float, check_bounds


def zero_one_normalization(minimum, maximum):
    def normalize(n):
        check_bounds(n, minimum, maximum, f'zero_one_normalization: \'{n}\' is out of bounds [{minimum}, {maximum}]')

        return (n - minimum) / (maximum - minimum)

    check_float(minimum, f'zero_one_normalization: \'{minimum}\' is not a real number')
    check_float(maximum, f'zero_one_normalization: \'{maximum}\' is not a real number')

    return normalize
