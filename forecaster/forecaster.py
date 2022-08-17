from utilities.input_validation import check_float
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from datetime import datetime
from matplotlib import pyplot
import utilities.date_util as date_util
import config
import pmdarima
import arch
import pandas
import numpy
import os

PRICES_DIR = 'prices'


def forecast(history, garch_p=1, garch_q=1):
    arima_model = pmdarima.auto_arima(history)
    arima_residuals = arima_model.arima_res_.resid
    garch = arch.arch_model(arima_residuals, p=garch_p, q=garch_q)
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
    check_float(expected, 'calculate_percent_error')
    check_float(actual, 'calculate_percent_error')

    return ((actual - expected) / actual) * 100


def evaluate_forecaster():
    columns = date_util.generate_aggregate_columns(config.end_date, config.raw_data_interval_days, config.bin_size)
    bins = date_util.generate_bin_boundaries(config.end_date, config.raw_data_interval_days, config.bin_size)
    mean_squared_percent_errors = []

    for garch_i in range(1, 6, 1):
        mean_squared_percent_errors.append([])

        for garch_j in range(1, 6, 1):
            output_frame = pandas.DataFrame(columns=columns)

            for stock in config.stocks:
                ticker = stock['ticker']
                price_history = fill_missing_dates(read_stock_prices(PRICES_DIR, ticker))

                stock_errors = [ticker]
                for _bin in bins:
                    bin_history = price_history_bin_to_series(price_history, _bin)
                    expected = forecast(bin_history[0:-1], garch_i, garch_j)
                    actual = bin_history[-1]
                    stock_errors.append(calculate_percent_error(expected, actual))

                output_frame.loc[len(output_frame)] = stock_errors

            all_errors = output_frame.loc[:, output_frame.columns != 'Ticker']
            mean_squared_percent_error = numpy.square(all_errors.values).mean()
            mean_squared_percent_errors[garch_i - 1].append(mean_squared_percent_error)
            output_frame.to_csv(f'garch_coeffs/i{garch_i}j{garch_j}.csv', index=False)

    for garch_i in range(1, 6, 1):
        for garch_j in range(1, 6, 1):
            error = mean_squared_percent_errors[garch_i - 1][garch_j - 1]
            print(f'GARCH({garch_i},{garch_j}) Mean Squared Percent Error: {error}\n')


def price_history_bin_to_series(history, _bin):
    start = datetime.fromisoformat(_bin['start'])
    end = datetime.fromisoformat(_bin['end'])
    return history[(history.index >= start) & (history.index <= end)]['Adj Close'].to_numpy()


def generate_forecasts():
    columns = date_util.generate_aggregate_columns(config.end_date, config.raw_data_interval_days, config.bin_size)
    bins = date_util.generate_bin_boundaries(config.end_date, config.raw_data_interval_days, config.bin_size)
    output_frame = pandas.DataFrame(columns=columns)
    garch_p = config.garch_coeffs['p']
    garch_q = config.garch_coeffs['q']

    for stock in config.stocks:
        ticker = stock['ticker']
        price_history = fill_missing_dates(read_stock_prices(PRICES_DIR, ticker))

        projections = [ticker]
        for _bin in bins:
            bin_history = price_history_bin_to_series(price_history, _bin)
            projections.append((forecast(bin_history, garch_p=garch_p, garch_q=garch_q) / bin_history[-1]) - 1)

        output_frame.loc[len(output_frame)] = projections

    output_frame.to_csv('projection.csv', index=False)


def lstm_tutorial():
    raw_train_data = pandas.read_csv('intermediate_data/prices/GME.csv')
    clean_train_data = raw_train_data.iloc[:, 1:2].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    clean_train_data = scaler.fit_transform(clean_train_data)
    features_set = []
    labels = []
    for i in range(60, len(clean_train_data)):
        features_set.append(clean_train_data[i-60:i, 0])
        labels.append(clean_train_data[i, 0])
    features_set = numpy.array(features_set)
    features_set = numpy.reshape(features_set, (features_set.shape[0], features_set.shape[1], 1))
    labels = numpy.array(labels)

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(features_set.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(features_set, labels, epochs=100, batch_size=32)

    raw_test_data = pandas.read_csv('intermediate_data/prices/GME.csv')
    clean_test_data = raw_test_data.iloc[:, 1:2].values
    total = pandas.concat((raw_train_data['Open'], raw_test_data['Open']), axis=0)
    test_inputs = total[len(total) - len(raw_test_data) - 60:].values
    test_inputs = test_inputs.reshape(-1,1)
    test_inputs = scaler.transform(test_inputs)
    test_features = []
    for i in range(60, len(clean_test_data)):
        test_features.append(test_inputs[i-60:i, 0])
    test_features = numpy.array(test_features)
    test_features = numpy.reshape(test_features, (test_features.shape[0], test_features.shape[1], 1))

    predictions = model.predict(test_features)
    predictions = scaler.inverse_transform(predictions)
    pyplot.figure(figsize=(10, 6))
    pyplot.plot(clean_test_data, color='blue', label='Actual GME')
    pyplot.plot(predictions, color='red', label='Predicted GME')
    pyplot.title('GME Prediction')
    pyplot.xlabel('Date')
    pyplot.ylabel('Stock Price')
    pyplot.legend()
    pyplot.savefig('GME.png')


def execute():
    generate_forecasts()
