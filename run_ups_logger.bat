@echo off

REM 顯示開始執行訊息
echo Starting the script...
echo Please wait...

REM 啟動虛擬環境(.venv)
call "%~dp0.venv\Scripts\activate.bat"

REM 執行 Python 腳本並檢查執行結果
echo Executing Python script...
python "%~dp0scripts_package\main.py"
if %ERRORLEVEL% equ 0 (
    echo.
    echo Script executed successfully!
) else (
    echo.
    echo Error: Script execution failed!
    echo Please check the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

REM 等待5秒後關閉視窗
echo.
echo Window will close in 5 seconds...
timeout /t 5 /nobreak > nul