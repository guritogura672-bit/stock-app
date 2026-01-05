@echo off
cd /d "%~dp0"
python launcher.py
if %errorlevel% neq 0 (
    echo [Info] 'python' command failed, trying 'py' command...
    py launcher.py
)
pause
