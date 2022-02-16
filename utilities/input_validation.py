from datetime import date


def check_float(n, function_name):
    error_msg = f'{function_name}: \'{n}\' is not a floating-point number'
    try:
        float(n)
    except ValueError as error:
        raise TypeError(error_msg) from error


def check_bounds(n, lower, upper, msg):
    if n < lower or n > upper:
        raise ValueError(msg)


def check_positive_int(n, msg):
    if type(n) != int or n <= 0:
        raise TypeError(msg)


def check_nonempty_string(s, function_name):
    error_msg = f'{function_name}: \'{s}\' is not a nonempty string'

    if type(s) != str or len(s) <= 0:
        raise TypeError(error_msg)


def check_isoformat_date_string(s, function_name):
    error_msg = f'{function_name}: \'{s}\' is not an ISO format date string'
    if type(s) != str:
        raise TypeError(error_msg)

    try:
        date.fromisoformat(s)
    except ValueError:
        raise TypeError(error_msg)
