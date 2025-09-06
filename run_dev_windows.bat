@echo off
REM Windows Development Helper Script
REM Use this if you encounter SSL issues during development on Windows

echo Setting up Windows development environment...

REM Set environment variable to disable SSL verification (development only)
set DISABLE_SSL_VERIFY=true

echo SSL verification disabled for development
echo Starting Flask application...

REM Start the application
C:\Users\cjuarbe\Casa\CasaTodos\.venv\Scripts\python.exe app.py

pause
