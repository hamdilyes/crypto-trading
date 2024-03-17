import pandas as pd

from Historic_Crypto import HistoricalData

from historic_crypto import *


def strategy_1(pairs, start_date, end_date, amount):
    """
    Buy and hold strategy
    Buy 'amount' USDT worth of each pair at the start date and sell at the end date
    """
    dict_df = {}

    for pair in pairs:
        # hourly data
        try:
            data_start = HistoricalData(ticker=pair, granularity=3600, start_date=start_date, end_date=end_date_str(start_date, 60), verbose=False).retrieve_data()
            data_end = HistoricalData(ticker=pair, granularity=3600, start_date=end_date, end_date=end_date_str(end_date, 60), verbose=False).retrieve_data()
        except:
            # print(f'Error retrieving data for {pair}')
            continue

        data = pd.concat([data_start, data_end])
        
        data = data[['close']]
        data = data.rename(columns={'close': 'price'})
        data['action'] = [1, -1]

        initial_price = data['price'].iloc[0]
        data['base_currency_amount'] = amount / initial_price
        
        dict_df[pair] = data

    return dict_df