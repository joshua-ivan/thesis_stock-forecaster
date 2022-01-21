def check_float(n, msg):
    try:
        float(n)
    except ValueError:
        raise TypeError(msg)


def check_bounds(n, lower, upper, msg):
    if n < lower or n > upper:
        raise ValueError(msg)
