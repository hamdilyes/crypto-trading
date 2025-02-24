from coinbase.rest import RESTClient
import matplotlib.pyplot as plt
import pandas as pd
import time


client = RESTClient(key_file="api_key.json")


def get_client():
    return client


def balance(currency=None):
    accounts = client.get_accounts()
    if currency:
        for account in accounts["accounts"]:
            if account.currency==currency:
                return account['available_balance']['value']
    else:
        print("Balance:")
        for account in accounts["accounts"]:
            if account.currency in ["BTC", "USDC"]:
                print(f"{account['currency']}: {account['available_balance']['value']}")


def sell_all(product="BTC-USDC"):
    coin = product.split("-")[0]
    balance_coin = float(balance(currency=coin))
    if balance_coin <= 0:
        print(f"No {coin} available to sell.")
        return
    client.market_order_sell(client_order_id="", product_id=product, base_size=str(balance_coin))
    print(f"Sold all {coin}")


def buy_and_sell(amount_usd, duration, product="BTC-USDC"):
    coin = product.split("-")[0]
    balance_usd = float(balance(currency="USDC"))
    if amount_usd > balance_usd:
        print(f"Insufficient balance: ${balance_usd:.2f}")
        return
    client.market_order_buy(product_id=product, quote_size=str(amount_usd), client_order_id="")
    amount_btc = float(balance(currency=coin))
    print(f"BUY {amount_btc} BTC")
    time.sleep(60 * duration)
    sell_all(product="BTC-USDC")

def cumulative_pnl(product="BTC-USDC"):
    fills = client.get_fills(product_ids=[product])
    # 'entry_id', 'trade_id', 'order_id', 'trade_time', 'trade_type',
    # 'price', 'size', 'commission', 'product_id', 'sequence_timestamp',
    # 'liquidity_indicator', 'size_in_quote', 'user_id', 'side', 'retail_portfolio_id'
    fills_data = []
    for fill in fills.fills:
        fills_data.append({
            "timestamp": fill.trade_time,
            "side": fill.side,
            "size": float(fill.size),
            "price": float(fill.price),
            "fee": float(fill.commission),
        })
    df_fills = pd.DataFrame(fills_data)
    df_fills["timestamp"] = pd.to_datetime(df_fills["timestamp"], format='%Y-%m-%dT%H:%M:%S.%fZ')
    df_fills["timestamp"] = pd.to_datetime(df_fills["timestamp"]).dt.floor('s')
    agg_dict = {
        "side": "first",
        "size": "sum",
        "price": "first",
        "fee": "sum",}
    df_fills = df_fills.groupby("timestamp").agg(agg_dict).reset_index()
    df_fills.set_index("timestamp", inplace=True)
    df_fills.sort_index(ascending=True, inplace=True)
    for idx, row in df_fills.iterrows():
        pnl = 0
        if row["side"] == "BUY":
            pnl = - row["size"] - row["fee"]
        if row["side"] == "SELL":
            pnl = row["size"]*row["price"] - row["fee"]
        df_fills.at[idx, "pnl"] = float(pnl)
    plt.figure(figsize=(10,5))
    plt.plot(df_fills["pnl"].cumsum())
    plt.title("PnL ($)")
    plt.show()