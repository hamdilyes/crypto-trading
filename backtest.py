import pandas as pd
import matplotlib.pyplot as plt

from historic_crypto import *
from strategy_1 import strategy_1


def backtest(pairs, end_date, nb_days, amount, verbose=True):
    """
    Backtest any strategy
    Show PnL for each pair as bar chart
    Show total PnL
    """
    if end_date == 'now':
        end_date = pd.to_datetime('now', utc=True).strftime('%Y-%m-%d-%H-%M')[:-2] + '00' # round to the nearest hour

    start_date = end_date_str(end_date, -nb_days*24*3600)

    if verbose:
        print(f'Backtesting -------------------- from {start_date} to {end_date} \n')
        print(f'Investment per pair ------------ {amount} USDT \n')

    dict_df = strategy_1(pairs, start_date, end_date, amount)
    selected_pairs = list(dict_df.keys())

    if verbose:
        print(f'Total Investment --------------- {len(selected_pairs)*amount} USDT \n')

    # calculate PnL for each pair
    pairs_pnl = {}
    for pair in selected_pairs:
        print(pair)
        try:
            df = dict_df[pair]
        except:
            continue
        df['pnl'] = -df['action'] * df[f'price'] * df['base_currency_amount']

        pairs_pnl[pair] = df['pnl'].sum()

    # calculate total PnL
    total_pnl = sum(pairs_pnl.values())

    if verbose:
        print(f'Total PnL --------------------- {round(total_pnl, 0)} USDT \n')
        try:
            print(f'Total ROI --------------------- {round(total_pnl / (len(selected_pairs)*amount) * 100, 2)} % \n')
        except:
            pass

    if verbose:
        # plot PnL for each pair as bar chart
        plt.bar(pairs_pnl.keys(), pairs_pnl.values())
        plt.xticks(rotation=90)
        plt.title(f'PnL per pair - {nb_days} Days')
        plt.show()

    return pairs_pnl, total_pnl