from config import stocks
from utilities.input_validation import check_float
import pmdarima
import arch
import pandas
import numpy
import os


def forecast(history):
    arima_model = pmdarima.auto_arima(history)
    arima_residuals = arima_model.arima_res_.resid
    garch = arch.arch_model(arima_residuals, p=1, q=1)
    garch_model = garch.fit()

    predicted_mean = arima_model.predict(n_periods=1)[0]
    predicted_residual = garch_model.forecast(horizon=1, reindex=False)

    predicted_variance = predicted_residual.mean['h.1'].iloc[-1]
    return predicted_mean + predicted_variance


def extract_stock_prices(ticker):
    file = f'prices/{ticker}.csv'
    if not os.path.exists(file):
        raise FileNotFoundError(f'No price history found for {ticker}')

    price_history = pandas.read_csv(f'prices/{ticker}.csv', usecols=['Date', 'Adj Close'])
    return price_history['Adj Close'].to_numpy()


def calculate_percent_error(expected, actual):
    check_float(expected, f'calculate_percent_error: \'{expected}\' is not a real number')
    check_float(actual, f'calculate_percent_error: \'{actual}\' is not a real number')

    return ((actual - expected) / actual) * 100


def evaluate_forecaster():
    output_frame = pandas.DataFrame(columns=['Ticker', 'Expected', 'Actual', 'Error'])
    for stock in stocks:
        ticker = stock['ticker']

        price_history = extract_stock_prices(ticker)
        expected = forecast(price_history[0:-1])
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


def execute():
    output_frame = pandas.DataFrame(columns=['Ticker', 'Projection', 'Profit/Loss'])
    for stock in stocks:
        ticker = stock['ticker']

        price_history = extract_stock_prices(ticker)
        projection = forecast(price_history)
        output_frame = output_frame.append({
            'Ticker': ticker,
            'Projection': projection,
            'Profit/Loss': projection / price_history[-1]},
            ignore_index=True)

    output_frame.to_csv('projection.csv')
