@echo off
echo ===================================================
echo     LSPD Document System - Organized Version
echo ===================================================
echo.
echo Cleaning up existing processes on ports 5000 and 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul

echo.
echo Installing backend dependencies...
cd server
python -m pip install -r requirements.txt
echo.
echo Starting Flask Backend on port 5000...
cd src
start cmd /k "python app.py"
echo.
echo Starting Frontend server on port 8000...
cd ../../client
start cmd /k "python -m http.server 8000"
echo.
echo System started successfully.
echo Please open: http://localhost:8000 in your browser.
pause
