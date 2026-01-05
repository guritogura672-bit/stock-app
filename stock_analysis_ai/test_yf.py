import yfinance as yf
import pandas as pd

def test_fetch():
    tickers_1 = ["7203.T"]
    tickers_2 = ["7203.T", "9984.T"]
    
    print("--- Testing 1 ticker ---")
    df1 = yf.download(tickers_1[0], period="1d", auto_adjust=True)
    print(f"Columns for 1 ticker ({tickers_1[0]}):")
    print(df1.columns)
    # print(df1.head())
    
    print("\n--- Testing 2 tickers ---")
    df2 = yf.download(tickers_2, period="1d", group_by='ticker', auto_adjust=True)
    print(f"Columns for 2 tickers:")
    print(df2.columns)
    if "7203.T" in df2:
        print(f"Columns for df2['7203.T']:")
        print(df2["7203.T"].columns)

if __name__ == "__main__":
    test_fetch()
