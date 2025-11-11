#!/usr/bin/env python3
"""
Check database schema to understand table structure
"""

import sqlite3

def check_database_schema():
    """Check the actual database schema"""
    print("=" * 60)
    print("CHECKING DATABASE SCHEMA")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Available tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check user_picks table structure
    print("\n" + "=" * 40)
    print("USER_PICKS TABLE STRUCTURE")
    print("=" * 40)
    
    cursor.execute("PRAGMA table_info(user_picks)")
    columns = cursor.fetchall()
    
    print("Columns in user_picks table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - PK: {col[5]}, Not Null: {col[3]}, Default: {col[4]}")
    
    # Check nfl_games table structure
    print("\n" + "=" * 40)
    print("NFL_GAMES TABLE STRUCTURE")
    print("=" * 40)
    
    cursor.execute("PRAGMA table_info(nfl_games)")
    columns = cursor.fetchall()
    
    print("Columns in nfl_games table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - PK: {col[5]}, Not Null: {col[3]}, Default: {col[4]}")
    
    # Sample data from user_picks
    print("\n" + "=" * 40)
    print("SAMPLE USER_PICKS DATA")
    print("=" * 40)
    
    cursor.execute("SELECT * FROM user_picks LIMIT 5")
    sample_picks = cursor.fetchall()
    
    for pick in sample_picks:
        print(f"  {pick}")
    
    # Sample data from nfl_games
    print("\n" + "=" * 40)
    print("SAMPLE NFL_GAMES DATA")
    print("=" * 40)
    
    cursor.execute("SELECT * FROM nfl_games LIMIT 3")
    sample_games = cursor.fetchall()
    
    for game in sample_games:
        print(f"  {game}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("SCHEMA CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    check_database_schema()