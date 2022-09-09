class PostSentiment:
    def __init__(self, filename, tickers, sentiment):
        self.filename = filename
        self.tickers = tickers
        self.sentiment = sentiment

    def __str__(self):
        return f'PostSentiment({self.filename}): ({self.tickers}, {self.sentiment})'

    def __eq__(self, other):
        if len(self.tickers) != len(other.tickers):
            return False
        for i in range(0, len(self.tickers)):
            if self.tickers[i] != other.tickers[i]:
                return False
        return self.filename == other.filename and self.sentiment == other.sentiment
