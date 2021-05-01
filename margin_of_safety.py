'''
Prefer smallcap
Low PE ratio
Reasonable Debt Ratio
'''
import json
import pandas as pd
from os import path

with open('data/stocks.json') as json_file:
    data = json.load(json_file)

for ticker in data["data"]["rows"]:
    if path.exists("data/balance-sheet/" + ticker["symbol"] + ".out") and path.exists("data/cash-flow/" + ticker["symbol"] + ".out") and ticker["symbol"] == 'AAPL':
        market_cap = ticker["marketCap"]
        df = pd.read_csv("data/income-statement/" + ticker["symbol"] + ".out")
        total_revenue = df["TotalRevenue"].tail(1).values[::-1][0]
        df = pd.read_csv("data/balance-sheet/" + ticker["symbol"] + ".out")
        current_assets = df[["CurrentAssets", "TotalNonCurrentLiabilitiesNetMinorityInterest"]].tail(1).values[::-1][0][0]
        non_current_liabilities= df[["CurrentAssets", "TotalNonCurrentLiabilitiesNetMinorityInterest"]].tail(1).values[::-1][0][1]
        df = pd.read_csv("data/cash-flow/" + ticker["symbol"] + ".out")
        net_income = df["NetIncome"].tail(1).values[::-1][0]

        print("symbol", ticker["symbol"])
        print("marketcap", ticker["marketCap"])
        print("lastsale", ticker["lastsale"])
        print("netincome", net_income)
        print("currentassets", current_assets)
        print("noncurrentliabilities", non_current_liabilities)
        print("totalrevenue", total_revenue)
        print("marketcap", market_cap)