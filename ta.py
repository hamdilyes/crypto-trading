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

        dict_df[symbol]['Ratio_EMA_12_21'] = (dict_df[symbol]['EMA_12'] / dict_df[symbol]['EMA_21'] - 1)*100
        pct = 0.07
        values = np.where((dict_df[symbol]['Ratio_EMA_12_21'] < pct) & (dict_df[symbol]['Ratio_EMA_12_21'].shift(1) > pct), -1,
                                        np.where((dict_df[symbol]['Ratio_EMA_12_21'] > -pct) & (dict_df[symbol]['Ratio_EMA_12_21'].shift(1) < -pct), 1, 0))
        dict_df[symbol]['Signal_Ratio_EMA_12_21'] = pd.DataFrame(values, index=df.index, columns=['Signal_Ratio_EMA_12_21'])

        values = np.where(df.index == df.index[0], 1,
                          np.where(df.index == df.index[-2], -1, 0))
        dict_df[symbol]['Buy_Hold'] = pd.DataFrame(values, index=df.index, columns=['Buy_Hold'])
                
    return dict_df


# help(ta.ema)