import subprocess
import sys
import os

def check_and_install():
    print("--- 準備中 (Checking requirements) ---")
    required_packages = [
        "streamlit", "pandas", "yfinance", 
        "plotly", "rich", "pyyaml", "streamlit-autorefresh"
    ]
    
    for pkg in required_packages:
        module_name = pkg if pkg != "pyyaml" else "yaml"
        try:
            __import__(module_name)
        except ImportError:
            print(f">> 準備開始: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def main():
    try:
        # 1. 依存関係のチェックとインストール
        check_and_install()
        
        # 2. アプリの起動
        print("\n--- 起動中 (Launching App) ---")
        # 直接 streamlit モジュールを実行
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        
    except Exception as e:
        print("\n" + "="*40)
        print(f"エラーが発生しました:\n{e}")
        print("="*40)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

