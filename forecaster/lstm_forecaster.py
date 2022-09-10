from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential as KerasSequential
from keras.models import load_model as keras_load_model
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from os.path import isdir as builtin_isdir
import matplotlib.pyplot as pyplot
import os as python_os
import pandas
import numpy


class LSTMForecaster:
    class TrainingSet:
        def __init__(self, feature_set, labels):
            self.feature_set = feature_set
            self.labels = labels

    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def load_stock_prices(self, stock_file_path, timestamp, num_prices):
        raw_prices = pandas.read_csv(stock_file_path)
        try:
            timestamp_index = raw_prices.index[raw_prices['Datetime'] == timestamp].tolist()[0] + 1
        except IndexError:
            return numpy.ndarray([])

        clean_prices = raw_prices.iloc[(timestamp_index - num_prices):timestamp_index, 1:2].values
        return numpy.ndarray.flatten(clean_prices)

    def generate_training_set(self, training_data, cluster_size):
        scaled_training_data = self.scaler.fit_transform(training_data.reshape(-1, 1))
        feature_set = []
        labels = []
        for i in range(cluster_size, len(scaled_training_data)):
            feature_set.append(scaled_training_data[i - cluster_size:i])
            labels.append(scaled_training_data[i][0])
        feature_set = numpy.array(feature_set)
        feature_set = numpy.reshape(feature_set, (feature_set.shape[0], feature_set.shape[1], 1))
        labels = numpy.array(labels)
        return LSTMForecaster.TrainingSet(feature_set, labels)

    def compile_model(self, isdir, load_model, model_builder, model_file_path, feature_set):
        if isdir(model_file_path):
            model = load_model(model_file_path)
        else:
            model = model_builder()
            model.add(LSTM(units=50, return_sequences=True, input_shape=(feature_set.shape[1], 1)))
            model.add(Dropout(0.2))
            model.add(LSTM(units=50, return_sequences=True))
            model.add(Dropout(0.2))
            model.add(LSTM(units=50, return_sequences=True))
            model.add(Dropout(0.2))
            model.add(LSTM(units=50))
            model.add(Dropout(0.2))
            model.add(Dense(units=1))
            model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def fit_model(self, model, model_file_path, training_set):
        model.fit(training_set.feature_set, training_set.labels, epochs=10, batch_size=256)
        model.save(model_file_path)
        return model

    def generate_test_set(self, training_data, test_data, cluster_size):
        total = numpy.concatenate((training_data, test_data))
        test_inputs = total[len(total) - len(test_data) - cluster_size:]
        test_inputs = test_inputs.reshape(-1, 1)
        test_inputs = self.scaler.transform(test_inputs)
        test_set = []
        if len(test_data) is 0:
            test_set.append(test_inputs)
        else:
            for i in range(cluster_size, (len(test_data) + cluster_size)):
                test_set.append(test_inputs[i - cluster_size:i, 0])
        test_set = numpy.array(test_set)
        test_set = numpy.reshape(test_set, (test_set.shape[0], test_set.shape[1], 1))
        return test_set

    def test_predictions(self, model, test_set, test_data, plotter, os, graph_dir, ticker):
        predictions = model.predict(test_set)
        predictions = self.scaler.inverse_transform(predictions)

        plotter.figure(figsize=(10, 6))
        plotter.plot(test_data, color='blue', label=f'Actual {ticker}')
        plotter.plot(predictions, color='red', label=f'Predicted {ticker}')
        plotter.title(f'{ticker} Prediction')
        plotter.xlabel('Date')
        plotter.ylabel('Stock Price')
        plotter.legend()

        if not os.path.isdir(graph_dir):
            os.makedirs(graph_dir)
        plotter.savefig(f'{graph_dir}/{ticker}.png')

    def prod_prediction(self, model, test_set):
        prediction = model.predict(test_set)
        prediction = self.scaler.inverse_transform(prediction)
        return prediction

    def evaluate_model(self, ticker, training_timestamp, training_size, test_timestamp, test_size, cluster_size):
        base_data_dir = 'intermediate_data'
        training_data = self.load_stock_prices(f'{base_data_dir}/prices/{ticker}.csv',
                                               training_timestamp, training_size)
        training_set = self.generate_training_set(training_data, cluster_size)
        stock_model = self.compile_model(builtin_isdir, keras_load_model, KerasSequential,
                                         f'{base_data_dir}/models/{ticker}', training_set.feature_set)
        stock_model = self.fit_model(stock_model, f'{base_data_dir}/models/{ticker}', training_set)

        test_data = self.load_stock_prices(f'{base_data_dir}/prices/{ticker}.csv',
                                           test_timestamp, test_size)
        test_set = self.generate_test_set(training_data, test_data, cluster_size)
        self.test_predictions(stock_model, test_set, test_data, pyplot, python_os, f'{base_data_dir}/graphs', ticker)

    def generate_forecast(self, ticker, training_timestamp, training_size, cluster_size):
        base_data_dir = 'intermediate_data'
        training_data = self.load_stock_prices(f'{base_data_dir}/prices/{ticker}.csv',
                                               training_timestamp, training_size)
        training_set = self.generate_training_set(training_data, cluster_size)
        stock_model = self.compile_model(builtin_isdir, keras_load_model, KerasSequential,
                                         f'{base_data_dir}/models/{ticker}', training_set.feature_set)
        stock_model = self.fit_model(stock_model, f'{base_data_dir}/models/{ticker}', training_set)

        test_set = self.generate_test_set(training_data, numpy.array([]), cluster_size)
        return (self.prod_prediction(stock_model, test_set) - training_data[-1]) / training_data[-1]
