#!/usr/bin/env python3
"""
Background Updater Status Checker
Identifies why the background updater isn't working on Ubuntu
"""

import os
import sys
import subprocess
import sqlite3
import requests
from datetime import datetime
import logging

def check_background_updater_file():
    """Check if background_updater.py exists and is executable"""
    print("📁 BACKGROUND UPDATER FILE CHECK")
    print("=" * 50)
    
    if not os.path.exists('background_updater.py'):
        print("❌ background_updater.py NOT FOUND")
        return False
    
    # Check permissions
    readable = os.access('background_updater.py', os.R_OK)
    executable = os.access('background_updater.py', os.X_OK)
    
    print(f"✅ background_updater.py exists")
    print(f"   Readable: {readable}")
    print(f"   Executable: {executable}")
    
    # Check file size
    size = os.path.getsize('background_updater.py')
    print(f"   Size: {size} bytes")
    
    if size < 100:
        print("⚠️  File seems too small")
        return False
    
    return readable and executable

def check_running_processes():
    """Check what Python processes are running"""
    print("\n🔄 RUNNING PROCESSES CHECK")
    print("=" * 50)
    
    try:
        # Check processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        python_procs = []
        background_found = False
        
        for line in result.stdout.split('\n'):
            if 'python' in line.lower():
                python_procs.append(line.strip())
                if 'background_updater' in line:
                    background_found = True
                    print(f"✅ Found background updater: {line.strip()}")
        
        if not background_found:
            print("❌ Background updater is NOT running")
            
        print(f"\n📋 All Python processes ({len(python_procs)}):")
        for proc in python_procs:
            print(f"   {proc}")
            
        return background_found
        
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return False

def test_espn_api():
    """Test ESPN API connectivity"""
    print("\n🌐 ESPN API TEST")
    print("=" * 50)
    
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ ESPN API Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('events', [])
            print(f"   Found {len(games)} games in response")
            return True
        else:
            print(f"❌ Bad response code: {response.status_code}")
            return False
            
    except requests.exceptions.SSLError as e:
        print(f"🔒 SSL Error: {e}")
        print("   This is likely the main issue!")
        return False
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def check_database_status():
    """Check database for recent updates"""
    print("\n🗃️  DATABASE UPDATE STATUS")
    print("=" * 50)
    
    db_files = ['database.db', 'nfl_fantasy.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check Week 3 games
                cursor.execute("""
                    SELECT COUNT(*) as total_games,
                           SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
                           MIN(game_date) as first_game,
                           MAX(game_date) as last_game
                    FROM nfl_games 
                    WHERE week = 3 AND year = 2025
                """)
                
                week3_stats = cursor.fetchone()
                print(f"✅ {db_file} - Week 3 Games:")
                print(f"   Total: {week3_stats[0]}")
                print(f"   Final: {week3_stats[1]}")
                print(f"   First game: {week3_stats[2]}")
                print(f"   Last game: {week3_stats[3]}")
                
                # Check most recent final game
                cursor.execute("""
                    SELECT home_team, away_team, home_score, away_score, game_date
                    FROM nfl_games 
                    WHERE is_final = 1 
                    ORDER BY game_date DESC 
                    LIMIT 3
                """)
                
                recent_finals = cursor.fetchall()
                print(f"\n   Most recent final games:")
                for game in recent_finals:
                    home, away, h_score, a_score, date = game
                    print(f"   {away} {a_score} @ {home} {h_score} - {date}")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ {db_file} error: {e}")

def generate_ubuntu_fixes():
    """Generate specific Ubuntu fix commands"""
    print("\n🔧 UBUNTU-SPECIFIC FIXES")
    print("=" * 50)
    
    fixes = [
        "# Kill any existing background processes",
        "pkill -f background_updater.py",
        "",
        "# Fix SSL certificate issues (common Ubuntu problem)",
        "sudo apt-get update",
        "sudo apt-get install ca-certificates",
        "pip3 install --upgrade certifi requests urllib3",
        "",
        "# Make background updater executable",
        "chmod +x background_updater.py",
        "",
        "# Start background updater with proper logging",
        "nohup python3 background_updater.py > updater.log 2>&1 &",
        "",
        "# Verify it started",
        "sleep 2",
        "ps aux | grep background_updater",
        "",
        "# Check logs for errors",
        "tail -20 updater.log",
        "",
        "# If SSL issues persist, try this fix:",
        "export PYTHONHTTPSVERIFY=0  # Temporary workaround",
        "python3 -c \"import ssl; print(ssl.get_default_verify_paths())\"",
    ]
    
    for fix in fixes:
        print(fix)

def main():
    """Run background updater diagnostics"""
    print("🏈 BACKGROUND UPDATER DIAGNOSTIC")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
    
    print(f"📂 Working directory: {os.getcwd()}")
    
    # Run checks
    file_ok = check_background_updater_file()
    process_running = check_running_processes()
    api_ok = test_espn_api()
    
    check_database_status()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"✅ Background updater file: {'OK' if file_ok else 'PROBLEM'}")
    print(f"✅ Process running: {'YES' if process_running else 'NO'}")
    print(f"✅ ESPN API access: {'OK' if api_ok else 'BLOCKED'}")
    
    # Root cause analysis
    print("\n🎯 ROOT CAUSE ANALYSIS")
    print("=" * 50)
    
    if not process_running:
        print("🚨 PRIMARY ISSUE: Background updater is not running")
        print("   → Need to start the background process")
    
    if not api_ok:
        print("🚨 SECONDARY ISSUE: ESPN API access blocked")
        print("   → SSL certificate or network connectivity problem")
        print("   → This is very common on Ubuntu servers")
    
    if not file_ok:
        print("🚨 FILE ISSUE: background_updater.py has problems")
        print("   → Check file exists and has correct permissions")
    
    # Generate fixes
    generate_ubuntu_fixes()

if __name__ == "__main__":
    main()
