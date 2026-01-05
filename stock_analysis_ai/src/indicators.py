import pandas as pd
import numpy as np

def calculate_indicators(df, settings):
    """
    Calculates technical indicators for a given DataFrame without external TA libraries.
    Supports Python 3.14+.
    """
    df = df.sort_index()

    # --- SMA ---
    df[f"SMA_{settings['ma_short']}"] = df['Close'].rolling(window=settings['ma_short']).mean()
    df[f"SMA_{settings['ma_long']}"] = df['Close'].rolling(window=settings['ma_long']).mean()

    # --- RSI ---
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=settings['rsi_window']).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=settings['rsi_window']).mean()
    rs = gain / loss
    df[f"RSI_{settings['rsi_window']}"] = 100 - (100 / (100 + rs))

    # --- MACD ---
    ema_fast = df['Close'].ewm(span=settings['macd_fast'], adjust=False).mean()
    ema_slow = df['Close'].ewm(span=settings['macd_slow'], adjust=False).mean()
    macd_val = ema_fast - ema_slow
    signal_line = macd_val.ewm(span=settings['macd_signal'], adjust=False).mean()
    
    df[f"MACD_{settings['macd_fast']}_{settings['macd_slow']}_{settings['macd_signal']}"] = macd_val
    df[f"MACDs_{settings['macd_fast']}_{settings['macd_slow']}_{settings['macd_signal']}"] = signal_line

    return df
