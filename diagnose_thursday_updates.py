#!/usr/bin/env python3
"""
Comprehensive Thursday Game Update Diagnostic Script
Checks all aspects of Thursday game updating on the server
"""

import sqlite3
import requests
import json
from datetime import datetime, timedelta
import sys
import os

def check_database_thursday_games():
    """Check Thursday games in the database"""
    print("🏈 DATABASE: Thursday Games Status")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check current week Thursday games
        cursor.execute('''
            SELECT id, away_team, home_team, game_date, is_thursday_night,
                   home_score, away_score, is_final, game_status
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 AND is_thursday_night = 1
        ''')
        
        thursday_games = cursor.fetchall()
        
        if thursday_games:
            for game in thursday_games:
                game_id, away_team, home_team, game_date, is_thursday_night, home_score, away_score, is_final, game_status = game
                print(f"Game {game_id}: {away_team} @ {home_team}")
                print(f"  Date: {game_date}")
                print(f"  Thursday Night: {bool(is_thursday_night)}")
                print(f"  Score: {away_team} {away_score or 'N/A'} - {home_team} {home_score or 'N/A'}")
                print(f"  Final: {bool(is_final)}")
                print(f"  Status: {game_status or 'Unknown'}")
                print()
        else:
            print("❌ No Thursday games found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def check_background_updater_status():
    """Check if background updater is running"""
    print("🔄 BACKGROUND UPDATER: Status Check")
    print("=" * 50)
    
    try:
        # Check if background_updater.py exists
        if os.path.exists('background_updater.py'):
            print("✅ background_updater.py exists")
        else:
            print("❌ background_updater.py not found")
            return
        
        # Try to import and check status
        import background_updater
        
        if hasattr(background_updater, 'get_updater_status'):
            status = background_updater.get_updater_status()
            print(f"Background updater running: {status.get('running', False)}")
            print(f"Last update: {status.get('last_update', 'Never')}")
            print(f"Update count: {status.get('update_count', 0)}")
            print(f"Errors: {status.get('error_count', 0)}")
        else:
            print("⚠️  Cannot check updater status - function not available")
            
    except Exception as e:
        print(f"❌ Background updater error: {e}")

def check_api_connectivity():
    """Check if we can reach the NFL API"""
    print("🌐 API CONNECTIVITY: NFL Data Source")
    print("=" * 50)
    
    # Test ESPN API (commonly used for NFL data)
    test_urls = [
        "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=20250911",
        "https://www.espn.com/nfl/scoreboard"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        if 'events' in data:
                            print(f"  Games found: {len(data.get('events', []))}")
                        else:
                            print("  ✅ JSON response received")
                    except:
                        print("  ⚠️  Non-JSON response")
                else:
                    print(f"  ✅ HTML response ({len(response.text)} chars)")
            print()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()

def check_game_day_logic():
    """Check if today is considered a game day"""
    print("📅 GAME DAY LOGIC: Current Day Check")
    print("=" * 50)
    
    now = datetime.now()
    weekday = now.weekday()  # 0=Monday, 1=Tuesday, etc.
    
    print(f"Current date: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Weekday: {weekday} ({now.strftime('%A')})")
    
    # Game days are typically Thursday (3), Sunday (6), Monday (0), Tuesday (1)
    game_days = [0, 1, 3, 6]  # Monday, Tuesday, Thursday, Sunday
    
    if weekday in game_days:
        print(f"✅ Today IS a game day (weekday {weekday})")
    else:
        print(f"❌ Today is NOT a game day (weekday {weekday})")
        print("Game days are: Monday(0), Tuesday(1), Thursday(3), Sunday(6)")

def check_rate_limiting():
    """Check API rate limiting status"""
    print("⏱️  RATE LIMITING: API Request Limits")
    print("=" * 50)
    
    try:
        if os.path.exists('api_rate_limit.json'):
            print("✅ Rate limit file exists")
            with open('api_rate_limit.json', 'r') as f:
                rate_data = json.load(f)
            
            print(f"Rate limit data: {rate_data}")
            
            if 'last_request' in rate_data:
                last_request = datetime.fromisoformat(rate_data['last_request'])
                time_since = datetime.now() - last_request
                print(f"Time since last request: {time_since}")
                
                if time_since < timedelta(minutes=5):
                    print("⚠️  Recent API request - may be rate limited")
                else:
                    print("✅ Sufficient time since last request")
        else:
            print("❌ No rate limit file found")
            
    except Exception as e:
        print(f"❌ Rate limit check error: {e}")

def check_server_environment():
    """Check server environment and configuration"""
    print("🖥️  SERVER ENVIRONMENT: Configuration")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__ if '__file__' in globals() else 'Unknown'}")
    
    # Check important files
    important_files = [
        'app.py',
        'background_updater.py', 
        'deadline_manager.py',
        'nfl_fantasy.db',
        'api_rate_limit.json'
    ]
    
    for file in important_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} exists ({size} bytes)")
        else:
            print(f"❌ {file} missing")

def check_recent_game_activity():
    """Check for recent game updates in the database"""
    print("📊 RECENT ACTIVITY: Database Updates")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check for any recent score updates
        cursor.execute('''
            SELECT id, away_team, home_team, home_score, away_score, 
                   is_final, game_status, game_date
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 
            AND (home_score IS NOT NULL OR away_score IS NOT NULL)
            ORDER BY id
        ''')
        
        updated_games = cursor.fetchall()
        
        if updated_games:
            print(f"Games with scores: {len(updated_games)}")
            for game in updated_games:
                game_id, away_team, home_team, home_score, away_score, is_final, game_status, game_date = game
                print(f"  Game {game_id}: {away_team} {away_score or 0} - {home_team} {home_score or 0} ({game_status})")
        else:
            print("❌ No games have scores yet")
        
        # Check for any completed games
        cursor.execute('''
            SELECT COUNT(*) FROM nfl_games 
            WHERE week = 2 AND year = 2025 AND is_final = 1
        ''')
        
        completed_count = cursor.fetchone()[0]
        print(f"Completed games: {completed_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Recent activity check error: {e}")

def main():
    """Run all diagnostic checks"""
    print("🔍 THURSDAY GAME UPDATE DIAGNOSTIC")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Run all checks
    check_database_thursday_games()
    print()
    
    check_background_updater_status()
    print()
    
    check_game_day_logic()
    print()
    
    check_api_connectivity()
    print()
    
    check_rate_limiting()
    print()
    
    check_server_environment()
    print()
    
    check_recent_game_activity()
    print()
    
    print("🎯 DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("If Thursday games aren't updating:")
    print("1. Check if background updater is running")
    print("2. Verify API connectivity")
    print("3. Check if today is a game day")
    print("4. Review rate limiting")
    print("5. Manually trigger update if needed")

if __name__ == "__main__":
    main()
