from pmdarima.model_selection import train_test_split
from matplotlib import pyplot
import pmdarima
import arch
import pandas
import numpy
import os


class ARIMAGARCHForecaster:
    def load_stock_prices(self, stock_file_path, timestamp, num_prices):
        raw_prices = pandas.read_csv(stock_file_path)
        try:
            timestamp_index = raw_prices.index[raw_prices['Datetime'] == timestamp].tolist()[0] + 1
        except IndexError:
            return numpy.ndarray([])

        clean_prices = raw_prices.iloc[(timestamp_index - num_prices):timestamp_index, 1:2].values
        return numpy.ndarray.flatten(clean_prices)

    def generate_test_set(self, training_data, test_data):
        total = numpy.concatenate((training_data, test_data))
        test_set = []
        for i in range(0, len(test_data)):
            test_set.append(total[i:len(training_data) + i])
        return test_set

    def predict(self, data):
        arima_model = pmdarima.auto_arima(data)
        arima_residuals = arima_model.arima_res_.resid
        garch_model = arch.arch_model(arima_residuals, p=1, q=1).fit()

        predicted_mean = arima_model.predict(n_periods=1)[0]
        predicted_residual = garch_model.forecast(horizon=1, reindex=False)
        predicted_variance = predicted_residual.mean['h.1'].iloc[-1]
        return predicted_mean - predicted_variance

    def evaluate_model(self):
        prices = self.load_stock_prices('intermediate_data/prices/BBBY.csv', '2022-09-07 15:59:00-04:00', 390)
        training_data, test_data = train_test_split(prices, train_size=360, test_size=30)
        test_set = self.generate_test_set(training_data, test_data)

        forecasts = []
        for i in range(0, len(test_set)):
            forecasts.append(self.predict(test_set[i]))

        pyplot.figure(figsize=(10, 6))
        pyplot.plot(test_data, color='blue', label=f'Actual BBBY')
        pyplot.plot(forecasts, color='red', label=f'Predicted BBBY')
        pyplot.title(f'BBBY Prediction')
        pyplot.xlabel('Date')
        pyplot.ylabel('Stock Price')
        pyplot.legend()

        if not os.path.isdir(f'intermediate_data/graphs'):
            os.makedirs(f'intermediate_data/graphs')
        pyplot.savefig(f'intermediate_data/graphs/BBBY.png')
