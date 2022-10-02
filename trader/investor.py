from trader.price_fetcher import PriceFetcher


class Investor:
    def __init__(self, start_date, end_date, pf=PriceFetcher()):
        self.open_positions = []
        self.portfolio_value = 0.0
        self.loss_threshold = 0.01
        self.start_date = start_date
        self.end_date = end_date
        self.price_fetcher = pf
        self.log = []

    def check_open_positions(self, closing_datetime):
        for i in range(len(self.open_positions) - 1, -1, -1):
            position = self.open_positions[i]
            current_price = self.price_fetcher.get_price(position.ticker, closing_datetime,
                                                         self.start_date, self.end_date)

            opening_value = position.price * position.quantity
            closing_value = current_price * position.quantity
            raw_profit, profit_percent = 0.0, 0.0
            if position.leverage_type == 'SHORT':
                raw_profit = opening_value - closing_value
                profit_percent = raw_profit / closing_value
            elif position.leverage_type == 'LONG':
                raw_profit = closing_value - opening_value
                profit_percent = raw_profit / opening_value

            if profit_percent > (1 * self.loss_threshold) or profit_percent < (-1 * self.loss_threshold):
                self.close_position(raw_profit, i)

    def close_position(self, raw_profit, index):
        self.portfolio_value += raw_profit
        position = self.open_positions.pop(index)

        log_str = f'Closed position: {position}\nPortfolio value: {self.portfolio_value}'
        self.log.append(log_str)
        print(log_str)
