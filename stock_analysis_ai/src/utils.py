import yaml
import os
import sys

def load_config(config_path="config.yaml"):
    """
    設定ファイルを読み込む関数。
    PC、スマホ公開用、EXEのすべてに対応。
    """
    # 1. プログラムの場所を基準にファイルを探す（最も確実）
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, config_path)

    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # 2. 現在開いている場所をチェック
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # 3. 万が一ファイルがない場合の「予備データ」
    # これがあれば、ファイルがなくてもエラーにならずに起動します
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
    設定を保存する関数。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, config_path)
    
    with open(target_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
