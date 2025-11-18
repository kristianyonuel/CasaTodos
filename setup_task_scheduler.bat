@echo off
echo Setting up NFL Fantasy Background Service...
echo.

REM Delete existing task if it exists
schtasks /delete /tn "NFL_Fantasy_Background" /f >nul 2>&1

REM Create new task to run every 15 minutes
schtasks /create /tn "NFL_Fantasy_Background" /tr "python \"C:\Users\cjuarbe\Casa\CasaTodos\simple_background_service.py\" --run" /sc minute /mo 15 /f

if %errorlevel% == 0 (
    echo ✅ Task scheduled successfully!
    echo   Task Name: NFL_Fantasy_Background
    echo   Frequency: Every 15 minutes
    echo   Command: python "C:\Users\cjuarbe\Casa\CasaTodos\simple_background_service.py" --run
    echo.
    echo To check status: schtasks /query /tn "NFL_Fantasy_Background"
    echo To delete task: schtasks /delete /tn "NFL_Fantasy_Background" /f
) else (
    echo ❌ Failed to create scheduled task
    echo   Make sure you're running as Administrator
)

echo.
pause
