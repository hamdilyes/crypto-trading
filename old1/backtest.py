import plotly.graph_objects as go

from old2.binance import get_daily_prices_dict, get_binance
from strategy_0 import get_strategy_0
from strategy_1 import get_strategy_1


_, _, symbols = get_binance()


def backtest(start_date, end_date=None, amount=10):
    # get prices
    prices = get_daily_prices_dict(start_date, end_date)

    # strategy 1: buy and hold all pairs from start date
    strategy_1, pairs = get_strategy_1(start_date, amount, prices, symbols)
    nb_cryptos = int(strategy_1.loc[start_date, 'value'] / amount)
    investment = nb_cryptos*amount

    strategy_1_1, _ = get_strategy_1(start_date, investment/3, prices, ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'])
    
    if pairs is not None:
        # strategy 0: BTC buy and hold from start date
        benchmark = get_strategy_0(start_date, investment, prices)

        fig = go.Figure()
        strategies = [benchmark, strategy_1, strategy_1_1]
        names = ['BTC', 'Mix', 'BTC/ETH/BNB']
        for strategy in strategies:
            fig.add_trace(go.Scatter(x=strategy.index, y=strategy['value'], mode='lines+markers', name=names.pop(0)))
        if end_date is None:
            # last index
            end_date = 'Today'
        fig.update_layout(showlegend=True, title=f'Portfolio Value | {start_date} - {end_date}', yaxis_title='$')
        fig.show()