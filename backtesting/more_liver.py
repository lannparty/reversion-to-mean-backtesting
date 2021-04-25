import pandas as pd
import numpy as np
import json
import math
import matplotlib.pyplot as plt
import sys
from datetime import datetime

# Dollar cost average at above 10 day sma starting at quantile below 200 SMA in chunks and trailing stop loss at cross.
def more_liver_test(tickers, signal, short_term_signal, chunk_size, rarity, trailing_stop_loss):
    with open('data/raw/IBM.json') as file:
        data = json.loads(file.read())

    parsed = pd.DataFrame(data["Time Series (Daily)"])
    parsed = parsed.T[[]].astype(float)
    parsed = parsed.iloc[::-1]

    black_swan = {}

    with open('data/raw/' + market_indicator + '.json') as file:
        data = json.loads(file.read())

    raw = pd.DataFrame(data["Time Series (Daily)"])
    raw = raw.T[['4. close']].astype(float)
    raw = raw.iloc[::-1]

    parsed[market_indicator] = raw['4. close']

    market_signal_sma = market_indicator + ' SMA(' + market_signal + ')'
    market_signal_sma_delta = market_indicator + ' SMA(' + market_signal + ') Delta'

    parsed[market_signal_sma] = parsed[market_indicator].rolling(int(market_signal)).mean()
    parsed[market_signal_sma_delta] = (parsed[market_indicator] - parsed[market_signal_sma]) / parsed[market_indicator]
    parsed = parsed[parsed[market_signal_sma].notna()]

    for ticker in tickers:
        with open('data/raw/' + ticker + '.json') as file:
            data = json.loads(file.read())

        raw = pd.DataFrame(data["Time Series (Daily)"])
        raw = raw.T[['4. close']].astype(float)
        raw = raw.iloc[::-1]

        parsed[ticker] = raw['4. close']

        signal_sma = ticker + ' SMA(' + signal + ')'
        signal_sma_delta = ticker + ' SMA(' + signal + ') Delta'
        short_term_signal_sma = ticker + ' SMA(' + short_term_signal + ')' 

        parsed[signal_sma] = parsed[ticker].rolling(int(signal)).mean()
        parsed[signal_sma_delta] = (parsed[ticker] - parsed[signal_sma]) / parsed[ticker]
        parsed[short_term_signal_sma] = parsed[ticker].rolling(int(short_term_signal)).mean()
        parsed = parsed[parsed[signal_sma].notna()]

        black_swan[ticker] = parsed[parsed[signal_sma_delta] < 0].dropna()[signal_sma_delta].quantile(rarity)

    balance = 1000000.00
    total_assets = 0
    shares = {}
    buy_point = {}
    previous_bought_price = {}
    previous_close = {}
    stop_loss = {}

    for ticker in tickers:
        stop_loss[ticker] = 0
        shares[ticker] = 0

    for row_index, row_value in parsed.iterrows():
        if datetime.strptime(row_index, '%Y-%m-%d') < start_date:
            parsed = parsed.drop(row_index)
        if datetime.strptime(row_index, '%Y-%m-%d') > end_date:
            parsed = parsed.drop(row_index)

    for row_index, row_value in parsed.iterrows():
        total_assets = 0
        for share_name, share_quantity in shares.items():
            total_assets += (share_quantity * row_value[share_name])

        total_assets += balance
            
        chunk = round((total_assets * chunk_size), 2)
        for ticker in tickers:
            if ticker == 'SPY':
                continue
            price = row_value[ticker]
            signal_sma = ticker + ' SMA(' + signal + ')'
            short_term_signal_sma = ticker + ' SMA(' + short_term_signal + ')'
            buy_point[ticker] = round(row_value[signal_sma] + (price * black_swan[ticker]), 2)
            shares_to_buy = math.floor(chunk / price)

            if shares[ticker] == 0 and balance > chunk and row_value['SPY'] > row_value['SPY SMA(200)']:
                if price < buy_point[ticker] and price:
                    shares_to_buy = math.floor(chunk / price)

                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy
                    previous_bought_price[ticker] = price

                    parsed.loc[row_value.name, ticker + ' bought'] = price
                    #print("Total Assets", total_assets, "Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "now own", shares[ticker], "shares", row_index)

            elif shares[ticker] > 0:
                if price < stop_loss[ticker]:
                    balance += round((shares[ticker] * price), 2)
                    shares[ticker] = 0
                    stop_loss[ticker] = 0

                    parsed.loc[row_value.name, ticker + ' sold'] = price
                    #print("Total Assets", total_assets, "sold", shares[ticker], "shares of", ticker, "at", price, "per shares", "total", round((shares[ticker] * price), 2))

                if price < previous_bought_price[ticker] and balance > chunk and price > row_value[short_term_signal_sma] and row_value['SPY'] > row_value['SPY SMA(200)']:
                    shares_to_buy = math.floor(chunk / price)
                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy
                    previous_bought_price[ticker] = price
                    
                    parsed.loc[row_value.name, ticker + ' bought'] = price
                    #print("Total Assets", total_assets, "Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "now own", shares[ticker], "shares", row_index)

                if price > (row_value[signal_sma] + (row_value[signal_sma] * trailing_stop_loss)) and shares[ticker] > 0 and price > previous_close[ticker]:
                    stop_loss[ticker] = price
            
            #print("Total Assets", total_assets, ticker, "Price:", row_value[ticker], "Balance:", round(balance, 2), "Shares:", shares, "Chunk:", chunk, "buy_point", buy_point, row_index)
            
            if ticker in previous_close.keys():
                print("HELLO", previous_close[ticker], round(row_value[signal_sma], 2), row_value[ticker], range(1.00, round(row_value[signal_sma], 2), .01))
                #if row_value[ticker] in range(previous_close[ticker], round(row_value[signal_sma], 2), .01):
            #    parsed.loc[row_value.name, ticker + ' cross'] = row_value[signal_sma]
                #    print("HELLO")

            previous_close[ticker] = price
    return parsed

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

tickers = ['IBM']
signal = str(200)
short_term_signal = str(10)
chunk_size = .1
rarity = .5
trailing_stop_loss = .01

market_indicator = 'SPY'
market_signal = str(200)

start_date = datetime.strptime("2011-02-03", '%Y-%m-%d')
end_date = datetime.strptime("2015-02-03", '%Y-%m-%d')

parsed = more_liver_test(tickers, signal, short_term_signal, chunk_size, rarity, trailing_stop_loss)

fig, ax = plt.subplots()

#for ticker in tickers:
#    parsed.plot(y=[ticker], color='black', ax=ax)
#    parsed.plot(y=[ticker + ' SMA(' + signal + ')'], color='blue', ax=ax)
#    parsed.plot(y=[ticker + ' SMA(' + short_term_signal + ')'], color='blue', ax=ax)
#    if (ticker + ' bought') in parsed.columns:
#        parsed.plot(y=[ticker + ' bought'], style='go', ax=ax)
#    if (ticker + ' sold') in parsed.columns:
#        parsed.plot(y=[ticker + ' sold'], style='ro', ax=ax)
#
#parsed.plot(y=[market_indicator], color='orange', ax=ax)
#parsed.plot(y=[market_indicator + ' SMA(' + signal + ')'], color='purple', ax=ax)
#
#plt.show()
