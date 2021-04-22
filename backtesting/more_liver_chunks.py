import pandas as pd
import numpy as np
import json
import math
import matplotlib.pyplot as plt
import sys

# Buy at quantile below 200 SMA in chunks and sell at cross.
def more_liver_test(tickers, signal):
    with open('data/raw/IBM.json') as file:
        data = json.loads(file.read())
    parsed = pd.DataFrame(data["Time Series (Daily)"])
    parsed = parsed.T[['4. close']].astype(float)
    parsed = parsed.iloc[::-1]
    parsed = parsed.drop(columns=['4. close'])

    black_swan = {}

    for ticker in tickers:
        with open('data/raw/' + ticker + '.json') as file:
            data = json.loads(file.read())

        raw = pd.DataFrame(data["Time Series (Daily)"])
        raw = raw.T[['4. close']].astype(float)
        raw = raw.iloc[::-1]

        parsed[ticker] = raw['4. close']

        signal_sma = ticker + ' SMA(' + signal + ')'
        signal_sma_delta = ticker + ' SMA(' + signal + ') Delta'
        parsed[signal_sma] = parsed[ticker].rolling(int(signal)).mean()
        parsed[signal_sma_delta] = (parsed[ticker] - parsed[signal_sma]) / parsed[ticker]
        parsed = parsed[parsed[signal_sma].notna()]

        black_swan[ticker] = parsed[parsed[signal_sma_delta] < 0].dropna()[signal_sma_delta].quantile(.1)

    balance = 100000.00
    chunk = 5000.00
    shares = {}
    next_buy_price = {}
    chunk_counter = {}
    buy_point = {}

    for ticker in tickers:
        shares[ticker] = 0
        next_buy_price[ticker] = 0
        chunk_counter[ticker] = 5

    for row_index, row_value in parsed.iterrows():
        for ticker in tickers:
            price = row_value[ticker]
            signal_sma = ticker + ' SMA(' + signal + ')'
            buy_point[ticker] = round(row_value[signal_sma] + (price * black_swan[ticker]), 2)
            shares_to_buy = math.floor(chunk / price)

            if shares[ticker] == 0 and balance > chunk:
                if price < buy_point[ticker] and price > next_buy_price[ticker] and chunk_counter[ticker] > 0:
                    shares_to_buy = math.floor(chunk / price)

                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy

                    next_buy_price[ticker] = round(price + (price * .01), 2)
                    chunk_counter[ticker] -= 1
                    parsed.loc[row_value.name, ticker + 'bought'] = price
                    print("Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "chunk number", 5 - chunk_counter[ticker], "now own", shares[ticker], "shares", row_index)

            elif shares[ticker] > 0:
                if price > next_buy_price[ticker] and chunk_counter[ticker] > 0 and balance > chunk:

                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy

                    next_buy_price[ticker] = round(price + (price * .01), 2)
                    chunk_counter[ticker] -= 1
                    parsed.loc[row_value.name, ticker + 'bought'] = price
                    print("Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "chunk number", 5 - chunk_counter[ticker], "now own", shares[ticker], "shares", row_index)

                elif price > row_value[signal_sma] and shares[ticker] > 0:
                    print("sold", shares[ticker], "shares of", ticker, "at", price, "per shares", "total", round((shares[ticker] * price), 2))
                    balance += round((shares[ticker] * price), 2)
                    shares[ticker] = 0
                    chunk_counter[ticker] = 5            
                    next_buy_price[ticker] = 0
                    parsed.loc[row_value.name, ticker + 'sold'] = price

            print(ticker, "Price:", row_value[ticker], "Balance:", round(balance, 2), "Shares:", shares, "Chunk:", chunk, "Next Buy Price", next_buy_price, "buy_point", buy_point, row_index)
    return parsed

signal = str(200)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

tickers = ['CVS']

parsed = more_liver_test(tickers, signal)

fig, ax = plt.subplots()

for ticker in tickers:
    parsed.plot(y=[ticker], color='black', ax=ax)
    parsed.plot(y=[ticker + ' SMA(' + signal + ')'], color='blue', ax=ax)

for ticker in tickers:
    parsed.plot(y=[ticker + 'bought'], style='go', ax=ax)
    parsed.plot(y=[ticker + 'sold'], style='ro', ax=ax)

plt.show()
