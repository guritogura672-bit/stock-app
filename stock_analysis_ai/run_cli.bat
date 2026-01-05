@echo off
cd /d "%~dp0"
echo 必要なライブラリを確認・インストールしています...
python -m pip install -r requirements.txt

echo 分析ツールを実行中...
python src/main_cli.py
if %errorlevel% neq 0 (
    echo.
    echo 実行中にエラーが発生しました。
)
pause
