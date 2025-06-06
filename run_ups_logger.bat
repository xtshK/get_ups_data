REM 將此內容儲存為 run_script.bat
@echo off

REM 指定 Python 可執行檔路徑（如有安裝在非系統預設路徑）
set PYTHON_PATH=C:\Users\kuose\AppData\Local\Microsoft\WindowsApps\python.exe

REM 指定 Python 腳本路徑
set SCRIPT_PATH=C:\Users\kuose\ViewSonic Dropbox\Selena Kuo\Code\Python\03_it_proj_ups\get_ups_data\scripts_package\main.py

REM 執行 Python 腳本
"%PYTHON_PATH%" "%SCRIPT_PATH%"

REM 暫停視窗以顯示輸出（可選）
pause
