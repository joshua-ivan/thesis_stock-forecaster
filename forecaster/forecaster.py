from utilities.input_validation import check_float
from datetime import datetime
import utilities.date_util as date_util
import config
import pmdarima
import arch
import pandas
import numpy
import os

PRICES_DIR = 'prices'


def forecast(history):
    arima_model = pmdarima.auto_arima(history)
    arima_residuals = arima_model.arima_res_.resid
    garch = arch.arch_model(arima_residuals, p=1, q=1)
    garch_model = garch.fit()

    predicted_mean = arima_model.predict(n_periods=1)[0]
    predicted_residual = garch_model.forecast(horizon=1, reindex=False)

    predicted_variance = predicted_residual.mean['h.1'].iloc[-1]
    return predicted_mean + predicted_variance


def read_stock_prices(directory, ticker):
    file = f'{directory}/{ticker}.csv'
    if not os.path.exists(file):
        raise FileNotFoundError(f'No price history found for {ticker}')

    return pandas.read_csv(f'{directory}/{ticker}.csv', usecols=['Date', 'Adj Close'], index_col='Date')


def fill_missing_dates(dataframe):
    dataframe.index = pandas.to_datetime(dataframe.index, format='%Y-%m-%d')
    return dataframe.resample('1D').ffill()


def calculate_percent_error(expected, actual):
    check_float(expected, f'calculate_percent_error: \'{expected}\' is not a real number')
    check_float(actual, f'calculate_percent_error: \'{actual}\' is not a real number')

    return ((actual - expected) / actual) * 100


def evaluate_forecaster():
    output_frame = pandas.DataFrame(columns=['Ticker', 'Expected', 'Actual', 'Error'])
    for stock in config.stocks:
        ticker = stock['ticker']

        price_history = read_stock_prices(PRICES_DIR, ticker)
        expected = forecast(price_history['Adj Close'].to_numpy())
        actual = price_history[-1]
        error = calculate_percent_error(expected, actual)
        output_frame = output_frame.append({
            'Ticker': ticker,
            'Expected': expected,
            'Actual': actual,
            'Error': error},
            ignore_index=True)

    errors = output_frame['Error'].to_numpy()
    print(f'Mean Squared Percent Error: {numpy.square(errors).mean()}\n')
    output_frame.to_csv('forecaster_evaluation.csv')


def price_history_bin_to_series(history, _bin):
    start = datetime.fromisoformat(_bin['start'])
    end = datetime.fromisoformat(_bin['end'])
    return history[(history.index >= start) & (history.index <= end)]['Adj Close'].to_numpy()


def execute():
    columns = date_util.generate_aggregate_columns(config.end_date, config.raw_data_interval_days, config.bin_size)
    bins = date_util.generate_bin_boundaries(config.end_date, config.raw_data_interval_days, config.bin_size)
    output_frame = pandas.DataFrame(columns=columns)

    for stock in config.stocks:
        ticker = stock['ticker']
        price_history = fill_missing_dates(read_stock_prices(PRICES_DIR, ticker))

        projections = [ticker]
        for _bin in bins:
            bin_history = price_history_bin_to_series(price_history, _bin)
            projections.append((forecast(bin_history) / bin_history[-1]) - 1)

        output_frame.loc[len(output_frame)] = projections

    output_frame.to_csv('projection.csv', index=False)
