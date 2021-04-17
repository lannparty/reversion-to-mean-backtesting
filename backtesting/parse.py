import pandas as pd
import numpy as np
import json
import os

for target in os.listdir('data/raw'):
    print("Parsing", target)
    with open('data/raw/' + target) as file:
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

    parsed.to_csv('data/parsed/' + target)
