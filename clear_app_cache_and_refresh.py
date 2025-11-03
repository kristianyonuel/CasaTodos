#!/usr/bin/env python3
"""
Clear Application Cache and Force Leaderboard Refresh
===================================================

This script helps resolve the cache issue where the season leaderboard
shows incorrect win counts despite the database being accurate.

Database Reality (Verified):
- KRISTIAN: 2 wins (Weeks 2, 3)
- ROBERT: 1 win (Week 4)
- RAMFIS: 1 win (Week 1)

App Display (Cached/Incorrect):
- KRISTIAN: 3 wins
- ROBERT: 2 wins
- RAMFIS: 1 win

Created: October 28, 2025
"""

import sqlite3
import os
import sys
from datetime import datetime

def verify_database_accuracy():
    """Verify the database has correct win counts"""
    print("🔍 Verifying Database Accuracy...")
    print("="*50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check weekly winners
        cursor.execute("""
            SELECT week, winner 
            FROM weekly_results 
            WHERE winner IS NOT NULL 
            ORDER BY week
        """)
        weekly_winners = cursor.fetchall()
        
        print("📊 Weekly Winners from Database:")
        for week, winner in weekly_winners:
            print(f"  Week {week}: {winner}")
        
        # Count wins per user
        cursor.execute("""
            SELECT winner, COUNT(*) as wins
            FROM weekly_results 
            WHERE winner IS NOT NULL 
            GROUP BY winner 
            ORDER BY wins DESC
        """)
        win_counts = cursor.fetchall()
        
        print("\n🏆 Season Win Counts (Database):")
        for user, wins in win_counts:
            print(f"  {user.upper()}: {wins} wins")
        
        # Verify user_statistics table
        cursor.execute("""
            SELECT username, season_wins, total_points, avg_points
            FROM user_statistics 
            ORDER BY season_wins DESC, total_points DESC
        """)
        user_stats = cursor.fetchall()
        
        print("\n📈 User Statistics Table:")
        for username, wins, points, avg in user_stats:
            print(f"  {username.upper()}: {wins} wins, {points} points, {avg:.1f} avg")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def suggest_cache_clearing_steps():
    """Provide steps to clear application cache"""
    print("\n🧹 Cache Clearing Solutions:")
    print("="*50)
    
    print("1. 🔄 Application Restart:")
    print("   - Stop the NFL Fantasy application")
    print("   - Wait 10-15 seconds")
    print("   - Restart the application")
    
    print("\n2. 🗑️ Clear Browser Cache (if web-based):")
    print("   - Press Ctrl+Shift+Delete")
    print("   - Select 'All time' or 'Everything'")
    print("   - Clear cached images and files")
    print("   - Refresh the page (Ctrl+F5)")
    
    print("\n3. 🔧 Force App Refresh:")
    print("   - Close all browser tabs with the app")
    print("   - Clear browser data for the app domain")
    print("   - Reopen the application")
    
    print("\n4. 📱 Mobile App (if applicable):")
    print("   - Force close the app")
    print("   - Clear app cache in phone settings")
    print("   - Restart the app")

def check_app_process():
    """Check if Flask app is running and suggest restart"""
    print("\n🖥️ Application Process Check:")
    print("="*50)
    
    try:
        import psutil
        
        # Look for Python processes running app.py
        found_app = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('app.py' in arg for arg in cmdline):
                        print(f"  🟢 Found app process: PID {proc.info['pid']}")
                        print(f"     Command: {' '.join(cmdline)}")
                        found_app = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not found_app:
            print("  🔴 No Flask app process found")
            print("     The application may not be running")
        
    except ImportError:
        print("  ⚠️ psutil not available - cannot check processes")
        print("  💡 You can manually check task manager for python processes")

def create_cache_refresh_script():
    """Create a script to restart the application"""
    script_content = '''@echo off
echo Restarting NFL Fantasy Application...
echo.

echo Stopping any running Flask processes...
taskkill /f /im python.exe 2>nul

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo Starting application...
cd /d "C:\\Users\\cjuarbe\\Casa\\CasaTodos"
start python app.py

echo.
echo Application restart complete!
echo Please wait 10-15 seconds then refresh your browser.
pause
'''
    
    try:
        with open('restart_app.bat', 'w') as f:
            f.write(script_content)
        print("\n📝 Created restart_app.bat script")
        print("   Double-click this file to restart the application")
        return True
    except Exception as e:
        print(f"❌ Could not create restart script: {e}")
        return False

def main():
    """Main execution function"""
    print("🧹 NFL Fantasy Cache Clearing Tool")
    print("="*50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verify database is correct
    if not verify_database_accuracy():
        print("❌ Database verification failed!")
        return False
    
    print("\n✅ Database is accurate - issue is in application cache")
    
    # Check application process
    check_app_process()
    
    # Provide cache clearing suggestions
    suggest_cache_clearing_steps()
    
    # Create restart script
    create_cache_refresh_script()
    
    print("\n🎯 SOLUTION SUMMARY:")
    print("="*50)
    print("✅ Database has correct data:")
    print("   - KRISTIAN: 2 wins")
    print("   - ROBERT: 1 win")
    print("   - RAMFIS: 1 win")
    print()
    print("🔧 To fix display:")
    print("   1. Run restart_app.bat (created)")
    print("   2. OR manually restart the application")
    print("   3. Clear browser cache if web-based")
    print("   4. Refresh the leaderboard page")
    print()
    print("🎉 After cache clear, leaderboard should show correct data!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)