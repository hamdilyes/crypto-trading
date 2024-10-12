import pandas as pd


def get_trades(df, signal_column, freq):
    trades = df[['open', signal_column]].copy()
    trades['side'] = 0
    trades_buys = trades[trades[signal_column] > 0]
    trades_sell = trades[trades[signal_column] < 0]

    def prev_next(trades, side):
        buy_index = [x+side*pd.Timedelta(freq) for x in trades_buys.index]
        sell_index = [x+side*pd.Timedelta(freq) for x in trades_sell.index]
        buy_index = list(set(buy_index).intersection(trades.index))
        sell_index = list(set(sell_index).intersection(trades.index))
        trades_ = trades.copy()
        trades_.loc[buy_index, 'side'] = 1
        trades_.loc[sell_index, 'side'] = -1
        trades_ = trades_[trades_['side'] != 0]
        trades_.drop(columns=[signal_column], inplace=True)
        return trades_

    trades_prev = prev_next(trades, -1)
    trades_next = prev_next(trades, 1)
    trades_2prev = prev_next(trades, -2)
    trades_3prev = prev_next(trades, -3)

    return trades_prev, trades_next, trades_2prev, trades_3prev


def pnl(trades, investment=1000, verbose=True):
    current_position = 0
    value = investment
    open_price = 0
    close_price = 0
    value_list = []
    
    for _, row in trades.iterrows():
        if current_position == 0:
            # open position
            amount = investment / row['open']
            current_position = amount
            open_price = row['open']

        else:
            # close position
            close_price = row['open']
            return_ = - (close_price / open_price - 1)*row['side']
            pnl = investment * return_
            value = value+pnl
            value_list.append(pnl)
            current_position = 0
            # reopen position
            amount = investment / row['open']
            current_position = amount
            open_price = row['open']

    value = round(value, 2)
    pnl = round(value - investment, 2)
    if verbose:
        print(f'Invest {investment} $ -> PnL {round(pnl,2)} $')

    df_value = pd.DataFrame(value_list, columns=['value']).cumsum()
    df_value['value'] = df_value['value'] + investment

    return value, df_value


def pnl_compund(trades, investment=1000, verbose=True):
    current_position = 0
    value = investment
    open_price = 0
    close_price = 0
    value_list = []
    return_list = []
    
    for _, row in trades.iterrows():
        if current_position == 0:
            # open position
            amount = value / row['open']
            current_position = amount
            open_price = row['open']

        else:
            # close position
            close_price = row['open']
            return_ = - (close_price / open_price - 1)*row['side']
            return_list.append(return_)
            value = value * (1 + return_)
            pnl = value*return_
            value_list.append(pnl)
            current_position = 0
            # reopen position
            amount = value / row['open']
            current_position = amount
            open_price = row['open']

    value = round(value, 2)
    pnl = round(value - investment, 2)
    if verbose:
        print(f'Invest {investment} $ -> PnL {round(pnl,2)} $')

    df_value = pd.DataFrame(value_list, columns=['compound_value']).cumsum()
    df_value['compound_value'] = df_value['compound_value'] + investment

    df_return = pd.DataFrame(return_list, columns=['return'])

    return value, df_value, df_return