from forecaster.utils import load_stock_prices, plot_predictions
from pmdarima.model_selection import train_test_split
import pmdarima
import arch
import numpy


class ARIMAGARCHForecaster:
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
        prices = load_stock_prices('model_eval/one-minute/BBBY.csv', '2022-09-12 15:59:00-04:00', 90)
        training_data, test_data = train_test_split(prices, train_size=60, test_size=30)
        test_set = self.generate_test_set(training_data, test_data)

        forecasts = []
        for i in range(0, len(test_set)):
            forecasts.append(self.predict(test_set[i]))

        plot_predictions(test_data, forecasts, 'BBBY')

    def generate_forecast(self, ticker, training_timestamp, training_size):
        base_data_dir = '../forecaster_data/prices'
        training_data = load_stock_prices(f'{base_data_dir}/{ticker}.csv', training_timestamp, training_size)
        return (self.predict(training_data) - training_data[-1]) / training_data[-1]
