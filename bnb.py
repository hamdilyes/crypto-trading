from binance.client import Client
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# Replace with your API key and secret
api_key = 'N82BEv4mWswNOxPa7FEN602VOfnn1N2XS6tF83eqoKO5Z43NBrmuGCjXGfewMoHE'
api_secret = 'SECRET-API-KEY'

client = Client(api_key, api_secret)

def get_asset_balance(asset_coin = "USDT"):
    return float(client.get_asset_balance(asset_coin)["free"])

def check_price_second_route():
    """
    returns a list with
    0: True if price of direct route is higher than the price of the second route
    1: price of ETHUSDT
    2: price of BTCUSDT
    3: price of ETHBTC
    """
    tickers = client.get_all_tickers()
    return [(float(tickers[12]["price"]) > (float(tickers[11]["price"]) * float(tickers[0]["price"]))), 
            float(tickers[12]["price"]), float(tickers[11]["price"]), float(tickers[0]["price"])]

def buy_btc_usdt(price = 55000, amount=0.0001): # okay
    try:
        # Place the limit buy order
        order = client.order_limit_buy(
            symbol="BTCUSDT",       # Trading pair (e.g., 'BTCUSDT')
            quantity=amount,     # Amount of buy_coin to buy
            price=price          # Limit price in use_coin
        )
        print(order)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def buy_eth_btc(price = 0.04010, amount=0.0001): # okay
    """
    The price is read as how much "price" bitcoin do I need to buy 1 eth
    The amount is the qunatity of BTC that you have
    """
    
        # Calculate how much ETH you can buy with the given BTC amount
    eth_amount = round(amount / price, 4)  # 4 decimal places for ETH

    try:
        order = client.order_limit_buy(
                symbol="ETHBTC",       # Trading pair (e.g., 'BTCUSDT')
                quantity=eth_amount,     # Amount of buy_coin to buy
                price= str(price)          # Limit price in use_coin
            )
        print(order)
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def sell_eth(price=2800, amount=0.003): # okay
    """
    Sells ETH for USDT with a limit order.
    
    Parameters:
    - price: The price of ETH in USDT (e.g., 2600 USDT per ETH).
    - amount: The amount of ETH to sell.
    """
    try:
        # Place a limit sell order on the ETHUSDT pair
        order = client.order_limit_sell(
            symbol="ETHUSDT",  # Trading pair (ETH/USDT)
            quantity=amount,   # Amount of ETH to sell
            price=str(price)   # Limit price in USDT per ETH
        )
        print(order)
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


# Check for the allowed format of binance ... 


def get_sol_price():
    tickers = client.get_all_tickers()
    return float(tickers[779]["price"])

