from utilities.input_validation import check_positive_int, check_isoformat_date_string, check_nonempty_string
from collections import deque
from datetime import datetime, date, timedelta


def generate_aggregate_columns(end_date, timeframe_days, interval):
    check_date_bin_utility_inputs('generate_aggregate_columns', end_date, timeframe_days, interval)

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
    check_date_bin_utility_inputs('generate_bin_boundaries', end_date, timeframe_days, interval)

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


def check_date_bin_utility_inputs(function_name, end_date, timeframe_days, interval):
    check_isoformat_date_string(end_date, function_name)
    check_positive_int(
        timeframe_days, f'{function_name}: \'{timeframe_days}\' (timeframe_days) is not a positive integer')
    check_positive_int(interval, f'{function_name}: \'{interval}\' (interval) is not a positive integer')


def get_stock_action_date(history, raw_date):
    action_date = date.fromisoformat(raw_date)
    while len(history[history['Date'] == action_date.isoformat()]) <= 0:
        action_date = action_date - timedelta(days=1)
    return action_date.isoformat()


def datetime_string_to_posix(datetime_string):
    dt = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S-04:00')
    return dt.replace(hour=(dt.hour + 4)).timestamp()


def datetime_string_to_yfinance_dates(datetime_string):
    dt = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S-04:00')
    start_date = dt.replace(day=(dt.day - 3)).strftime('%Y-%m-%d')
    end_date = dt.replace(day=(dt.day + 1)).strftime('%Y-%m-%d')
    return start_date, end_date
