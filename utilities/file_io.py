import os


def read_file(location):
    try:
        with open(location, 'r', encoding='utf-8') as file:
            text = file.read()
            file.close()
            return text
    except OSError as error:
        print(error)


def write_file(directory, filename, content):
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(f'{directory}/{filename}', 'w', encoding='utf-8') as file:
            file.write(content)
            file.close()
    except OSError as error:
        print(error)
