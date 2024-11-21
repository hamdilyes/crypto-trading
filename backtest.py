import pandas as pd


def get_trades(df, signal_column, freq, shorts):
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

        # processing
        trades_.reset_index(inplace=True)
        trades_.columns = ['entry_timestamp', 'entry', 'side']
        trades_['exit'] = trades_['entry'].shift(-1)
        trades_['exit_timestamp'] = trades_['entry_timestamp'].shift(-1)
        trades_['return'] = round((trades_['exit']/trades_['entry']-1)*100,2)*trades_['side']
        trades_.dropna(inplace=True)

        if not shorts:
            trades_ = trades_[trades_['side'] > 0]

        return trades_

    trades_next = prev_next(trades, 1)

    return trades_next


def get_pnl(trades, investment, start_date):
    df = trades[['exit_timestamp', 'return']].copy()
    df.set_index('exit_timestamp', inplace=True)

    # non-compound
    df['pnl'] = df['return']*investment/100
    df['value'] = df['pnl'].cumsum()+investment

    # compound
    df['value_compound'] = round(investment * (1 + df['return'] / 100).cumprod(),2)

    # add row
    row = {'value': investment, 'value_compound': investment}
    df = pd.concat([df, pd.DataFrame(row, index=[pd.to_datetime(start_date, format='%Y-%m-%d')])])
    df.sort_index(inplace=True)
    df.drop(columns=['pnl', 'return'], inplace=True)

    return df