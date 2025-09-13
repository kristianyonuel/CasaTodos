#!/usr/bin/env python3
"""
Server Diagnostic Script - Run this on your Ubuntu server
"""

import sqlite3
import sys
import os
from datetime import datetime

def diagnose_server_issues():
    """Comprehensive server diagnostics"""
    
    print("🔍 NFL Fantasy Server Diagnostics")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # 1. Check database file exists
    print("1️⃣ Database File Check:")
    db_files = ['nfl_fantasy.db', 'database.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"  ✅ {db_file} exists ({size:,} bytes)")
        else:
            print(f"  ❌ {db_file} not found")
    
    # 2. Check WSH@GB game status in database
    print("\n2️⃣ WSH@GB Game Status:")
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT game_id, away_team, home_team, away_score, home_score, is_final, game_date
            FROM nfl_games 
            WHERE (UPPER(away_team) = 'WSH' AND UPPER(home_team) = 'GB') 
            OR (UPPER(away_team) = 'GB' AND UPPER(home_team) = 'WSH')
            AND week = 2 AND year = 2025
        ''')
        
        game = cursor.fetchone()
        if game:
            game_id, away, home, away_score, home_score, is_final, game_date = game
            print(f"  Game ID: {game_id}")
            print(f"  Matchup: {away} @ {home}")
            print(f"  Score: {away_score}-{home_score}")
            print(f"  Final: {'Yes' if is_final else 'No'}")
            print(f"  Game Date: {game_date}")
        else:
            print("  ❌ WSH@GB game not found!")
        
        conn.close()
    except Exception as e:
        print(f"  ❌ Database error: {e}")
    
    # 3. Check if score_updater module is available
    print("\n3️⃣ Score Updater Module Check:")
    try:
        from score_updater import NFLScoreUpdater
        print("  ✅ score_updater module imported successfully")
        
        # Test ESPN API connection
        print("  🌐 Testing ESPN API connection...")
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        params = {"week": 2, "year": 2025, "seasontype": 2}
        
        response = requests.get(url, params=params, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            games = data.get('events', [])
            print(f"  ✅ ESPN API accessible - {len(games)} games found")
            
            # Look for WSH@GB specifically
            for game in games:
                competitions = game.get('competitions', [])
                for comp in competitions:
                    competitors = comp.get('competitors', [])
                    if len(competitors) >= 2:
                        team1 = competitors[0].get('team', {}).get('abbreviation', '').upper()
                        team2 = competitors[1].get('team', {}).get('abbreviation', '').upper()
                        
                        if ('WSH' in [team1, team2] and 'GB' in [team1, team2]):
                            score1 = competitors[0].get('score', 0)
                            score2 = competitors[1].get('score', 0)
                            status = comp.get('status', {}).get('type', {}).get('name', 'Unknown')
                            print(f"    🎯 Found WSH@GB: {team1} {score1}-{score2} {team2} ({status})")
                            break
        else:
            print(f"  ❌ ESPN API error: HTTP {response.status_code}")
        
    except ImportError as e:
        print(f"  ❌ score_updater import failed: {e}")
    except Exception as e:
        print(f"  ❌ ESPN API test failed: {e}")
    
    # 4. Check background_updater module
    print("\n4️⃣ Background Updater Check:")
    try:
        import background_updater
        print("  ✅ background_updater module available")
        
        # Check if background updater functions exist
        functions = [attr for attr in dir(background_updater) if not attr.startswith('_')]
        print(f"  Available functions: {', '.join(functions)}")
        
    except ImportError as e:
        print(f"  ❌ background_updater import failed: {e}")
    
    # 5. Try manual score update
    print("\n5️⃣ Manual Score Update Test:")
    try:
        from score_updater import NFLScoreUpdater
        
        print("  🚀 Running manual score update...")
        updater = NFLScoreUpdater('nfl_fantasy.db')
        results = updater.run_update_cycle()
        
        print(f"  ✅ Update completed:")
        print(f"    Games checked: {results['games_checked']}")
        print(f"    Games updated: {results['games_updated']}")
        print(f"    Duration: {results['duration_seconds']:.2f}s")
        
        # Check WSH@GB again after update
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT away_score, home_score, is_final
            FROM nfl_games 
            WHERE (UPPER(away_team) = 'WSH' AND UPPER(home_team) = 'GB') 
            OR (UPPER(away_team) = 'GB' AND UPPER(home_team) = 'WSH')
            AND week = 2 AND year = 2025
        ''')
        
        game = cursor.fetchone()
        if game:
            away_score, home_score, is_final = game
            print(f"  📊 WSH@GB after update: {away_score}-{home_score} (Final: {'Yes' if is_final else 'No'})")
            
            if away_score is not None and home_score is not None:
                print("  🎯 SUCCESS: Scores are now updated!")
            else:
                print("  ⚠️ Scores still null - API or matching issue")
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Manual update failed: {e}")
    
    print(f"\n🏁 Diagnostics completed at {datetime.now()}")

if __name__ == "__main__":
    diagnose_server_issues()
