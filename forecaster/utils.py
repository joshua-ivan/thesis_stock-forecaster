from datetime import datetime, timedelta
import matplotlib.pyplot as pyplot
import pandas
import numpy
import os


default_graph_dir = '../forecaster_data/graphs'


def load_stock_prices(stock_file_path, timestamp, num_prices):
    raw_prices = pandas.read_csv(stock_file_path)
    try:
        timestamp_index = raw_prices.index[raw_prices['Datetime'] == timestamp].tolist()[0] + 1
    except IndexError:
        try:
            datetime_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S-04:00')
            datetime_obj -= timedelta(minutes=1)
            if datetime_obj.hour <= 9 and datetime_obj.minute < 30:
                datetime_obj = datetime_obj - timedelta(hours=17, minutes=30)
            return load_stock_prices(stock_file_path, datetime_obj.strftime('%Y-%m-%d %H:%M:%S-04:00'), num_prices)
        except ValueError:
            return numpy.ndarray([])

    clean_prices = raw_prices.iloc[(timestamp_index - num_prices):timestamp_index, 1:2].values
    return numpy.ndarray.flatten(clean_prices)


def plot_predictions(actual, predicted, ticker, plotter=pyplot, graph_dir=default_graph_dir, op_sys=os):
    plotter.figure(figsize=(10, 6))
    plotter.plot(actual, color='blue', label=f'Actual {ticker}')
    plotter.plot(predicted, color='red', label=f'Predicted {ticker}')
    plotter.title(f'{ticker} Prediction')
    plotter.xlabel('Date')
    plotter.ylabel('Stock Price')
    plotter.legend()

    if not op_sys.path.isdir(graph_dir):
        op_sys.makedirs(graph_dir)
    plotter.savefig(f'{graph_dir}/{ticker}.png')
