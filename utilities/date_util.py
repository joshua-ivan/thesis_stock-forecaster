from utilities.input_validation import check_positive_int, check_isoformat_date_string, check_nonempty_string
from collections import deque
from datetime import date, timedelta


def generate_aggregate_columns(end_date, timeframe_days, interval):
    check_date_utility_inputs('generate_aggregate_columns', end_date, timeframe_days, interval)

    current_date = date.fromisoformat(end_date)
    columns = deque([end_date])
    days_remaining = timeframe_days - interval

    while int(days_remaining / interval) > 0:
        current_date = current_date - timedelta(days=interval)
        columns.appendleft(str(current_date.isoformat()))
        days_remaining = days_remaining - interval
    columns.appendleft('Ticker')

    return list(columns)


def generate_bin_boundaries(end_date, timeframe_days, interval):
    check_date_utility_inputs('generate_bin_boundaries', end_date, timeframe_days, interval)

    bin_boundaries = deque()
    bin_end = date.fromisoformat(end_date)
    days_remaining = timeframe_days

    while days_remaining > 0:
        delta = interval - 1
        if (days_remaining - interval) >= interval:
            days_remaining = days_remaining - interval
        else:
            delta = days_remaining - 1
            days_remaining = 0

        bin_start = bin_end - timedelta(days=delta)
        bin_boundaries.appendleft({'start': bin_start.isoformat(), 'end': bin_end.isoformat()})

        bin_end = bin_start - timedelta(days=1)

    return list(bin_boundaries)


def check_date_utility_inputs(function_name, end_date, timeframe_days, interval):
    check_isoformat_date_string(
        end_date, f'{function_name}: \'{end_date}\' (end_date) is not an ISO format date string')
    check_positive_int(
        timeframe_days, f'{function_name}: \'{timeframe_days}\' (timeframe_days) is not a positive integer')
    check_positive_int(interval, f'{function_name}: \'{interval}\' (interval) is not a positive integer')
