from sentiment.tokenizer import TickerTokenizer
import unittest


class TickerTokenizerTests(unittest.TestCase):
    def assertArraysEqual(self, expected, actual):
        for i in range(len(expected)):
            self.assertEqual(expected[i], actual[i])

    def test_build_prefixed_ticker_tuples(self):
        tickers = ['MOCK', 'TEST']
        tokenizer = TickerTokenizer(tickers)
        expected = [('$', 'MOCK'), ('$', 'TEST')]
        actual = tokenizer.build_prefixed_tuples()
        self.assertArraysEqual(expected, actual)

    def test_word_tokenize(self):
        tickers = ['MOCK', 'TEST']
        tokenizer = TickerTokenizer(tickers)

        expected = ['$MOCK', 'and', '$TEST', 'to', 'the', 'moon']
        actual = tokenizer.word_tokenize('$MOCK and $TEST to the moon')
        self.assertArraysEqual(expected, actual)

    def test_sent_tokenize(self):
        tickers = ['MOCK', 'TEST']
        tokenizer = TickerTokenizer(tickers)

        expected = ['Everyone says $MOCK is going to zero.', '$TEST is going to the moon.']
        actual = tokenizer.sent_tokenize('Everyone says $MOCK is going to zero. $TEST is going to the moon.')
        self.assertArraysEqual(expected, actual)
