import pandas as pd
import numpy as np
import json
import math
import matplotlib.pyplot as plt
import sys

# Buy at quantile below 200 SMA in chunks and sell at cross.
def more_liver_test(tickers, signal):
    for ticker in tickers:
        with open('data/raw/' + ticker + '.json') as file:
            data = json.loads(file.read())

        raw = pd.DataFrame(data["Time Series (Daily)"])
        parsed = raw.T[['4. close']].astype(float)
        parsed = parsed.iloc[::-1]

        parsed = parsed.rename(columns={'4. close': ticker})
        signal_sma = ticker + ' SMA(' + signal + ')'
        signal_sma_delta = ticker + ' SMA(' + signal + ') Delta'
        parsed[signal_sma] = parsed[ticker].rolling(int(signal)).mean()
        parsed[signal_sma_delta] = (parsed[ticker] - parsed[signal_sma]) / parsed[ticker]
        parsed = parsed[parsed[signal_sma].notna()]

    #balance = 100000.00
    #shares = 0
    #line = None
    #chunk = None
    #chunk_counter = 5
    #next_buy_price = 0
    #previous_close = None

    #black_swan = parsed[parsed[signal_sma_delta] < 0].dropna()[signal_sma_delta].quantile(.1)

    #for row_index, row_value in parsed.iterrows():
    #    price = row_value[ticker]
    #    buy_point = round(row_value[signal_sma] + (price * black_swan), 2)

    #    if shares == 0:
    #        if price < buy_point and price > next_buy_price and chunk_counter > 0:
    #            if line == None:
    #                line = math.floor((balance/price))

    #            if chunk == None:
    #                chunk = math.floor(line / 5)

    #            balance -= round((chunk * price), 2)
    #            shares += chunk
    #            next_buy_price = round(price + (price * .01), 2)
    #            chunk_counter -= 1
    #            parsed.loc[row_value.name, 'bought'] = price
    #            #print("bought", chunk, "shares", "at price", price, "chunk number", 5 - chunk_counter, "now own", shares, "shares", line, "line")
    #    elif shares > 0:
    #        if price > next_buy_price and chunk_counter > 0:
    #            if line == None:
    #                line = math.floor((balance/price))

    #            if chunk == None:
    #                chunk = math.floor(line / 5)

    #            balance -= round((chunk * price), 2)
    #            shares += chunk
    #            next_buy_price = round(price + (price * .01), 2)
    #            chunk_counter -= 1
    #            parsed.loc[row_value.name, 'bought'] = price
    #            #print("bought", chunk, "shares", "at price", price, "chunk number", 5 - chunk_counter, "now own", shares, "shares")

    #        elif price > row_value[signal_sma] and shares > 0:
    #            #print("sold", shares, "shares at", price, "per shares", "total", round((shares* price), 2))
    #            balance += round((shares * price), 2)
    #            line = None
    #            chunk = None
    #            shares = 0
    #            chunk_counter = 5            
    #            next_buy_price = 0
    #            parsed.loc[row_value.name, 'sold'] = price

    #    #print("Price:", row_value[ticker], "Balance:", round(balance, 2), "Shares:", shares, "Line:", line, "Chunk:", chunk, "Next Buy Price", next_buy_price, "Previous close", previous_close, "buy_point", buy_point)
    #    previous_close = price
    return parsed

signal = str(200)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

tickers = ['IBM', 'MDC', 'MFT', 'MCRI']
#for ticker in targets:
#    parsed = more_liver_test(ticker, signal)

parsed = more_liver_test(tickers, signal)
print(parsed)

#fig, ax = plt.subplots()
#parsed.plot(y=['4. close'], color='black', ax=ax)
#parsed.plot(y=[short_term_signal_sma], color='blue', ax=ax)
#parsed.plot(y=[signal_sma], color='blue', ax=ax)
#parsed.plot(y=['bought'], style='go', ax=ax)
#parsed.plot(y=['sold'], style='ro', ax=ax)

#plt.show()
