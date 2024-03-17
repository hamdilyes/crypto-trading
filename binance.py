import ccxt
import pandas as pd
import plotly.graph_objects as go


def get_binance():
    exchange = ccxt.binance()
    markets = exchange.load_markets()

    # all active trading pairs
    symbols = list(markets.keys())
    symbols = [s for s in symbols if markets[s]['active']]
    # filter USDT pairs
    symbols = [s for s in symbols if s.endswith('/USDT')]
    # blacklist
    for s in ['XAI/USDT', 'MANTA/USDT', 'JUP/USDT', 'RONIN/USDT', 'PIXEL/USDT', 'PORTAL/USDT', 'AXL/USDT', 'METIS/USDT', 'BOME/USDT']:
        symbols.remove(s)

    return exchange, markets, symbols


exchange, markets, symbols = get_binance()


def plot_daily_prices(crypto, n, exchange=exchange):
    symbol = crypto + '/USDT'
    pair = exchange.fetch_ohlcv(symbol, '1d', limit=n)

    pair = pd.DataFrame(pair, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    pair['timestamp'] = pd.to_datetime(pair['timestamp'], unit='ms')
    pair.set_index('timestamp', inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pair.index, y=pair['close'], mode='lines+markers', name=symbol))
    fig.update_layout(showlegend=True)
    fig.show()


def get_daily_prices_dict(start_date, end_date=None, symbols=symbols, exchange=exchange):
    start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
    if end_date is not None:
        end_date = pd.to_datetime(end_date, format='%Y-%m-%d')

    prices = {}

    for symbol in symbols:
        # from start_date to today
        pair = exchange.fetch_ohlcv(symbol, '1d', since=int(start_date.timestamp()*1000))
        pair = pd.DataFrame(pair, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        pair.rename(columns={'close': 'price'}, inplace=True)
        pair.drop(columns=['open', 'high', 'low', 'volume'], inplace=True)
        pair['timestamp'] = pd.to_datetime(pair['timestamp'], unit='ms')
        pair.set_index('timestamp', inplace=True)
        # stop at end_date
        if end_date is not None:
            pair = pair.loc[:end_date]
        
        prices[symbol] = pair

    return prices