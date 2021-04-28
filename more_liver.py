import pandas as pd
import numpy as np
import json
import math
import matplotlib.pyplot as plt
import sys
from datetime import datetime

def float_range(x, y):
    float_range = []
    if x < y:
        while x < y:
            float_range.append(round(x, 2))
            x += .01
    elif x > y:
        while x > y:
            float_range.append(round(y, 2))
            y += .01
    else:
        float_range.append(x)

    return float_range
# Dollar cost average at above short_term_signal sma starting at quantile below signal_sma in chunks and trailing stop loss at cross.
def long_test(tickers, signal, short_term_signal, market_indicator, market_signal, chunk_size, rarity, trailing_stop_loss, start_date, end_date):
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
    signal_cross = {}

    for ticker in tickers:
        stop_loss[ticker] = 0
        shares[ticker] = 0
        signal_cross[ticker] = 0

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
                    print("Total Assets", total_assets, "Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "now own", shares[ticker], "shares", row_index)

            elif shares[ticker] > 0:
                if price < stop_loss[ticker]:
                    balance += round((shares[ticker] * price), 2)
                    shares[ticker] = 0
                    stop_loss[ticker] = 0

                    parsed.loc[row_value.name, ticker + ' sold'] = price
                    print("Total Assets", total_assets, "sold", shares[ticker], "shares of", ticker, "at", price, "per shares", "total", round((shares[ticker] * price), 2))

                if price < previous_bought_price[ticker] and balance > chunk and price > row_value[short_term_signal_sma] and row_value['SPY'] > row_value['SPY SMA(200)']:
                    shares_to_buy = math.floor(chunk / price)
                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy
                    previous_bought_price[ticker] = price
                    
                    parsed.loc[row_value.name, ticker + ' bought'] = price
                    print("Total Assets", total_assets, "Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "now own", shares[ticker], "shares", row_index)

                if price > (row_value[signal_sma] + (row_value[signal_sma] * trailing_stop_loss)) and shares[ticker] > 0 and price > previous_close[ticker]:
                    stop_loss[ticker] = price
            
            print("Total Assets", total_assets, ticker, "Price:", row_value[ticker], "Balance:", round(balance, 2), "Shares:", shares, "Chunk:", chunk, "buy_point", buy_point, row_index)
            
            if ticker in previous_close.keys():
                if round(row_value[signal_sma], 2) in float_range(previous_close[ticker], row_value[ticker]):
                    signal_cross[ticker] += 1

            previous_close[ticker] = price
    return parsed

# Dollar cost average starting at quantile below signal_sma in chunks and trailing stop loss at cross.
def long_no_short_signal_test(tickers, signal, market_indicator, market_signal, chunk_size, rarity, trailing_stop_loss, start_date, end_date):
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

        parsed[signal_sma] = parsed[ticker].rolling(int(signal)).mean()
        parsed[signal_sma_delta] = (parsed[ticker] - parsed[signal_sma]) / parsed[ticker]
        parsed = parsed[parsed[signal_sma].notna()]

        black_swan[ticker] = parsed[parsed[signal_sma_delta] < 0].dropna()[signal_sma_delta].quantile(rarity)

    balance = 1000000.00
    total_assets = 0
    shares = {}
    buy_point = {}
    previous_bought_price = {}
    previous_close = {}
    stop_loss = {}
    signal_cross = {}

    for ticker in tickers:
        stop_loss[ticker] = 0
        shares[ticker] = 0
        signal_cross[ticker] = 0

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
            buy_point[ticker] = round(row_value[signal_sma] + (price * black_swan[ticker]), 2)
            shares_to_buy = math.floor(chunk / price)

            if shares[ticker] == 0 and balance > chunk and row_value['SPY'] > row_value['SPY SMA(200)']:
                if price < buy_point[ticker] and price:
                    shares_to_buy = math.floor(chunk / price)

                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy
                    previous_bought_price[ticker] = price

                    parsed.loc[row_value.name, ticker + ' bought'] = price
                    print("Total Assets", total_assets, "Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "now own", shares[ticker], "shares", row_index)

            elif shares[ticker] > 0:
                if price < stop_loss[ticker]:
                    balance += round((shares[ticker] * price), 2)
                    shares[ticker] = 0
                    stop_loss[ticker] = 0

                    parsed.loc[row_value.name, ticker + ' sold'] = price
                    print("Total Assets", total_assets, "sold", shares[ticker], "shares of", ticker, "at", price, "per shares", "total", round((shares[ticker] * price), 2))

                if price < previous_bought_price[ticker] and balance > chunk and row_value['SPY'] > row_value['SPY SMA(200)']:
                    shares_to_buy = math.floor(chunk / price)
                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy
                    previous_bought_price[ticker] = price
                    
                    parsed.loc[row_value.name, ticker + ' bought'] = price
                    print("Total Assets", total_assets, "Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "now own", shares[ticker], "shares", row_index)

                if price > (row_value[signal_sma] + (row_value[signal_sma] * trailing_stop_loss)) and shares[ticker] > 0 and price > previous_close[ticker]:
                    stop_loss[ticker] = price
            
            print("Total Assets", total_assets, ticker, "Price:", row_value[ticker], "Balance:", round(balance, 2), "Shares:", shares, "Chunk:", chunk, "buy_point", buy_point, row_index)
            
            if ticker in previous_close.keys():
                if round(row_value[signal_sma], 2) in float_range(previous_close[ticker], row_value[ticker]):
                    signal_cross[ticker] += 1

            previous_close[ticker] = price
    return parsed

# Dollar cost average starting at quantile below signal_sma in chunks and sell at quantile above signal_sma.
def long_greedy_test(tickers, signal, market_indicator, market_signal, chunk_size, below_rarity, above_rarity, trailing_stop_loss, start_date, end_date):
    with open('data/raw/IBM.json') as file:
        data = json.loads(file.read())

    parsed = pd.DataFrame(data["Time Series (Daily)"])
    parsed = parsed.T[[]].astype(float)
    parsed = parsed.iloc[::-1]

    black_swan_below = {}
    black_swan_above = {}

    with open('data/raw/' + market_indicator + '.json') as file:
        data = json.loads(file.read())

    raw = pd.DataFrame(data["Time Series (Daily)"])
    raw = raw.T[['4. close']].astype(float)
    raw = raw.iloc[::-1]

    parsed[market_indicator] = raw['4. close']

    for row_index, row_value in parsed.iterrows():
        if datetime.strptime(row_index, '%Y-%m-%d') < start_date:
            parsed = parsed.drop(row_index)
        if datetime.strptime(row_index, '%Y-%m-%d') > end_date:
            parsed = parsed.drop(row_index)

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

        parsed[signal_sma] = parsed[ticker].rolling(int(signal)).mean()
        parsed[signal_sma_delta] = (parsed[ticker] - parsed[signal_sma]) / parsed[ticker]
        parsed = parsed[parsed[signal_sma].notna()]

        black_swan_below[ticker] = parsed[parsed[signal_sma_delta] < 0].dropna()[signal_sma_delta].quantile(below_rarity)
        black_swan_above[ticker] = parsed[parsed[signal_sma_delta] > 0].dropna()[signal_sma_delta].quantile(above_rarity)

    return(black_swan_below[ticker], black_swan_above[ticker])

    balance = 1000000.00
    total_assets = 0
    shares = {}
    buy_point = {}
    sell_point = {}
    previous_bought_price = {}
    previous_close = {}
    stop_loss = {}
    signal_cross = {}

    for ticker in tickers:
        stop_loss[ticker] = 0
        shares[ticker] = 0
        signal_cross[ticker] = 0

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
            buy_point[ticker] = round(row_value[signal_sma] + (price * black_swan_below[ticker]), 2)
            sell_point[ticker] = round(row_value[signal_sma] + (price * black_swan_above[ticker]), 2)
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

                if price < previous_bought_price[ticker] and balance > chunk and row_value['SPY'] > row_value['SPY SMA(200)']:
                    shares_to_buy = math.floor(chunk / price)
                    balance -= round((shares_to_buy * price), 2)
                    shares[ticker] += shares_to_buy
                    previous_bought_price[ticker] = price
                    
                    parsed.loc[row_value.name, ticker + ' bought'] = price
                    #print("Total Assets", total_assets, "Balance", balance, "bought", shares_to_buy, "shares of", ticker, "at price", price, "now own", shares[ticker], "shares", row_index)

                if price > (sell_point[ticker] + (row_value[signal_sma] * trailing_stop_loss)) and shares[ticker] > 0 and price > previous_close[ticker]:
                    stop_loss[ticker] = price
            
            #print("Total Assets", total_assets, ticker, "Price:", row_value[ticker], "Balance:", round(balance, 2), "Shares:", shares, "Chunk:", chunk, "buy_point", buy_point, row_index)
            
            if ticker in previous_close.keys():
                if round(row_value[signal_sma], 2) in float_range(previous_close[ticker], row_value[ticker]):
                    signal_cross[ticker] += 1

            previous_close[ticker] = price
    return parsed

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

tickers = ['ILMN']
signal = str(70)
short_term_signal = str(5)
chunk_size = .10
rarity = .5
trailing_stop_loss = .01
rarity_below = .5
rarity_above = .5

market_indicator = 'SPY'
market_signal = str(200)

std_above = {}
std_below = {}

for signal in range(10, 150):
    signal = str(signal)
    date_range = {
        "2001-02-03":"2005-02-03",
        "2003-02-03":"2007-02-03",
        "2005-02-03":"2010-02-03",
        "2007-02-03":"2012-02-03",
        "2010-02-03":"2015-02-03",
        "2012-02-03":"2017-02-03",
        "2015-02-03":"2020-02-03"
        }

    above_list = []
    below_list = []

    for start, end in date_range.items():
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')
        #parsed = long_test(tickers, signal, short_term_signal, market_indicator, market_signal, chunk_size, rarity, trailing_stop_loss, start, end)
        #parsed = long_no_short_signal_test(tickers, signal, market_indicator, market_signal, chunk_size, rarity, trailing_stop_loss, start, end)
        #parsed = long_greedy_test(tickers, signal, market_indicator, market_signal, chunk_size, rarity_below, rarity_above, trailing_stop_loss, start, end)
        below, above = long_greedy_test(tickers, signal, market_indicator, market_signal, chunk_size, rarity_below, rarity_above, trailing_stop_loss, start, end)
        below_list.append(below)
        above_list.append(above)

    std_below[signal + 'below'] = np.std(below_list)
    std_above[signal + 'above'] = np.std(above_list)

print(std_below)
print(std_above)

#std_avg = (std_above + std_below) / 2
#print(std_avg)

#fig, ax = plt.subplots()
#
#for ticker in tickers:
#    parsed.plot(y=[ticker], color='black', ax=ax)
#    parsed.plot(y=[ticker + ' SMA(' + signal + ')'], color='blue', ax=ax)
#    #parsed.plot(y=[ticker + ' SMA(' + short_term_signal + ')'], color='blue', ax=ax)
#    if (ticker + ' bought') in parsed.columns:
#        parsed.plot(y=[ticker + ' bought'], style='go', ax=ax)
#    if (ticker + ' sold') in parsed.columns:
#        parsed.plot(y=[ticker + ' sold'], style='ro', ax=ax)
#
#parsed.plot(y=[market_indicator], color='orange', ax=ax)
#parsed.plot(y=[market_indicator + ' SMA(' + market_signal + ')'], color='purple', ax=ax)
#
#plt.show()
#