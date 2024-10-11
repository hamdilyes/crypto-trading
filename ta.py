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


# pd.DataFrame().ta.indicators()

# indicators_list = ['aberration', 'above', 'above_value', 'accbands', 'ad', 'adosc', 'adx', 'alma', 'amat', 'ao', 'aobv', 'apo', 'aroon', 'atr', 'bbands', 'below', 'below_value', 'bias', 'bop', 'brar', 'cci', 'cdl_pattern',
# 'cdl_z', 'cfo', 'cg', 'chop', 'cksp', 'cmf', 'cmo', 'coppock', 'cross', 'cross_value', 'cti', 'decay', 'decreasing', 'dema', 'dm', 'donchian', 'dpo', 'ebsw', 'efi', 'ema', 'entropy', 'eom', 'er', 'eri',
# 'fisher', 'fwma', 'ha', 'hilo', 'hl2', 'hlc3', 'hma', 'hwc', 'hwma', 'ichimoku', 'increasing', 'inertia', 'jma', 'kama', 'kc', 'kdj', 'kst', 'kurtosis', 'kvo', 'linreg', 'log_return', 'long_run', 'macd',
# 'mad', 'massi', 'mcgd', 'median', 'mfi', 'midpoint', 'midprice', 'mom', 'natr', 'nvi', 'obv', 'ohlc4', 'pdist', 'percent_return', 'pgo', 'ppo', 'psar', 'psl', 'pvi', 'pvo', 'pvol', 'pvr', 'pvt', 'pwma', 'qqe',
# 'qstick', 'quantile', 'rma', 'roc', 'rsi', 'rsx', 'rvgi', 'rvi', 'short_run', 'sinwma', 'skew', 'slope', 'sma', 'smi', 'squeeze', 'squeeze_pro', 'ssf', 'stc', 'stdev', 'stoch', 'stochrsi', 'supertrend',
# 'swma', 't3', 'td_seq', 'tema', 'thermo', 'tos_stdevall', 'trima', 'trix', 'true_range', 'tsi', 'tsignals', 'ttm_trend', 'ui', 'uo', 'variance', 'vhf', 'vidya', 'vortex', 'vp', 'vwap', 'vwma', 'wcp',
# 'willr', 'wma', 'xsignals', 'zlma', 'zscore']

# search = 'ema'

# for x in indicators_list:
#     if search in x:
#         print(x)

# help(ta.ema)