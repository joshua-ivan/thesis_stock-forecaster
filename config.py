stocks = [
    {
        'ticker': 'MMM',
        'company': '3M'
    },
    {
        'ticker': 'AXP',
        'company': 'American Express'
    },
    {
        'ticker': 'AMGN',
        'company': 'Amgen'
    },
    {
        'ticker': 'AAPL',
        'company': 'Apple'
    },
    {
        'ticker': 'BA',
        'company': 'Boeing'
    },
    {
        'ticker': 'CAT',
        'company': 'Caterpillar'
    },
    {
        'ticker': 'CVX',
        'company': 'Chevron'
    },
    {
        'ticker': 'CSCO',
        'company': 'Cisco Systems'
    },
    {
        'ticker': 'KO',
        'company': 'Coca-Cola'
    },
    {
        'ticker': 'DIS',
        'company': 'Disney'
    },
    {
        'ticker': 'DOW',
        'company': 'Dow'
    },
    {
        'ticker': 'GS',
        'company': 'Goldman Sachs'
    },
    {
        'ticker': 'HD',
        'company': 'Home Depot'
    },
    {
        'ticker': 'HON',
        'company': 'Honeywell'
    },
    {
        'ticker': 'IBM',
        'company': 'IBM'
    },
    {
        'ticker': 'INTC',
        'company': 'Intel'
    },
    {
        'ticker': 'JNJ',
        'company': 'Johnson & Johnson'
    },
    {
        'ticker': 'JPM',
        'company': 'JPMorgan Chase'
    },
    {
        'ticker': 'MCD',
        'company': 'McDonald\'s'
    },
    {
        'ticker': 'MRK',
        'company': 'Merck'
    },
    {
        'ticker': 'MSFT',
        'company': 'Microsoft'
    },
    {
        'ticker': 'NKE',
        'company': 'Nike'
    },
    {
        'ticker': 'PG',
        'company': 'Procter & Gamble'
    },
    {
        'ticker': 'CRM',
        'company': 'Salesforce'
    },
    {
        'ticker': 'TRV',
        'company': 'Travelers'
    },
    {
        'ticker': 'UNH',
        'company': 'UnitedHealth'
    },
    {
        'ticker': 'VZ',
        'company': 'Verizon'
    },
    {
        'ticker': 'V',
        'company': 'Visa'
    },
    {
        'ticker': 'WBA',
        'company': 'Walgreens Boots Alliance'
    },
    {
        'ticker': 'WMT',
        'company': 'Walmart'
    },
]

subreddits = ['stocks', 'StockMarket', 'MillennialBets', 'Optionmillionaires', 'wallstreetbets']

end_date = '2022-01-30'
raw_data_interval_days = 365
bin_size = 90
djia_performance = 0.1582

counts_dir = 'counts'

garch_coeffs = {
    'p': 4,
    'q': 1
}

thresholds = {
    'positive': 0.25,
    'negative': -0.25
}

debug_responses = False
