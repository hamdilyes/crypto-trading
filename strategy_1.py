import pandas as pd

##################################################################
### strategy 1: buy and hold all pairs from start date + TP/SL ###
##################################################################

def get_strategy_1(start_date, amount, prices, symbols, take_profit=None, stop_loss=None):

    selected_symbols = symbols.copy()
    portfolio = {}

    for symbol in selected_symbols:
        # initialize volume
        df = prices[symbol].copy()
        df['volume'] = 0
        df['pnl'] = 0

        # buy
        trade_date = start_date
        trade_amount = amount
        try:
            trade_volume = trade_amount / df.loc[trade_date, 'price']
        except:
            selected_symbols.remove(symbol)
            continue
        df.loc[trade_date:, 'volume'] += trade_volume
        df.loc[trade_date, 'pnl'] -= trade_amount

        # stop loss
        if stop_loss is not None:
            sl_price = df.loc[trade_date, 'price'] * (1 - stop_loss/100)
            for i in range(1, len(df)):
                if df.iloc[i]['price'] <= sl_price:
                    trade_date = df.index[i]
                    trade_amount = df.loc[trade_date, 'volume'] * df.loc[trade_date, 'price']
                    df.loc[trade_date:, 'volume'] = 0
                    df.loc[trade_date, 'pnl'] += trade_amount
                    break

         # take profit
        if take_profit is not None:
            tp_price = df.loc[trade_date, 'price'] * (1 + take_profit/100)
            for i in range(1, len(df)):
                if df.iloc[i]['price'] >= tp_price:
                    trade_date = df.index[i]
                    trade_amount = df.loc[trade_date, 'volume'] * df.loc[trade_date, 'price']
                    df.loc[trade_date:, 'volume'] = 0
                    df.loc[trade_date, 'pnl'] += trade_amount
                    break

        # update value
        df['value'] = df['volume'] * df['price']

        # add to portfolio
        portfolio[symbol] = df

    # show portfolio value over time for all pairs aggregated
    strategy_value, strategy_pnl = 0, 0
    for symbol in selected_symbols:
        try:
            strategy_value += pd.DataFrame(portfolio[symbol]['value'])
            strategy_pnl += pd.DataFrame(portfolio[symbol]['pnl'])
        except:
            continue

    # portfolio value + PnL
    strategy = pd.concat([strategy_value, strategy_pnl.cumsum()], axis=1)
    strategy.columns = ['value', 'pnl']
    strategy['total'] = strategy['value'] + strategy['pnl']

    return strategy