from datetime import date


def check_float(n, msg):
    try:
        float(n)
    except ValueError:
        raise TypeError(msg)


def check_bounds(n, lower, upper, msg):
    if n < lower or n > upper:
        raise ValueError(msg)


def check_positive_int(n, msg):
    if type(n) != int or n <= 0:
        raise TypeError(msg)


def check_nonempty_string(s, msg):
    if type(s) != str or len(s) <= 0:
        raise TypeError(msg)


def check_isoformat_date_string(s, msg):
    if type(s) != str:
        raise TypeError(msg)

    try:
        date.fromisoformat(s)
    except ValueError:
        raise TypeError(msg)
