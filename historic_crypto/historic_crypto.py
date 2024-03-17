import pandas as pd

from Historic_Crypto import Cryptocurrencies
# from Historic_Crypto import LiveCryptoData


def get_pairs():
    pairs_df = Cryptocurrencies(extended_output=True).find_crypto_pairs()
    # quote currency = USDT
    pairs_df = pairs_df[(pairs_df['quote_currency'] == 'USDT')
                        & (pairs_df['status'] == 'online')
                        & (pairs_df['fx_stablecoin'] == False)]
    pairs_df = pairs_df[['id']].sort_values(by='id').reset_index(drop=True)

    # store as list
    pairs = pairs_df['id'].tolist()

    # blacklist_pairs = []
    # for pair in blacklist_pairs:
    #     pairs.remove(pair)

    return pairs


def end_date_str(start_date_str, delta):
    start_date = pd.to_datetime(start_date_str)
    end_date = start_date + pd.Timedelta(delta, unit='s')
    
    return end_date.strftime('%Y-%m-%d-%H-%M')

