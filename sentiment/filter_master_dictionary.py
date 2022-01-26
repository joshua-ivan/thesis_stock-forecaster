import pandas


def condense_dictionary(terms):
    if str(type(terms)) != '<class \'pandas.core.frame.DataFrame\'>':
        raise TypeError('condensed_dictionary expects a pandas DataFrame')

    condensed = terms[(terms['Negative'] > 0) | (terms['Positive'] > 0)]
    condensed = condensed[['Word', 'Negative', 'Positive']]
    condensed['Negative'].where(condensed['Negative'] <= 0, 1, inplace=True)
    condensed['Positive'].where(condensed['Positive'] <= 0, 1, inplace=True)
    condensed.reset_index(drop=True, inplace=True)
    return condensed


def generate_filename(filename):
    if str(type(filename)) != '<class \'str\'>':
        raise TypeError('generate_filename expects a string')

    condensed_filename = filename.split('.')[0]
    return f'{condensed_filename}__condensed.csv'


def execute(filename):
    condense_dictionary(pandas.read_csv(filename)).to_csv(generate_filename(filename), index=False)
