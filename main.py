from sentiment import build_database
from forecaster import get_stock_history, forecaster


def main():
    build_database.execute()
    # get_stock_history.execute()
    # forecaster.execute()


if __name__ == '__main__':
    main()
