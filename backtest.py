import pandas as pd


def get_trades(df, signal_column):
    trades = df[['open', 'close', signal_column]].copy()
    trades['side'] = 0
    trades_buys = trades[trades[signal_column] > 0]
    trades_sell = trades[trades[signal_column] < 0]

    def prev_next(trades, side):
        buy_index = [x+side*pd.Timedelta('1h') for x in trades_buys.index]
        sell_index = [x+side*pd.Timedelta('1h') for x in trades_sell.index]

        trades_ = trades.copy()
        trades_.loc[buy_index, 'side'] = 1
        trades_.loc[sell_index, 'side'] = -1
        trades_ = trades_[trades_['side'] != 0]
        trades_.drop(columns=[signal_column, 'close'], inplace=True)

        return trades_

    trades_prev = prev_next(trades, -1)
    trades_next = prev_next(trades, 1)    

    return trades_prev, trades_next


def pnl(trades, investment=1000):
    pnl = 0
    current_position = 0

    for _, row in trades.iterrows():
        if current_position == 0:
            # open position
            amount = investment / row['open']
            current_position = amount
            pnl += - row['side']*investment
        else:
            # close position
            pnl += - row['side'] * current_position * row['open']
            current_position = 0
            # reopen position
            amount = investment / row['open']
            current_position = amount
            pnl += - row['side']*investment

    print(f'Invest {investment} $ -> PnL {round(pnl,2)} $ -> Return {round(pnl/investment*100,2)} %')