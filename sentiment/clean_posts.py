import re


NON_ALPHANUMERIC_WHITESPACE = re.compile('[^0-9a-zA-Z \n]+')


def strip_nonalphanumeric_characters(string):
    return NON_ALPHANUMERIC_WHITESPACE.sub(' ', string)
