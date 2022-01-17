from utilities import file_io
import re
import os


NON_ALPHANUMERIC_WHITESPACE = re.compile('[^0-9a-zA-Z \n]+')


def strip_nonalphanumeric_characters(string):
    return NON_ALPHANUMERIC_WHITESPACE.sub(' ', string)


def execute():
    post_directories = os.listdir('posts')
    for post_dir in post_directories:
        dates = os.listdir(f'posts/{post_dir}')
        for date in dates:
            files = os.listdir(f'posts/{post_dir}/{date}')
            for file in files:
                post = file_io.read_file(f'posts/{post_dir}/{date}/{file}')
                clean_post = strip_nonalphanumeric_characters(post)
                file_io.write_file(f'clean_posts/{post_dir}/{date}', file, clean_post)
