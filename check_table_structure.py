#!/usr/bin/env python3

import sqlite3

def check_table_structure():
    """Check the actual structure of the user_picks table"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== USER_PICKS TABLE STRUCTURE ===")
    cursor.execute("PRAGMA table_info(user_picks)")
    columns = cursor.fetchall()
    
    print("Columns in user_picks table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - Nullable: {not col[3]}")
    
    print("\n=== NFL_GAMES TABLE STRUCTURE ===")
    cursor.execute("PRAGMA table_info(nfl_games)")
    columns = cursor.fetchall()
    
    print("Columns in nfl_games table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - Nullable: {not col[3]}")
    
    print("\n=== SAMPLE DATA ===")
    cursor.execute("SELECT * FROM user_picks LIMIT 3")
    picks = cursor.fetchall()
    if picks:
        print("Sample picks data:")
        for pick in picks:
            print(f"  {pick}")
    else:
        print("No picks found")
    
    conn.close()

if __name__ == '__main__':
    check_table_structure()
