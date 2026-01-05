import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils import load_config, save_config
from src.fetcher import fetch_stock_data
from src.indicators import calculate_indicators
from src.scorer import evaluate_stock

# ページ設定
# ページ設定
st.set_page_config(page_title="Stock Analysis AI", layout="wide", page_icon="📈")

# カスタムCSSでデザインをリッチにする
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
    }
    
    /* 判定ラベルの装飾 */
    .signal-buy { color: #10b981; font-weight: 700; }
    .signal-sell { color: #ef4444; font-weight: 700; }
    .signal-hold { color: #f59e0b; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🚀 Stock Analysis AI - Premium Market Scanner</h1><p>テクニカル指標に基づいた高度な株式分析システム</p></div>', unsafe_allow_html=True)

# サイドバー設定
st.sidebar.header("🔍 分析対象の設定")
try:
    config = load_config()
    default_tickers = config['tickers']
    settings = config['settings']
except Exception as e:
    st.error(f"Config Error: {e}")
    st.stop()

# 自由入力欄の追加
st.sidebar.subheader("銘柄の一括追加")
custom_tickers_input = st.sidebar.text_area("ティッカー入力 (コードのみ可)", 
    placeholder="例:\n7203\nAAPL, NVDA\n3350 9984",
    help="証券コードのみ、カンマ区切り、スペース区切り、改行のすべてに対応しています。")

# 合計銘柄リストの作成
import re
all_tickers = list(dict.fromkeys(default_tickers)) # 重複排除
selected_default = all_tickers.copy()

if custom_tickers_input:
    custom_list = []
    # カンマ、スペース、改行で分割
    raw_symbols = re.split(r'[,\s\n]+', custom_tickers_input)
    
    for symbol in raw_symbols:
        symbol = symbol.strip().upper()
        if not symbol: continue
        
        # 4桁の数字だけなら自動で .T を付けて日本株として扱う
        if symbol.isdigit() and len(symbol) == 4:
            symbol = f"{symbol}.T"
        
        custom_list.append(symbol)
        
    all_tickers = list(dict.fromkeys(all_tickers + custom_list))
    # カスタム入力がある場合は、それだけを選択状態にする
    selected_default = custom_list

selected_tickers = st.sidebar.multiselect("分析する銘柄を選択", all_tickers, default=selected_default)

# お気に入り登録機能
if st.sidebar.button("★ 選択中の銘柄をお気に入りに保存"):
    if selected_tickers:
        config['tickers'] = selected_tickers
        try:
            save_config(config)
            st.sidebar.success(f"お気に入りを更新しました ({len(selected_tickers)}銘柄)")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"保存エラー: {e}")
    else:
        st.sidebar.warning("銘柄が選択されていません")

st.sidebar.markdown("---")

# 時間足の選択
interval_options = {
    "1日": "1d",
    "1時間": "1h",
    "15分": "15m",
    "5分": "5m",
    "1分": "1m"
}
selected_interval_label = st.sidebar.selectbox("時間足 (Interval)", list(interval_options.keys()), index=0)
interval = interval_options[selected_interval_label]

# 時間足に応じた期間の選択肢（日本語ラベルと内部コードの対応）
if interval == "1d":
    period_map = {
        "1ヶ月": "1mo",
        "3ヶ月": "3mo",
        "6ヶ月": "6mo",
        "1年": "1y",
        "2年": "2y",
        "5年": "5y",
        "全期間": "max"
    }
    period_index = 3 # 1年
elif interval == "1h":
    period_map = {
        "1日": "1d",
        "5日": "5d",
        "1ヶ月": "1mo",
        "3ヶ月": "3mo",
        "2年": "730d"
    }
    period_index = 2 # 1ヶ月
else: # 短期足 (1m, 5m etc)
    period_map = {
        "1日": "1d",
        "5日": "5d",
        "1ヶ月": "1mo",
        "2ヶ月": "60d"
    }
    period_index = 1 # 5日

selected_period_label = st.sidebar.selectbox("分析期間 (Period)", list(period_map.keys()), index=period_index)
period = period_map[selected_period_label]

# リアルタイム更新の設定
st.sidebar.markdown("---")
st.sidebar.subheader("🕒 リアルタイム更新")
auto_refresh = st.sidebar.checkbox("自動更新を有効にする")
refresh_interval = st.sidebar.slider("更新間隔 (秒)", 10, 300, 60)

if auto_refresh:
    import time
    from streamlit_autorefresh import st_autorefresh
    # ページを一定間隔でリロードさせる
    st_autorefresh(interval=refresh_interval * 1000, key="stock_refresh")

if st.sidebar.button("分析開始"):
    with st.spinner("データ取得・会社名を確認中..."):
        # データ取得
        res_tuple = fetch_stock_data(selected_tickers, period=period, interval=interval)
        
        # デバッグ用（エラー回避）
        if isinstance(res_tuple, tuple):
            if len(res_tuple) == 2:
                data_map, name_map = res_tuple
            else:
                st.error(f"システムエラー: データの形式が正しくありません (想定2, 実際{len(res_tuple)})")
                st.stop()
        else:
            data_map = res_tuple
            name_map = {}
        
        results = []
        
        # 分析ループ
        for ticker, df in data_map.items():
            if df.empty:
                continue
            
            # 指標計算
            df = calculate_indicators(df, settings)
            score, signal, reason = evaluate_stock(df, settings)
            
            results.append({
                "Ticker": ticker,
                "Name": name_map.get(ticker, ticker),
                "Close": df['Close'].iloc[-1],
                "Score": score,
                "Signal": signal,
                "Trend": reason
            })
            
            # 詳細表示用のデータ保持
            data_map[ticker] = df

        # ランキング表示
        st.subheader("📊 分析結果ランキング")
        if results:
            results_df = pd.DataFrame(results)
            results_df = results_df.sort_values(by="Score", ascending=False)
            
            # スタイリング
            def color_signal(val):
                color = 'red' if val == 'SELL' else 'green' if val == 'BUY' else 'orange'
                return f'color: {color}; font-weight: bold'
            
            # 表示列の整理
            display_df = results_df[['Ticker', 'Name', 'Close', 'Score', 'Signal', 'Trend']]
            st.dataframe(display_df.style.applymap(color_signal, subset=['Signal']), use_container_width=True)
            
            # --- ここから「買い・売りシグナル」のまとめ表示 ---
            st.markdown("### 🔔 アラート・注目銘柄")
            col1, col2 = st.columns(2)
            
            buy_stocks = results_df[results_df['Signal'] == 'BUY']
            sell_stocks = results_df[results_df['Signal'] == 'SELL']
            
            with col1:
                st.markdown("#### 🟢 買い推奨 (BUY)")
                if not buy_stocks.empty:
                    for idx, row in buy_stocks.iterrows():
                        st.success(f"**{row['Ticker']}** ({row['Name']}) - スコア: {row['Score']}")
                else:
                    st.info("現在、買いシグナルの銘柄はありません")
                    
            with col2:
                st.markdown("#### 🔴 売り注意 (SELL)")
                if not sell_stocks.empty:
                    for idx, row in sell_stocks.iterrows():
                        st.error(f"**{row['Ticker']}** ({row['Name']}) - スコア: {row['Score']}")
                else:
                    st.info("現在、売りシグナルの銘柄はありません")
            st.markdown("---")
            # --- ここまで ---

            # 個別チャート表示
            st.subheader("📈 詳細テクニカルチャート")
            
            for ticker in results_df['Ticker'].tolist():
                df = data_map[ticker]
                res = results_df[results_df['Ticker'] == ticker].iloc[0]
                ticker_display_name = f"{ticker} ({res['Name']})"
                
                with st.expander(f"【{ticker_display_name}】 スコア: {res['Score']} / 判定: {res['Signal']}", expanded=True):
                    st.write(f"**トレンド分析:** {res['Trend']}")
                    
                    # --- Plotly Multi-chart ---
                    from plotly.subplots import make_subplots
                    
                    # 3つのセクション (価格, MACD, RSI)
                    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                       vertical_spacing=0.05, 
                                       row_heights=[0.5, 0.25, 0.25],
                                       subplot_titles=(f"{ticker_display_name} 価格 & 移動平均線", "MACD", "RSI"))

                    # 1. 価格チャート (Candlestick)
                    # 日本式の色設定 (陽線: 赤, 陰線: 青/緑系)
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                               increasing_line_color='#e63946', decreasing_line_color='#457b9d',
                                               name="株価"), row=1, col=1)
                    
                    # 移動平均線
                    ma_short = settings['ma_short']
                    ma_long = settings['ma_long']
                    fig.add_trace(go.Scatter(x=df.index, y=df[f'SMA_{ma_short}'], line=dict(color='#ffb703', width=1.5), name=f'SMA {ma_short}'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df[f'SMA_{ma_long}'], line=dict(color='#219ebc', width=1.5), name=f'SMA {ma_long}'), row=1, col=1)

                    # 2. MACD
                    macd_col = f"MACD_{settings['macd_fast']}_{settings['macd_slow']}_{settings['macd_signal']}"
                    signal_col = f"MACDs_{settings['macd_fast']}_{settings['macd_slow']}_{settings['macd_signal']}"
                    fig.add_trace(go.Scatter(x=df.index, y=df[macd_col], line=dict(color='#fb8500', width=1), name="MACD"), row=2, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df[signal_col], line=dict(color='#8ecae6', width=1), name="Signal"), row=2, col=1)
                    # ゼロライン
                    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)

                    # 3. RSI
                    rsi_col = f"RSI_{settings['rsi_window']}"
                    fig.add_trace(go.Scatter(x=df.index, y=df[rsi_col], line=dict(color='#a2d2ff', width=1.5), name="RSI"), row=3, col=1)
                    # 境界線 (70/30)
                    fig.add_hline(y=70, line_dash="dash", line_color="#ff4d6d", row=3, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="#00f5d4", row=3, col=1)

                    # レイアウト調整
                    fig.update_layout(height=800, 
                                    template="plotly_dark",
                                    xaxis_rangeslider_visible=True, # ズーム・移動がしやすくなるようスライダーを表示
                                    xaxis_rangeslider_thickness=0.05, # スライダーを細めにしてメインチャートを広く
                                    margin=dict(l=50, r=50, t=50, b=50),
                                    hovermode="x unified") # マウス位置の値をまとめて表示
                    
                    # スクロール（マウスホイール）でのズームを有効化
                    fig.update_xaxes(fixedrange=False)
                    fig.update_yaxes(fixedrange=False)

                    # Streamlitのプロット時に設定を注入
                    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
                
        else:
            st.warning("データが見つかりませんでした。")
