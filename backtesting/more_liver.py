import pandas as pd
import numpy as np
import json
import math
import matplotlib.pyplot as plt
import sys

# Sell at 200 SMA cross, with chunks.
def more_liver_test(dataframe, signal):
    balance = 100000.00
    shares = 0
    line = None
    chunk = None
    chunk_counter = 5
    next_buy_price = 0
    previous_close = None

    black_swan = parsed[parsed[signal + ' Delta'] < 0].dropna()[signal + ' Delta'].quantile(.1)

    for row_index, row_value in dataframe.iterrows():
        price = row_value['4. close']
        buy_point = round(row_value[signal] + (price * black_swan), 2)

        if shares == 0:
            if price < buy_point and price > next_buy_price and chunk_counter > 0:
                if line == None:
                    line = math.floor((balance/price))

                if chunk == None:
                    chunk = math.floor(line / 5)

                balance -= round((chunk * price), 2)
                shares += chunk
                next_buy_price = round(price + (price * .01), 2)
                chunk_counter -= 1
                dataframe.loc[row_value.name, 'bought'] = price
                print("bought", chunk, "shares", "at price", price, "chunk number", 5 - chunk_counter, "now own", shares, "shares", line, "line")
        elif shares > 0:
            if price > next_buy_price and chunk_counter > 0:
                if line == None:
                    line = math.floor((balance/price))

                if chunk == None:
                    chunk = math.floor(line / 5)

                balance -= round((chunk * price), 2)
                shares += chunk
                next_buy_price = round(price + (price * .01), 2)
                chunk_counter -= 1
                dataframe.loc[row_value.name, 'bought'] = price
                print("bought", chunk, "shares", "at price", price, "chunk number", 5 - chunk_counter, "now own", shares, "shares")

            elif price > row_value[signal] and shares > 0:
                print("sold", shares, "shares at", price, "per shares", "total", round((shares* price), 2))
                balance += round((shares * price), 2)
                line = None
                chunk = None
                shares = 0
                chunk_counter = 5            
                next_buy_price = 0
                dataframe.loc[row_value.name, 'sold'] = price

        print("Price:", row_value['4. close'], "Balance:", round(balance, 2), "Shares:", shares, "Line:", line, "Chunk:", chunk, "Next Buy Price", next_buy_price, "Previous close", previous_close, "buy_point", buy_point)
        previous_close = price
    return dataframe

with open('data/raw/' + sys.argv[1] + '.json') as file:
    data = json.loads(file.read())

raw = pd.DataFrame(data["Time Series (Daily)"])
parsed = raw.T[['4. close']].astype(float)
parsed = parsed.iloc[::-1]

signal = 200
signal_sma = 'SMA(' + str(signal) + ')'
signal_sma_delta = 'SMA(' + str(signal) + ') Delta'

parsed[signal_sma] = parsed['4. close'].rolling(signal).mean()

parsed[signal_sma_delta] = (parsed['4. close'] - parsed[signal_sma]) / parsed['4. close']

parsed = parsed[parsed[signal_sma].notna()]

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

parsed = more_liver_test(parsed, signal_sma)

fig, ax = plt.subplots()
parsed.plot(y=['4. close'], color='black', ax=ax)
parsed.plot(y=[signal_sma], color='blue', ax=ax)
parsed.plot(y=['bought'], style='go', ax=ax)
parsed.plot(y=['sold'], style='ro', ax=ax)

plt.show()
