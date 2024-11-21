import ccxt
import pandas as pd
import plotly.graph_objects as go


def get_binance():
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    symbols = ['BTC/USDT']

    return exchange, markets, symbols


exchange, markets, symbols = get_binance()

# start_date = '2024-01-01'
# end_date = '2024-06-30'

# start_date = '2023-07-01'
# end_date = '2023-12-31'

start_date = '2023-01-01'
end_date = '2024-01-01'


def plot_prices(cryptos, freq, exchange=exchange, start_date=start_date, end_date=end_date):
    symbols = [crypto + '/USDT' for crypto in cryptos]
    fig = go.Figure()

    for symbol in symbols:
        pair = custom_fetch_ohlcv(exchange, symbol, freq, start_date, end_date)
    
        fig.add_trace(go.Scatter(x=pair.index, y=pair['close'], mode='lines+markers', name=symbol))
    
    fig.update_layout(showlegend=True)
    fig.show()


def get_dict_df(symbols, freq, columns=None, exchange=exchange, start_date=start_date, end_date=end_date):
    prices = {}

    for symbol in symbols:
        pair = custom_fetch_ohlcv(exchange, symbol, freq, start_date, end_date)
        if columns:
            pair = pair[columns]
        
        prices[symbol] = pair

    return prices


def plot_df(df):
    fig = go.Figure()

    for c in df.columns:
        if 'Signal' in c:
            ymin = df['close'].min()
            ymax = df['close'].max()

            for x in df.index[df[c] == 1]:
                fig.add_trace(go.Scatter(
                    x=[x, x],
                    y=[ymin, ymax],
                    mode='lines',
                    line=dict(color='green')))

            for x in df.index[df[c] == -1]:
                fig.add_trace(go.Scatter(
                    x=[x, x],
                    y=[ymin, ymax],
                    mode='lines',
                    line=dict(color='red')))

        else:
            mode = 'lines+markers'
            if c not in ['open', 'high', 'low', 'close']:
                mode = 'lines'
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