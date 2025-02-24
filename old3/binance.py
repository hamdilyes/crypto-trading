import ccxt
import pandas as pd
import plotly.graph_objects as go


def get_binance():
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    symbols = ['BTC/USDT']

    return exchange, markets, symbols


exchange, markets, symbols = get_binance()


def plot_prices(symbols, freq, start_date, end_date, exchange=exchange):
    fig = go.Figure()

    for symbol in symbols:
        pair = custom_fetch_ohlcv(exchange, symbol, freq, start_date, end_date)
    
        fig.add_trace(go.Scatter(x=pair.index, y=pair['close'], mode='lines+markers', name=symbol))
    
    fig.update_layout(showlegend=True)
    fig.show()


def get_dict_df(symbols, freq, start_date, end_date, columns=None, exchange=exchange):
    prices = {}

    for symbol in symbols:
        pair = custom_fetch_ohlcv(exchange, symbol, freq, start_date, end_date)
        if columns:
            pair = pair[columns]
        
        prices[symbol] = pair

    return prices


def plot_df(df):
    colors={'EMA_12': 'green', 'EMA_21': 'red'}
    fig = go.Figure()

    for c in df.columns:
        mode = 'lines'
        if c in colors:
            fig.add_trace(go.Scatter(x=df.index, y=df[c], mode=mode, name=c, line=dict(color=colors[c])))
        else:
            fig.add_trace(go.Scatter(x=df.index, y=df[c], mode=mode, name=c))
        
    fig.update_layout(showlegend=True)
    fig.show()


def custom_fetch_ohlcv(exchange, symbol, freq, start_date, end_date):
    start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
    end_date = pd.to_datetime(end_date, format='%Y-%m-%d')
    if start_date:
        start_date = int(start_date.timestamp() * 1000)
    if end_date:
        end_date = int(end_date.timestamp() * 1000)
        
    pair_list = []
    pair = exchange.fetch_ohlcv(symbol, freq, start_date, limit=1000)
    pair = [candle for candle in pair if candle[0] <= end_date]
    pair_list.append(pair)
    while True:
        if len(pair) == 1000 and pair[-1][0] <= end_date:
            pair = exchange.fetch_ohlcv(symbol, freq, pair[-1][0], limit=1000)
            pair = [candle for candle in pair if candle[0] < end_date]
            pair_list.append(pair)
        else:
            break

    pair_list_df = []
    for pair in pair_list:
        pair = pd.DataFrame(pair, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        pair['timestamp'] = pd.to_datetime(pair['timestamp'], unit='ms')
        pair.set_index('timestamp', inplace=True)
        pair_list_df.append(pair)

    pair = pd.concat(pair_list_df, axis=0)

    return pair