#!/usr/bin/env python3
"""
Check database schema and fix the picks update script
"""

import sqlite3

def check_database_schema():
    """Check the actual database schema"""
    print("🔍 CHECKING DATABASE SCHEMA")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check user_picks table structure
        print("\n1. USER_PICKS TABLE STRUCTURE:")
        cursor.execute("PRAGMA table_info(user_picks)")
        picks_columns = cursor.fetchall()
        for col in picks_columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Check tiebreaker_predictions table structure
        print("\n2. TIEBREAKER_PREDICTIONS TABLE STRUCTURE:")
        cursor.execute("PRAGMA table_info(tiebreaker_predictions)")
        tiebreaker_columns = cursor.fetchall()
        for col in tiebreaker_columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Check nfl_games table structure
        print("\n3. NFL_GAMES TABLE STRUCTURE:")
        cursor.execute("PRAGMA table_info(nfl_games)")
        games_columns = cursor.fetchall()
        for col in games_columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Sample some data to understand the structure
        print("\n4. SAMPLE USER_PICKS DATA:")
        cursor.execute("SELECT * FROM user_picks LIMIT 5")
        sample_picks = cursor.fetchall()
        for pick in sample_picks:
            print(f"   {pick}")
        
        print("\n5. SAMPLE NFL_GAMES DATA (WEEK 9):")
        cursor.execute("SELECT id, home_team, away_team, week FROM nfl_games WHERE week = 9 LIMIT 5")
        sample_games = cursor.fetchall()
        for game in sample_games:
            print(f"   Game {game[0]}: {game[2]} @ {game[1]} (Week {game[3]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    check_database_schema()

if __name__ == "__main__":
    main()