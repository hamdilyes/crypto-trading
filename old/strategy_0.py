import pandas as pd

####################################################
### strategy 0: buy and hold BTC from start date ###
####################################################

def get_strategy_0(start_date, amount, prices):

    symbol = 'BTC/USDT'
    portfolio = {}

    # initialize volume
    df = prices[symbol].copy()
    df['volume'] = 0
    df['pnl'] = 0

    # buy
    trade_date = start_date
    trade_amount = amount
    trade_volume = trade_amount / df.loc[trade_date, 'price']
    df.loc[trade_date:, 'volume'] += trade_volume
    df.loc[trade_date, 'pnl'] -= trade_amount

    # update value
    df['value'] = df['volume'] * df['price']

    # add to portfolio
    portfolio[symbol] = df

    # show portfolio value over time for all pairs aggregated
    strategy_value, strategy_pnl = 0, 0
    strategy_value += pd.DataFrame(portfolio[symbol]['value'])
    strategy_pnl += pd.DataFrame(portfolio[symbol]['pnl'])
    

    # portfolio value + PnL
    strategy = pd.concat([strategy_value, strategy_pnl.cumsum()], axis=1)
    strategy.columns = ['value', 'pnl']
    strategy['total'] = strategy['value'] + strategy['pnl']

    return strategy