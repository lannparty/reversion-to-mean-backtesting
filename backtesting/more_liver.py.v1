import pandas as pd
import numpy as np
import json
import math
import matplotlib.pyplot as plt


## Pyramid up, trailing stoploss.
#def more_liver_test(dataframe, mean_below_SMA_200, trailing_stop_loss, short_term_signal):
#    balance = 100000.00
#    shares = 0
#    stop_loss = 0
#    line = None
#    chunk = None
#    chunk_counter = 5
#    next_buy_price = 0
#    previous_close = None
#
#    for row_index, row_value in dataframe.iterrows():
#        price = row_value['4. close']
#        short_term_sma = round(row_value[short_term_signal], 2)
#        sma_200 = round(row_value['SMA(200)'], 2)
#        sma_200_buy_point = round((sma_200 + (price * mean_below_SMA_200)), 2)
#
#        if shares == 0:
#            if price < sma_200_buy_point and price > short_term_sma and price > next_buy_price and chunk_counter > 0:
#                if line == None:
#                    line = math.floor((balance/price))
#
#                if chunk == None:
#                    chunk = math.floor(line / 5)
#
#                balance -= round((chunk * price), 2)
#                shares += chunk
#                stop_loss = round((price - (price * trailing_stop_loss)), 2)
#                next_buy_price = round(price + (price * .01), 2)
#                chunk_counter -= 1
#                #print("bought", chunk, "shares", "at price", price, "chunk number", 5 - chunk_counter, "stop loss at", stop_loss, "now own", shares, "shares")
#                dataframe.loc[row_value.name, 'bought'] = price
#        elif shares > 0:
#            if price > short_term_sma and price > next_buy_price and chunk_counter > 0:
#                if line == None:
#                    line = math.floor((balance/price))
#
#                if chunk == None:
#                    chunk = math.floor(line / 5)
#
#                balance -= round((chunk * price), 2)
#                shares += chunk
#                stop_loss = round((price - (price * trailing_stop_loss)), 2)
#                next_buy_price = round(price + (price * .01), 2)
#                chunk_counter -= 1
#                #print("bought", chunk, "shares", "at price", price, "chunk number", 5 - chunk_counter, "stop loss at", stop_loss, "now own", shares, "shares")
#                dataframe.loc[row_value.name, 'bought'] = price
#
#            elif price < stop_loss and shares > 0:
#                balance += round((shares * price), 2)
#                #print("sold", shares, "shares at", price, "per shares", "total", round((shares* price), 2))
#                line = None
#                chunk = None
#                shares = 0
#                chunk_counter = 5            
#                next_buy_price = 0
#                dataframe.loc[row_value.name, 'sold'] = price
#
#        if shares > 0 and price > previous_close:
#            new_stop_loss = round((price - (price * trailing_stop_loss)), 2)
#            if new_stop_loss > stop_loss:
#                stop_loss = new_stop_loss
#        
#        #print("Price:", row_value['4. close'], "Balance:", round(balance, 2), "Shares:", shares, "Stop Loss:", stop_loss, "Line:", line, "Chunk:", chunk, "Next Buy Price", next_buy_price, "Previous close", previous_close, "buy_point", sma_200_buy_point)
#        previous_close = price
#    return dataframe

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

## Sell at 200 SMA cross, with chunks.
#def more_liver_test(dataframe, mean_below_SMA_200, trailing_stop_loss):
#    balance = 100000.00
#    shares = 0
#    line = None
#    chunk = None
#    next_buy_price = 0
#    previous_close = None
#
#    for row_index, row_value in dataframe.iterrows():
#        price = row_value['4. close']
#        sma_200 = round(row_value['SMA(200)'], 2)
#        sma_200_buy_point = round((sma_200 + (price * mean_below_SMA_200)), 2)
#
#        if price < sma_200_buy_point and shares == 0:
#            if line == None:
#                line = math.floor((balance/price))
#
#            balance -= round((line * price), 2)
#            shares += line
#            dataframe.loc[row_value.name, 'bought'] = price
#
#        elif price > sma_200 and shares > 0:
#            balance += round((shares * price), 2)
#            line = None
#            shares = 0
#            dataframe.loc[row_value.name, 'sold'] = price
#
#        print("Price:", row_value['4. close'], "Balance:", round(balance, 2), "Shares:", shares, "Line:", line, "Next Buy Price", next_buy_price, "Previous close", previous_close, "buy_point", sma_200_buy_point)
#        previous_close = price
#    return dataframe

with open('data/raw/IBM.json') as file:
    data = json.loads(file.read())

raw = pd.DataFrame(data["Time Series (Daily)"])
parsed = raw.T[['4. close']].astype(float)
parsed = parsed.iloc[::-1]

parsed['SMA(10)'] = parsed['4. close'].rolling(10).mean()
parsed['SMA(20)'] = parsed['4. close'].rolling(20).mean()
parsed['SMA(50)'] = parsed['4. close'].rolling(50).mean()
parsed['SMA(100)'] = parsed['4. close'].rolling(100).mean()
parsed['SMA(200)'] = parsed['4. close'].rolling(200).mean()

parsed['SMA(10) Delta'] = (parsed['4. close'] - parsed['SMA(10)']) / parsed['4. close']
parsed['SMA(20) Delta'] = (parsed['4. close'] - parsed['SMA(20)']) / parsed['4. close']
parsed['SMA(50) Delta'] = (parsed['4. close'] - parsed['SMA(50)']) / parsed['4. close']
parsed['SMA(100) Delta'] = (parsed['4. close'] - parsed['SMA(100)']) / parsed['4. close']
parsed['SMA(200) Delta'] = (parsed['4. close'] - parsed['SMA(200)']) / parsed['4. close']

parsed = parsed[parsed['SMA(200)'].notna()]

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

signal = 'SMA(200)'

parsed = more_liver_test(parsed, signal)

fig, ax = plt.subplots()
parsed.plot(y=['4. close'], color='black', ax=ax)
parsed.plot(y=[signal], color='blue', ax=ax)
parsed.plot(y=['bought'], style='go', ax=ax)
parsed.plot(y=['sold'], style='ro', ax=ax)

plt.show()
