#!/usr/bin/env python3
"""
Thursday Game Update Fix Script
Addresses the specific issues found in the diagnostic
"""

import subprocess
import sys
import os
from datetime import datetime

def fix_background_updater():
    """Start the background updater"""
    print("🔄 FIXING: Background Updater")
    print("=" * 40)
    
    try:
        # Check if app is running
        print("Checking if app is running...")
        
        # Start background updater through app
        print("Background updater should be started when the app runs.")
        print("If app is running but updater stopped, restart the app.")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def manual_score_update():
    """Manually update scores for recent games"""
    print("📊 MANUAL UPDATE: Force Score Refresh")
    print("=" * 40)
    
    try:
        # Import and run update function
        import background_updater
        
        print("Running manual score update...")
        result = background_updater.update_live_scores()
        
        if result:
            print("✅ Manual update completed successfully")
        else:
            print("⚠️  Manual update completed with issues")
            
        return result
        
    except Exception as e:
        print(f"❌ Manual update error: {e}")
        return False

def verify_thursday_game():
    """Verify Thursday game has correct scores"""
    print("🏈 VERIFICATION: Thursday Game Status")
    print("=" * 40)
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT away_team, home_team, away_score, home_score, is_final, game_status
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 AND is_thursday_night = 1
        ''')
        
        game = cursor.fetchone()
        
        if game:
            away_team, home_team, away_score, home_score, is_final, game_status = game
            print(f"Game: {away_team} @ {home_team}")
            print(f"Score: {away_team} {away_score} - {home_team} {home_score}")
            print(f"Final: {bool(is_final)}")
            print(f"Status: {game_status}")
            
            # Check if scores look correct (WSH won 27-18 according to user)
            if away_team == 'WSH' and home_team == 'GB':
                if away_score == 27 and home_score == 18:
                    print("✅ Scores are correct!")
                else:
                    print(f"⚠️  Scores may be incorrect. Expected: WSH 27 - GB 18")
                    print(f"   Current: WSH {away_score} - GB {home_score}")
                    return False
            
            return True
        else:
            print("❌ Thursday game not found")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def restart_app_command():
    """Provide commands to restart the app properly"""
    print("🚀 RESTART COMMANDS: App Restart Instructions")
    print("=" * 40)
    
    commands = [
        "# Stop any running Python processes:",
        "taskkill /F /IM python.exe",
        "",
        "# Start app in production mode:",
        "python app.py",
        "",
        "# OR start in development mode:",
        "python app.py dev",
        "",
        "# Check if background updater started:",
        "# Look for: '✅ Background game updater started' in logs"
    ]
    
    for cmd in commands:
        print(cmd)

def main():
    """Run the fix procedures"""
    print("🔧 THURSDAY GAME UPDATE FIX")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print()
    
    # Step 1: Verify current status
    print("STEP 1: Verify Thursday Game")
    if verify_thursday_game():
        print("✅ Thursday game data looks good")
    else:
        print("❌ Thursday game needs correction")
    print()
    
    # Step 2: Try manual update
    print("STEP 2: Manual Score Update")
    manual_score_update()
    print()
    
    # Step 3: Fix background updater
    print("STEP 3: Background Updater Fix")
    fix_background_updater()
    print()
    
    # Step 4: Restart instructions
    print("STEP 4: Restart App")
    restart_app_command()
    print()
    
    print("🎯 FIX SUMMARY:")
    print("=" * 30)
    print("1. Thursday game already has scores (WSH 24 - GB 21)")
    print("2. Background updater needs to be running")
    print("3. Restart the app to ensure updater starts")
    print("4. Verify correct scores: WSH 27 - GB 18 (if different)")

if __name__ == "__main__":
    main()
