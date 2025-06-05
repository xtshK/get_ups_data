@echo off
echo [UPS Logger] Activating virtual environment...

call "C:\Users\kuose\ViewSonic Dropbox\Selena Kuo\Code\Python\03_it_proj_ups\get_ups_data\.venv\Scripts\activate.bat"

echo [UPS Logger] Running script...
python "C:\Users\kuose\ViewSonic Dropbox\Selena Kuo\Code\Python\03_it_proj_ups\get_ups_data\scripts_package\main.py"

echo [UPS Logger] Script finished.
pause
