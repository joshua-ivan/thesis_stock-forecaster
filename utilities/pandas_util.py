def extract_cell(data, index, row, column):
    series = data.loc[data[index] == row].reset_index(drop=True)[column]
    if len(series) <= 0:
        return None
    return series[0]
