import pandas_ta as ta
import numpy as np
import pandas as pd


def add_dict_df_emas(dict_df, lengths=[12, 21]):
    for symbol, df in dict_df.items():
        # add EMAs
        for l in lengths:
            dict_df[symbol][f'EMA_{l}'] = ta.ema(df['close'], length=l)

        values = np.where(
            (dict_df[symbol]['EMA_12'] > dict_df[symbol]['EMA_21']) & (dict_df[symbol]['EMA_12'].shift(1) < dict_df[symbol]['EMA_21'].shift(1)), 1,
            np.where(
            (dict_df[symbol]['EMA_12'] < dict_df[symbol]['EMA_21']) & (dict_df[symbol]['EMA_12'].shift(1) > dict_df[symbol]['EMA_21'].shift(1)), -1, 0))
        
        dict_df[symbol]['Signal_EMA_12_21'] = pd.DataFrame(values, index=df.index, columns=['Signal_EMA_12_21'])

        # distance between EMAs
        dict_df[symbol]['Distance_EMA_12_21'] = dict_df[symbol]['EMA_12'] - dict_df[symbol]['EMA_21']

        # relative distance between EMAs
        dict_df[symbol]['Relative_Distance_EMA_12_21'] = dict_df[symbol]['Distance_EMA_12_21'] / (np.abs(dict_df[symbol]['Distance_EMA_12_21']).max()) * 100
    
    return dict_df