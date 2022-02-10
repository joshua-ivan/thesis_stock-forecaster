from utilities.input_validation import check_float, check_bounds
from utilities.pandas_util import extract_cell
import utilities.date_util as date_util
import pandas
import config


def zero_one_normalization(minimum, maximum):
    def normalize(n):
        check_bounds(n, minimum, maximum, f'zero_one_normalization: \'{n}\' is out of bounds [{minimum}, {maximum}]')

        return (n - minimum) / (maximum - minimum)

    check_float(minimum, f'zero_one_normalization: \'{minimum}\' is not a real number')
    check_float(maximum, f'zero_one_normalization: \'{maximum}\' is not a real number')

    return normalize


def polarity_preserving_normalization(filename, column):
    data = pandas.read_csv(filename)
    positive = data[data[column] > 0].copy()
    negative = data[data[column] <= 0].copy()

    positive[column] = positive[column].apply(
        zero_one_normalization(
            0.0,
            positive[column].max()))

    negative[column] = negative[column].apply(
        zero_one_normalization(
            negative[column].min(),
            0.0))
    negative[column] = negative[column] - 1

    return positive.merge(negative, how='outer')


def trade_decision(sentiment, projection):
    minimum, maximum = -1.0, 1.0
    check_bounds(
        sentiment, minimum, maximum, f'trade_decision: \'{sentiment}\' is out of bounds [{minimum}, {maximum}]')
    check_bounds(
        projection, minimum, maximum, f'trade_decision: \'{projection}\' is out of bounds [{minimum}, {maximum}]')

    if sentiment >= config.thresholds['positive'] and projection <= config.thresholds['negative']:
        return 'SELL'
    elif sentiment <= config.thresholds['negative'] and projection >= config.thresholds['positive']:
        return 'BUY'
    return 'HOLD'


def execute():
    decisions_dataframe = pandas.DataFrame(columns=['Ticker'])
    for stock in config.stocks:
        decisions_dataframe.loc[len(decisions_dataframe)] = stock['ticker']

    dates = date_util.generate_aggregate_columns(config.end_date, config.raw_data_interval_days, config.bin_size)[1:]
    for date in dates:
        sentiments = polarity_preserving_normalization('sentiment.csv', date)
        projections = polarity_preserving_normalization('projection.csv', date)

        decisions_column = []
        for stock in config.stocks:
            stock_sentiment = extract_cell(sentiments, 'Ticker', stock['ticker'], date)
            stock_sentiment = 0.0 if stock_sentiment is None else stock_sentiment
            stock_projection = extract_cell(projections, 'Ticker', stock['ticker'], date)
            stock_projection = 0.0 if stock_projection is None else stock_projection
            decisions_column.append(trade_decision(stock_sentiment, stock_projection))

        decisions_dataframe.insert(len(decisions_dataframe.columns), column=date, value=decisions_column)

    decisions_dataframe.to_csv('decision.csv', index=False)
