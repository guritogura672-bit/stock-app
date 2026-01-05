import sys
import os

# Ensure src is in path if running directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import load_config
from fetcher import fetch_stock_data
from indicators import calculate_indicators
from scorer import evaluate_stock
from rich.console import Console
from rich.table import Table
from rich import box

def main():
    console = Console()
    console.print("[bold green]Stock Analysis AI Tool[/bold green]")

    # 1. Load Config
    try:
        config = load_config()
        tickers = config['tickers']
        settings = config['settings']
        console.print(f"Loaded {len(tickers)} tickers from config.")
    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")
        return

    # 2. Fetch Data
    console.print(f"Fetching data (Period: {settings['period']}, Interval: {settings['interval']})...")
    data, names = fetch_stock_data(tickers, period=settings['period'], interval=settings['interval'])

    # 3. Analyze and Show Result
    table = Table(title="Stock Analysis Ranking", box=box.ROUNDED)
    table.add_column("Ticker", style="cyan", justify="left")
    table.add_column("Latest Close", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Signal", justify="center")
    table.add_column("Reasons", style="dim")

    results = []

    for ticker, df in data.items():
        if df.empty:
            continue
            
        # Calc Indicators
        try:
            df = calculate_indicators(df, settings)
            score, signal, reason = evaluate_stock(df, settings)
            
            # Colorize Signal
            signal_str = f"[bold green]{signal}[/bold green]" if signal == "BUY" else \
                         f"[bold red]{signal}[/bold red]" if signal == "SELL" else \
                         f"[yellow]{signal}[/yellow]"
                         
            results.append({
                "Ticker": ticker,
                "Close": df['Close'].iloc[-1],
                "Score": score,
                "Signal": signal_str,
                "Reason": reason
            })
        except Exception as e:
            console.print(f"[red]Error analyzing {ticker}: {e}[/red]")

    # Sort by Score (Desc)
    results.sort(key=lambda x: x["Score"], reverse=True)

    for res in results:
        table.add_row(
            res["Ticker"], 
            f"{res['Close']:.2f}", 
            str(res["Score"]), 
            res["Signal"],
            res["Reason"]
        )

    console.print(table)

if __name__ == "__main__":
    main()
