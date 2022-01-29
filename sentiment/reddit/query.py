def build(keywords):
    query = f'"{keywords[0]}"'
    index = 1
    while index < len(keywords):
        query = query + f' OR "{keywords[index]}"'
        index = index + 1
    return query
