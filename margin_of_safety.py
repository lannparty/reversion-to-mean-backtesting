'''
Prefer smallcap
Low PE ratio
Reasonable Debt Ratio
'''
import json
import pandas as pd
from os import path

safe = {}

with open('data/stocks.json') as json_file:
    data = json.load(json_file)

for ticker in data["data"]["rows"]:
        if (path.exists("data/income-statement/" + ticker["symbol"] + ".out")
        and path.exists("data/balance-sheet/" + ticker["symbol"] + ".out") 
        and path.exists("data/cash-flow/" + ticker["symbol"] + ".out")):

            income_statement = pd.read_csv("data/income-statement/" + ticker["symbol"] + ".out")
            balance_sheet = pd.read_csv("data/balance-sheet/" + ticker["symbol"] + ".out")

        if (ticker["marketCap"] != 0 and ticker["marketCap"] != ""
        and "TotalRevenue" in income_statement
        and "NetIncome" in income_statement
        and "CurrentAssets" in balance_sheet
        and "TotalNonCurrentLiabilitiesNetMinorityInterest" in balance_sheet):

            market_cap = ticker["marketCap"]
            total_revenue = income_statement["TotalRevenue"].tail(1).values[::-1][0]
            current_assets = balance_sheet[["CurrentAssets", "TotalNonCurrentLiabilitiesNetMinorityInterest"]].tail(1).values[::-1][0][0]
            non_current_liabilities = balance_sheet[["CurrentAssets", "TotalNonCurrentLiabilitiesNetMinorityInterest"]].tail(1).values[::-1][0][1]
            net_income = income_statement["NetIncome"].tail(1).values[::-1][0]

        if (total_revenue != 0 and total_revenue > 0
        and current_assets != 0 and current_assets > 0
        and non_current_liabilities != 0 and non_current_liabilities > 0
        and net_income != 0 and net_income > 0):

            margins = net_income / total_revenue
            solvency = current_assets / non_current_liabilities
            pe_ratio = float(market_cap) / net_income
            if (float(market_cap) > 10000000000
            and margins > .2
            and solvency > 1
            and pe_ratio > 1 and pe_ratio < 10):
                safe[ticker["symbol"]] = "market_cap: " + market_cap + " margins: " + str(margins) + " solvency: " + str(solvency) + " pe_ratio: " + str(pe_ratio)
    
for ticker, fundamentals in safe.items():
    print(ticker)
    print(fundamentals)