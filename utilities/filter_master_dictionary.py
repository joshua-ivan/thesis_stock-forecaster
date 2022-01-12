import pandas

dictionary = pandas.read_csv('LoughranMcDonald_MasterDictionary_2020.csv')

condensed_dict = dictionary[(dictionary['Negative'] > 0) | (dictionary['Positive'] > 0)]
condensed_dict = condensed_dict[['Word', 'Negative', 'Positive']]
condensed_dict.reset_index(drop=True, inplace=True)

condensed_dict.to_csv('LoughranMcDonald_MasterDictionary_2020__condensed.csv')
