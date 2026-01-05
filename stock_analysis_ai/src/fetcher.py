import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(tickers, period="1y", interval="1d"):
    """
    Fetches historical stock data and company names.
    Returns: (dict of DataFrames, dict of company names)
    """
    data = {}
    names = {}
    
    if not tickers:
        return data, names
        
    print(f"Fetching data and names for: {tickers}")
    
    try:
        # Ensure tickers is a list
        if isinstance(tickers, str):
            tickers = [tickers]

        # 常に group_by='ticker' を指定して、一貫したデータ構造の取得を試みる
        df = yf.download(tickers, period=period, interval=interval, group_by='ticker', auto_adjust=True, threads=True, progress=False)
        
        if df is None or df.empty:
            print("No data received from yfinance.")
            return data, names

        for ticker in tickers:
            ticker_df = None
            
            # 1. データの抽出
            if isinstance(df.columns, pd.MultiIndex):
                # group_by='ticker' の場合は第1レベルがティッカー名
                if ticker in df.columns.levels[0]:
                    try:
                        ticker_df = df[ticker].copy()
                    except KeyError:
                        continue
            else:
                # 銘柄が1つで、かつ yfinance が MultiIndex を返さなかった場合
                if len(tickers) == 1:
                    ticker_df = df.copy()

            # 2. データのクリーンアップ
            if ticker_df is not None and not ticker_df.empty:
                # 列を確実に1階層（Open, High, Low, Close, Volume）にする
                if isinstance(ticker_df.columns, pd.MultiIndex):
                    ticker_df.columns = ticker_df.columns.get_level_values(-1)
                
                # 重複する列名があれば最初のものだけを残す（これが重要）
                ticker_df = ticker_df.loc[:, ~ticker_df.columns.duplicated()]
                
                # インデックスがDatetimeでない場合は変換を試みる（yfinanceのバージョンによる）
                if not isinstance(ticker_df.index, pd.DatetimeIndex):
                    ticker_df.index = pd.to_datetime(ticker_df.index)
                
                # 必要な列が揃っているかチェック
                if 'Close' in ticker_df.columns:
                    ticker_df.dropna(subset=['Close'], inplace=True)
                    if not ticker_df.empty:
                        data[ticker] = ticker_df


        # 2. 会社名の取得
        for ticker in tickers:
            try:
                t = yf.Ticker(ticker)
                # get_info() は遅いので、見つかればラッキー程度に処理
                info = t.info
                name = info.get('longName') or info.get('shortName') or ticker
                names[ticker] = name
            except:
                names[ticker] = ticker

    except Exception as e:
        print(f"Error in fetch_stock_data: {e}")
    
    # 明示的に2つの要素を持つタプルを返す
    return (data, names)
