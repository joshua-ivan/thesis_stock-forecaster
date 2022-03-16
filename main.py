from sentiment import build_database, clean_posts, calculate
from forecaster import get_stock_history, forecaster
from trader import trader, simulation


def main():
    # build_database.execute()
    # clean_posts.execute()
    # get_stock_history.execute()
    calculate.execute()
    forecaster.execute()
    trader.execute()
    simulation.execute()


if __name__ == '__main__':
    main()
