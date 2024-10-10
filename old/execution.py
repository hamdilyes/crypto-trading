from binance import get_binance


exchange, markets, symbols = get_binance()


def execute_trade(symbol, amount, side):
    if side == 'buy':
        buy_price = exchange.fetch_ticker(symbol)['bid']
        # USDT to crypto
        amount_crypto = amount / buy_price
        exchange.create_market_buy_order(symbol, amount_crypto)
        print(f'BUY {amount} $ - {symbol}')
    
    elif side == 'sell':
        sell_price = exchange.fetch_ticker(symbol)['ask']
        # USDT to crypto
        amount_crypto = amount / sell_price
        exchange.create_market_sell_order(symbol, amount)
        print(f'SELL {amount} $ - {symbol}')