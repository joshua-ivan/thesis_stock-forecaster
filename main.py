from sentiment import build_database, clean_posts, calculate
from forecaster import get_stock_history, forecaster
from trader import trader


def main():
    # build_database.execute()
    # get_stock_history.execute()
    # forecaster.execute()
    # clean_posts.execute()
    # calculate.execute()
    trader.execute()


if __name__ == '__main__':
    main()