def sell_sol(price=158, amount=0.06):
    try:
        order = client.order_limit_sell(
            symbol="SOLUSDT",  # Trading pair (SOL/USDT)
            quantity=amount,   # Amount of SOL to sell
            price=str(price)   # Limit price in USDT per SOL
        )
        print(order)
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def buy_sol(price=152, amount=0.06):
    try:
        order = client.order_limit_buy(
            symbol="SOLUSDT",  # Trading pair (SOL/USDT)
            quantity=amount,   # Amount of SOL to sell
            price=str(price)   # Limit price in USDT per SOL
        )
        print(order)
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def cancel_order(which_order="all"):
    """
    Cancel orders based on input:
    - 'all' cancels all open orders.
    - 'buy' cancels all open buy orders.
    - 'sell' cancels all open sell orders.
    
    Parameters:
    which_order: str, optional (default = 'all')
    """
    try:
        # Fetch all open orders
        open_orders = client.get_open_orders()

        if not open_orders:
            print("No open orders found.")
            return

        # Loop through orders and cancel based on the filter
        for order in open_orders:
            order_type = order['side']  # Buy or Sell
            symbol = order['symbol']
            order_id = order['orderId']

            # Cancel based on order type
            if which_order == "all" or \
               (which_order == "buy" and order_type == "BUY") or \
               (which_order == "sell" and order_type == "SELL"):
                
                result = client.cancel_order(symbol=symbol, orderId=order_id)
                print(f"Cancelled {order_type.lower()} order {order_id} for {symbol}")
        
        print("Order cancellation completed.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def there_is_order():
    # check whether there is an order
    return(not not client.get_open_orders())
        

### Historical prices 
# Function to get historical prices for BTC/USDT
def get_historical_prices(coin="BTC", price_coin="USDT", start_date=None, end_date=None, interval="1m", limit=30):
    """
    Fetches historical price data for a given coin pair from Binance.

    Parameters:
    - coin: The base coin (e.g., BTC).
    - price_coin: The quote coin (e.g., USDT).
    - start_date: The start date for fetching historical data (e.g., "2024-09-01"). Default is None.
    - end_date: The end date for fetching historical data (e.g., "2024-09-02"). Default is None.
    - interval: The interval for candlestick data (e.g., "1m" for 1 minute).
    - limit: The number of price data points to retrieve (default is 30).

    Returns:
    - A pandas DataFrame containing the historical price data.
    """
    # Construct the trading pair symbol (e.g., "BTCUSDT")
    symbol = f"{coin}{price_coin}"
    
    # Define interval mappings for Binance API
    interval_mapping = {
        "1m": Client.KLINE_INTERVAL_1MINUTE,
        "3m": Client.KLINE_INTERVAL_3MINUTE,
        "5m": Client.KLINE_INTERVAL_5MINUTE,
        "15m": Client.KLINE_INTERVAL_15MINUTE,
        "30m": Client.KLINE_INTERVAL_30MINUTE,
        "1h": Client.KLINE_INTERVAL_1HOUR,
        "2h": Client.KLINE_INTERVAL_2HOUR,
        "4h": Client.KLINE_INTERVAL_4HOUR,
        "6h": Client.KLINE_INTERVAL_6HOUR,
        "8h": Client.KLINE_INTERVAL_8HOUR,
        "12h": Client.KLINE_INTERVAL_12HOUR,
        "1d": Client.KLINE_INTERVAL_1DAY,
        "3d": Client.KLINE_INTERVAL_3DAY,
        "1w": Client.KLINE_INTERVAL_1WEEK,
        "1M": Client.KLINE_INTERVAL_1MONTH
    }

    # Fetch the last 'limit' data points if start_date and end_date are not specified
    if start_date is None and end_date is None:
        klines = client.get_historical_klines(symbol, interval_mapping[interval], limit=limit)
    else:
        klines = client.get_historical_klines(symbol, interval_mapping[interval], start_date, end_date, limit=limit)
    
    # Convert the data into a pandas DataFrame for easier analysis
    df = pd.DataFrame(klines, columns=[
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
        'Close Time', 'Quote Asset Volume', 'Number of Trades', 
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'])
    
    # Convert the time to a human-readable format
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')

    # Convert price columns to numeric for easier analysis
    df['Open'] = pd.to_numeric(df['Open'])
    df['High'] = pd.to_numeric(df['High'])
    df['Low'] = pd.to_numeric(df['Low'])
    df['Close'] = pd.to_numeric(df['Close'])
    
    # Return the DataFrame with historical data
    return df



#### Get the trend 
def trend_going_up(coin="SOL", limit=10, period=300, plot=False):
    """
    Function to determine if the trend of a given time series is going up.
    
    Parameters:
    - coin: The cryptocurrency to fetch the data for.
    - limit: The number of historical data points to retrieve. in minutes
    - period: The period to be used for seasonal decomposition and other calculations.
    - plot: Whether or not to plot the trend and linear regression.
    
    Returns:
    - True if the trend is going up, False otherwise.
    """
    
    # Get historical prices (you need to define or import `get_historical_prices`)
    df = get_historical_prices(interval="1m", limit=limit, coin=coin)
    df_sim = df[["Low", "High", "Number of Trades"]]

    # Generate time series by repeating the mean value for each row
    samples = []
    for index, row in df_sim.iterrows():
        mean = (row['Low'] + row['High']) / 2
        repeated_samples = [mean] * int(row['Number of Trades'])
        samples.append(repeated_samples)

    time_series = np.hstack(samples)
    
    # Check if the sum of trades is less than the period (early exit if so)
    if df_sim["Number of Trades"].sum() < (period/4):
        print("There is not enough data to perform the analysis.")
        return False
    
    # Decompose the time series to extract the trend
    result = seasonal_decompose(time_series, model='additive', period=period)
    trend = result.trend

    # Generate time indices
    len_ts = len(time_series)
    time = np.arange(len_ts)

    # Fit a linear regression (1st-degree polynomial) to the time series
    slope, intercept = np.polyfit(time, time_series, 1)

    # Plot both the trend and the linear regression line
    if plot:
        plt.figure(figsize=(10, 6))
        
        # Plot the original time series
        plt.plot(time_series, label="Original Time Series", alpha=0.6)
        
        # Plot the trend from seasonal decomposition
        plt.plot(trend, label="Trend (Decomposition)", color='orange', linewidth=2)
        
        # Plot the linear regression line
        linear_fit = intercept + slope * time
        plt.plot(time, linear_fit, label="Linear Regression", color='red', linestyle='--')
        
        # Labels and legend
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.title(f"Trend Analysis for {coin}")
        plt.legend()
        plt.show()

    # Return True if the slope is higher than `how_fast`, indicating an upward trend
    if slope > 0:
        print(len_ts*slope)
        return True
    else:
        print(slope)
        return False

