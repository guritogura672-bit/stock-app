python -m PyInstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "StockAnalysisAI" ^
    --collect-all streamlit ^
    --collect-all pandas ^
    --collect-all altair ^
    --collect-all plotly ^
    --hidden-import="streamlit.runtime.scriptrunner.magic_funcs" ^
    --add-data "app.py;." ^
    --add-data "src;src" ^
    --add-data "config.yaml;." ^
    app_entry_point.py
