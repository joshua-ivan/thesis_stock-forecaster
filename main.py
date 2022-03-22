from sentiment import build_database, clean_posts, calculate
from forecaster import get_stock_history, forecaster
from trader import trader, simulation
from datetime import datetime


def main():
    # build_database.execute()
    # clean_posts.execute()
    # get_stock_history.execute()
    start_time = datetime.now()
    # calculate.execute()
    # forecaster.execute()
    trader.execute()
    simulation.execute()
    end_time = datetime.now()

    print(f'Runtime: {end_time - start_time}')


if __name__ == '__main__':
    main()
