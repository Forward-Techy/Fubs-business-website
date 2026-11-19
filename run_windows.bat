@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo FUBS - Forward Universal Biz Solutions
echo Windows local launcher
echo ==============================================

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.10+ from https://www.python.org/downloads/ and enable "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto error
)

echo Installing/checking required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Starting FUBS. Keep this window open while using the website.
echo Open your browser at http://127.0.0.1:5000
echo Press CTRL+C in this window to stop the website.
echo.
start "FUBS Website" http://127.0.0.1:5000
".venv\Scripts\python.exe" run.py
pause
exit /b 0

:error
echo.
echo Setup failed. Check the error above and confirm Python 3.10+ is installed.
pause
exit /b 1
