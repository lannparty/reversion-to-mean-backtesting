import pathlib
import json
import sys
from os import path
import pandas as pd

from yahooquery import Ticker


def get_symbols():
    stocks_json = pathlib.Path(__file__).parent / "stocks.json"
    symbols = []
    with open(stocks_json, "r") as f:
        stocks = json.load(f)
        for stock in stocks["data"]["rows"]:
            symbol = stock["symbol"]
            if symbol.isalpha():
                symbols.append(symbol)
    return symbols

if __name__ == "__main__":
    symbols = get_symbols()

    if path.exists("financials-unavailable/income-statement-unavailable.json"):
        with open("financials-unavailable/income-statement-unavailable.json") as target:
            income_statement_unavailable = json.load(target)
    else:
        income_statement_unavailable = {}

    if path.exists("financials-unavailable/balance-sheet-unavailable.json"):
        with open("financials-unavailable/balance-sheet-unavailable.json") as target:
            balance_sheet_unavailable = json.load(target)
    else:
        balance_sheet_unavailable = {}

    if path.exists("financials-unavailable/cash-flow-unavailable.json"):
        with open("financials-unavailable/cash-flow-unavailable.json") as target:
            cash_flow_unavailable = json.load(target)
    else:
        cash_flow_unavailable = {}
    
    if len(income_statement_unavailable) == 0:
        for symbol in symbols:
           income_statement_unavailable[symbol] = False 
    if len(balance_sheet_unavailable) == 0:
        for symbol in symbols:
           balance_sheet_unavailable[symbol] = False 
    if len(cash_flow_unavailable) == 0:
        for symbol in symbols:
           cash_flow_unavailable[symbol] = False 

    for symbol in symbols:
        print(symbol)
        NASDAQ = Ticker(symbol, validate=True, progress=True)
        if not path.exists("income-statement/" + symbol + ".out") and income_statement_unavailable[symbol] == False:
            income_statement = NASDAQ.income_statement()
            print(income_statement)
            if isinstance(income_statement, pd.DataFrame):
                income_statement.to_csv("income-statement/" + symbol + ".out")
            elif "Income Statement data unavailable for" in income_statement:
                income_statement_unavailable[symbol] = True
                with open('financials-unavailable/income-statement-unavailable.json', 'w+') as target:
                    json.dump(income_statement_unavailable, target)
                    target.close()
            else:
                break

        if not path.exists("balance-sheet/" + symbol + ".out") and balance_sheet_unavailable[symbol] == False:
            balance_sheet = NASDAQ.balance_sheet()
            print(balance_sheet)
            if isinstance(balance_sheet, pd.DataFrame):
                balance_sheet.to_csv("balance-sheet/" + symbol + ".out")
            elif "Balance Sheet data unavailable for" in balance_sheet:
                balance_sheet_unavailable[symbol] = True
                with open('financials-unavailable/balance-sheet-unavailable.json', 'w+') as target:
                    json.dump(balance_sheet_unavailable, target)
                    target.close()
            else:
                break

        if not path.exists("cash-flow/" + symbol + ".out") and cash_flow_unavailable[symbol] == False:
            cash_flow = NASDAQ.cash_flow()
            print(cash_flow)
            if isinstance(cash_flow, pd.DataFrame):
                cash_flow.to_csv("cash-flow/" + symbol + ".out")
            elif "Cash Flow data unavailable for" in cash_flow:
                cash_flow_unavailable[symbol] = True
                with open('financials-unavailable/cash-flow-unavailable.json', 'w+') as target:
                    json.dump(cash_flow_unavailable, target)
                    target.close()
            else:
                break

