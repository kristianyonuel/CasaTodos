#!/usr/bin/env python3
"""
Fix incorrect NFL game 9 schedule - should be Green Bay Packers vs Carolina Panthers
"""

import sqlite3
import subprocess
from datetime import datetime

def connect_to_remote_db():
    """Copy and connect to the remote database"""
    print("📥 Downloading current database from server...")
    
    # Copy database from server
    result = subprocess.run(['scp', 'casa@20.157.116.145:~/CasaTodos/nfl_fantasy.db', './nfl_fantasy_remote.db'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to download database: {result.stderr}")
        return None
    
    # Connect to the copied database
    try:
        conn = sqlite3.connect('./nfl_fantasy_remote.db')
        print("✅ Connected to database")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def check_game_9():
    """Check current game 9 details"""
    conn = connect_to_remote_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n=== CHECKING CURRENT GAME 9 ===")
    
    # Find game 9
    cursor.execute("""
        SELECT id, week, home_team, away_team, game_time, game_date 
        FROM nfl_games 
        WHERE id = 9
    """)
    
    game = cursor.fetchone()
    if game:
        game_id, week, home_team, away_team, game_time, game_date = game
        print(f"Game ID: {game_id}")
        print(f"Week: {week}")
        print(f"Current matchup: {away_team} @ {home_team}")
        print(f"Date/Time: {game_date} {game_time}")
        
        return game
    else:
        print("❌ Game 9 not found")
        return None
    
    conn.close()

def fix_game_9_schedule():
    """Fix game 9 to be Green Bay Packers vs Carolina Panthers"""
    conn = connect_to_remote_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n=== FIXING GAME 9 SCHEDULE ===")
    
    # First check current game 9
    cursor.execute("SELECT * FROM nfl_games WHERE id = 9")
    current_game = cursor.fetchone()
    
    if current_game:
        print(f"Current Game 9: {current_game}")
        
        # Update to Green Bay Packers vs Carolina Panthers
        # Assuming Carolina Panthers are away team and Green Bay Packers are home team
        cursor.execute("""
            UPDATE nfl_games 
            SET home_team = 'Green Bay Packers',
                away_team = 'Carolina Panthers'
            WHERE id = 9
        """)
        
        conn.commit()
        print("✅ Updated Game 9:")
        print("   Away Team: Carolina Panthers")
        print("   Home Team: Green Bay Packers")
        
        # Verify the change
        cursor.execute("SELECT home_team, away_team FROM nfl_games WHERE id = 9")
        updated_game = cursor.fetchone()
        print(f"✅ Verified: {updated_game[1]} @ {updated_game[0]}")
        
    else:
        print("❌ Game 9 not found in database")
    
    conn.close()
    
    # Upload fixed database back to server
    print("\n📤 Uploading fixed database to server...")
    result = subprocess.run(['scp', './nfl_fantasy_remote.db', 'casa@20.157.116.145:~/CasaTodos/nfl_fantasy.db'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Database uploaded successfully")
        
        # Clean up local copy
        import os
        os.remove('./nfl_fantasy_remote.db')
        print("✅ Local database copy cleaned up")
    else:
        print(f"❌ Failed to upload database: {result.stderr}")

def check_all_week_games(week_num=None):
    """Check all games for a specific week to see context"""
    conn = connect_to_remote_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # If no week specified, find the week of game 9
    if week_num is None:
        cursor.execute("SELECT week FROM nfl_games WHERE id = 9")
        result = cursor.fetchone()
        if result:
            week_num = result[0]
        else:
            print("❌ Could not determine week for game 9")
            conn.close()
            return
    
    print(f"\n=== ALL GAMES FOR WEEK {week_num} ===")
    
    cursor.execute("""
        SELECT id, home_team, away_team, game_date, game_time
        FROM nfl_games 
        WHERE week = ?
        ORDER BY id
    """, (week_num,))
    
    games = cursor.fetchall()
    
    for game in games:
        game_id, home_team, away_team, game_date, game_time = game
        status = "🔥 GAME 9" if game_id == 9 else ""
        print(f"Game {game_id}: {away_team} @ {home_team} | {game_date} {game_time} {status}")
    
    conn.close()

def main():
    print("🏈 NFL GAME 9 SCHEDULE FIX")
    print("=" * 50)
    print("Issue: Game 9 should be Green Bay Packers vs Carolina Panthers")
    
    # Check current game 9
    current_game = check_game_9()
    
    if current_game:
        # Show context - all games in the same week
        check_all_week_games()
        
        # Ask for confirmation
        print(f"\n🔧 READY TO FIX:")
        print(f"   Current: {current_game[3]} @ {current_game[2]}")
        print(f"   Will change to: Carolina Panthers @ Green Bay Packers")
        
        # Fix the schedule
        fix_game_9_schedule()
        
        print("\n✅ SCHEDULE FIX COMPLETE!")
        print("The NFL Fantasy app will now show the correct matchup for Game 9")
    else:
        print("❌ Could not process Game 9 - please check database")

if __name__ == "__main__":
    main()