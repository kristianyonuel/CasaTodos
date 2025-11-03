@echo off
echo 🏈 NFL Fantasy Application Restart Script
echo ==========================================
echo.

echo 🔄 Stopping any running Flask/Python processes...
taskkill /f /im python.exe 2>nul
if %errorlevel% == 0 (
    echo ✅ Python processes stopped
) else (
    echo ℹ️ No Python processes were running
)

echo.
echo ⏳ Waiting 5 seconds for cleanup...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 Starting NFL Fantasy application...
cd /d "C:\Users\cjuarbe\Casa\CasaTodos"
start python app.py

echo.
echo ✅ Application restart complete!
echo.
echo 📌 NEXT STEPS:
echo    1. Wait 10-15 seconds for app to fully start
echo    2. Open your browser and navigate to the app
echo    3. Clear browser cache (Ctrl+Shift+Delete) if needed
echo    4. Refresh the leaderboard page
echo.
echo 🎯 Expected result after cache clear:
echo    - KRISTIAN: 2 wins (correct)
echo    - ROBERT: 1 win (correct)
echo    - RAMFIS: 1 win (correct)
echo.
pause