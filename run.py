from binance import *
from ta import *
from backtest import *


def run(symbol, start_date, end_date, investment=1000, frequencies=['4h'], shorts=False, strategies=['Signal_EMA_12_21', 'Signal_Ratio_EMA_12_21'], live=False):

    df_freq, df_plot_freq, trades_freq, pnl_freq, pnl_live_freq = {}, {}, {}, {}, {}
    for freq in frequencies:

        dict_df = get_dict_df(symbols=[symbol], freq=freq, columns=['close', 'open'], start_date=start_date, end_date=end_date)
        dict_df = add_dict_df_emas(dict_df, lengths=[12, 21])
        df = dict_df[symbol]

        df_plot = df[['close', 'EMA_12', 'EMA_21']].copy()
        df_plot.columns = [symbol, 'EMA_12', 'EMA_21']

        trades, pnl, pnl_live = {}, {}, {}
        for signal in strategies:
            if signal =='Buy_Hold' and freq != frequencies[0]:
                continue
            trades[signal] = get_trades(df=df, signal_column=signal, freq=freq, shorts=shorts)

            pnl[signal] = get_pnl(trades=trades[signal], start_date=start_date, investment=investment)
            if signal == 'Buy_Hold':
                pnl[signal].columns = [f'{signal}', f'{signal}_']
                pnl[signal] = pnl[signal][[f'{signal}']]
            else:
                pnl[signal].columns = [f'{freq}_{signal}', f'{freq}_compound_{signal}']
                pnl[signal] = pnl[signal][[f'{freq}_{signal}']]

            # make it live
            if live:
                dff = pd.DataFrame(index=df.index)
                dff['close'] = df['close']
                dff['cash'] = np.nan
                dff['btc'] = 0
                for idx, row in pnl[signal].iterrows():
                    name = f'{freq}_{signal}' if signal != 'Buy_Hold' else f'{signal}'
                    dff.loc[idx, 'cash'] = row[name]
                dff.fillna(method='ffill', inplace=True)
                for _, row in trades[signal].iterrows():
                    dff.loc[row['entry_timestamp']: row['exit_timestamp'], 'btc'] = investment*dff.loc[row['entry_timestamp']: row['exit_timestamp'], 'close']/dff.loc[row['entry_timestamp'], 'close']
                    dff.loc[row['entry_timestamp']: row['exit_timestamp'], 'cash'] -= investment
                dff['live'] = dff['cash'] + dff['btc']
                dff = dff[['live']]
                dff.columns = [name]
                pnl_live[signal] = dff

        # save to dict
        df_freq[freq] = df
        df_plot_freq[freq] = df_plot
        trades_freq[freq] = trades
        pnl_freq[freq] = pnl
        pnl_live_freq[freq] = pnl_live

    pnl_concat = pd.concat([pnl_freq[freq][signal] for freq in frequencies for signal in strategies], axis=1)
    pnl_concat.fillna(method='ffill', inplace=True)

    if live:
        pnl_live_concat = pd.concat([pnl_live_freq[freq][signal] for freq in frequencies for signal in strategies], axis=1)
        pnl_live_concat.fillna(method='ffill', inplace=True)
        return df_freq, df_plot_freq, trades_freq, pnl_freq, pnl_concat, pnl_live_concat

    return df_freq, df_plot_freq, trades_freq, pnl_freq, pnl_concat, None


# def live(df_freq, trades_freq, pnl_freq):
#     freq = list(df_freq.keys())[0]

#     df = df_freq[freq][['close']]
#     trades = trades_freq[freq]['Signal_EMA_12_21'][['entry_timestamp', 'exit_timestamp']]
#     pnl = pnl_freq[freq]['Signal_EMA_12_21']

#     investment = 1000
#     dff = pd.DataFrame(index=df.index)

#     dff['close'] = df['close']

#     dff['cash'] = np.nan
#     dff['btc'] = 0

#     for idx, row in pnl.iterrows():
#         dff.loc[idx, 'cash'] = row[f'{freq}_Signal_EMA_12_21']

#     dff.fillna(method='ffill', inplace=True)

#     for _, row in trades.iterrows():
#         dff.loc[row['entry_timestamp']: row['exit_timestamp'], 'btc'] = investment*dff.loc[row['entry_timestamp']: row['exit_timestamp'], 'close']/dff.loc[row['entry_timestamp'], 'close']
#         dff.loc[row['entry_timestamp']: row['exit_timestamp'], 'cash'] -= investment

#     dff['live'] = dff['cash'] + dff['btc']

#     plot_df(dff[['live']])


# def run(symbol, start_date, end_date, investment=1000, frequencies=['4h'], shorts=False):

#     df_freq, df_plot_freq, trades_freq, pnl_freq = {}, {}, {}, {}
#     for freq in frequencies:

#         dict_df = get_dict_df(symbols=[symbol], freq=freq, columns=['close', 'open'], start_date=start_date, end_date=end_date)
#         dict_df = add_dict_df_emas(dict_df, lengths=[12, 21])
#         df = dict_df[symbol]

#         df_plot = df[['close', 'EMA_12', 'EMA_21']].copy()
#         df_plot.columns = [symbol, 'EMA_12', 'EMA_21']

#         trades = get_trades(df, 'Signal_EMA_12_21', freq, shorts=shorts)

#         pnl = get_pnl(trades=trades, start_date=start_date, investment=investment)
#         pnl.columns = [f'{freq}_value', f'{freq}_value_compound']
#         pnl = pnl[[f'{freq}_value']]

#         # save to dict
#         df_freq[freq] = df
#         df_plot_freq[freq] = df_plot
#         trades_freq[freq] = trades
#         pnl_freq[freq] = pnl

#         # bh
#         if freq == frequencies[0]:
#             pnl_bh = df[['close']].copy()
#             pnl_bh['Buy&Hold'] = round(pnl_bh['close']*1000/pnl_bh['close'].iloc[0],2)
#             pnl_bh = pnl_bh[['Buy&Hold']]

#     pnl_concat = pd.concat([pnl_freq[freq] for freq in frequencies], axis=1)
#     pnl_concat = pd.concat([pnl_concat, pnl_bh], axis=1)
#     pnl_concat.fillna(method='ffill', inplace=True)

#     return df_freq, df_plot_freq, trades_freq, pnl_freq, pnl_concat