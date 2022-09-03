class Position:
    def __init__(self, ticker, leverage_type, quantity, price, date_time):
        self.ticker = ticker
        self.leverage_type = leverage_type
        self.price = price
        self.quantity = quantity
        self.date_time = date_time

    def __eq__(self, other):
        return self.ticker == other.ticker and\
            self.leverage_type == other.leverage_type and\
            self.price == other.price and\
            self.quantity == other.quantity and\
            self.date_time == other.date_time

    def __str__(self):
        return f'Position: {self.ticker} {self.leverage_type} - {self.quantity} @ {self.price} on {self.date_time}'
