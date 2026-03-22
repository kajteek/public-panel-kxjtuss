@echo off
echo ===================================================
echo     Port Status Checker (5000 & 8000)
echo ===================================================
echo.
echo Port 8000 (Frontend):
netstat -aon | findstr :8000 | findstr LISTENING
if %ERRORLEVEL% NEQ 0 echo [NOT RUNNING]
echo.
echo Port 5000 (Backend):
netstat -aon | findstr :5000 | findstr LISTENING
if %ERRORLEVEL% NEQ 0 echo [NOT RUNNING]
echo.
echo If both are LISTENING, visit http://localhost:8000
pause
