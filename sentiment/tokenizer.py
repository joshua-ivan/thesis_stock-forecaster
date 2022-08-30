from nltk.tokenize import MWETokenizer, word_tokenize, sent_tokenize


class TickerTokenizer:
    def __init__(self, tickers):
        self.tickers = tickers
        tuples = self.build_prefixed_tuples()
        self.mwe_tokenizer = MWETokenizer(tuples, '')

    def build_prefixed_tuples(self):
        return [(lambda t: ('$', t.replace('$', '')))(t) for t in self.tickers]

    def word_tokenize(self, text):
        return self.mwe_tokenizer.tokenize(word_tokenize(text))

    def sent_tokenize(self, text):
        return sent_tokenize(text)
