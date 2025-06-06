@echo off

REM 啟動虛擬環境（.venv）
call "%~dp0.venv\Scripts\activate.bat"

REM 執行 Python 腳本
python "%~dp0scripts_package\main.py"

REM 暫停視窗以顯示輸出（可選）
pause
