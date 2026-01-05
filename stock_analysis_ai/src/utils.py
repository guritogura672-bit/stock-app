import yaml
import os
import sys

def load_config(config_path="config.yaml"):
    """
    Loads configuration from a YAML file.
    Works for Local, Streamlit Cloud, and EXE.
    """
    # 0. プログラムがある場所からの絶対パスを計算
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, config_path)

    # 1. 絶対パスでチェック
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # 2. 現在の実行ディレクトリをチェック
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # 3. EXE化されている場合
    if getattr(sys, 'frozen', False):
        bundle_dir = getattr(sys, '_MEIPASS', base_dir)
        bundled_path = os.path.join(bundle_dir, config_path)
        if os.path.exists(bundled_path):
            with open(bundled_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

    # 4. 【最強の予備】ファイルがなくてもデフォルト値で起動させる
    return {
        'tickers': ['7203.T', '9984.T', 'AAPL', 'NVDA'],
        'settings': {
            'period': '1y', 'interval': '1d',
            'ma_short': 25, 'ma_long': 75,
            'rsi_window': 14, 'macd_fast': 12,
            'macd_slow': 26, 'macd_signal': 9
        }
    }

def save_config(config, config_path="config.yaml"):
    """
    Saves the configuration dictionary to a YAML file.
    """
    # 保存時も確実に実行ファイルと同じ階層を狙う
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, config_path)
    
    with open(target_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
