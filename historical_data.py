import datetime
import pandas as pd
from coinbase_connect import *


client = get_client()


def get_candles_data(granularity, product="BTC-USDC"):
    start_date = (datetime.datetime.now() - datetime.timedelta(weeks=12))
    end_date = datetime.datetime.now()
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    granularities = {3600: "ONE_HOUR", 900: "FIFTEEN_MINUTE", 300: "FIVE_MINUTE"}
    granularity_str = granularities[granularity]
    time_per_request = 300 * granularity  # limit 350
    df = pd.DataFrame()
    while start_timestamp < end_timestamp:
        request_end_timestamp = min(start_timestamp + time_per_request, end_timestamp)
        candles = client.get_candles(
            product_id=product,
            start=str(start_timestamp),
            end=str(request_end_timestamp),
            granularity=granularity_str)
        if not candles:
            break
        candles_data = []
        for row in candles["candles"]:
            candles_data.append(row.to_dict())
        temp_df = pd.DataFrame(candles_data)
        df = pd.concat([df, temp_df], ignore_index=True)
        start_timestamp = request_end_timestamp
    df['start'] = pd.to_datetime(df['start'].astype(int), unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
    df.set_index("start", inplace=True)
    df.sort_index(inplace=True)
    df = df.astype(float)
    return df