#!/usr/bin/env python3
"""
Robust scoring fix script for Ubuntu server
Handles different database schemas and fixes WSH@GB game scoring
"""

import sqlite3
import os
import sys
from datetime import datetime

def find_database():
    """Find the database file"""
    possible_paths = [
        '/home/casa/CasaTodos/nfl_fantasy.db',
        '/home/casa/CasaTodos/database.db', 
        './nfl_fantasy.db',
        './database.db',
        'nfl_fantasy.db',
        'database.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found database: {path}")
            return path
    
    print("❌ No database found!")
    return None

def check_schema(cursor):
    """Check database schema and available columns"""
    print("\n=== CHECKING DATABASE SCHEMA ===")
    
    # Check nfl_games table structure
    cursor.execute("PRAGMA table_info(nfl_games)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"nfl_games columns: {', '.join(columns)}")
    
    has_winner = 'winner' in columns
    has_home_score = 'home_score' in columns
    has_away_score = 'away_score' in columns
    
    print(f"Has winner column: {has_winner}")
    print(f"Has score columns: {has_home_score and has_away_score}")
    
    return {
        'has_winner': has_winner,
        'has_scores': has_home_score and has_away_score,
        'columns': columns
    }

def find_wsh_gb_game(cursor):
    """Find the WSH@GB game for Week 2, 2025"""
    print("\n=== FINDING WSH@GB GAME ===")
    
    # Try different ways to find the game
    queries = [
        # Direct match
        "SELECT id, home_team, away_team, week, year FROM nfl_games WHERE week = 2 AND year = 2025 AND ((home_team = 'GB' AND away_team = 'WSH') OR (home_team = 'WSH' AND away_team = 'GB'))",
        
        # Case insensitive
        "SELECT id, home_team, away_team, week, year FROM nfl_games WHERE week = 2 AND year = 2025 AND ((UPPER(home_team) = 'GB' AND UPPER(away_team) = 'WSH') OR (UPPER(home_team) = 'WSH' AND UPPER(away_team) = 'GB'))",
        
        # Partial match
        "SELECT id, home_team, away_team, week, year FROM nfl_games WHERE week = 2 AND year = 2025 AND (home_team LIKE '%GB%' OR away_team LIKE '%GB%') AND (home_team LIKE '%WSH%' OR away_team LIKE '%WSH%')",
        
        # Look for Green Bay variations
        "SELECT id, home_team, away_team, week, year FROM nfl_games WHERE week = 2 AND year = 2025 AND (home_team IN ('GB', 'Green Bay', 'GreenBay', 'Packers') OR away_team IN ('GB', 'Green Bay', 'GreenBay', 'Packers'))",
        
        # Look for Washington variations  
        "SELECT id, home_team, away_team, week, year FROM nfl_games WHERE week = 2 AND year = 2025 AND (home_team IN ('WSH', 'WAS', 'Washington', 'Commanders') OR away_team IN ('WSH', 'WAS', 'Washington', 'Commanders'))"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query[:80]}...")
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print(f"  Found {len(results)} games:")
            for game in results:
                print(f"    Game {game[0]}: {game[2]} @ {game[1]} (Week {game[3]}, {game[4]})")
            
            # Return the first match
            return results[0][0], results[0][1], results[0][2]
    
    print("❌ No WSH@GB game found with standard queries")
    
    # Last resort - show all Week 2 games
    print("\nAll Week 2, 2025 games:")
    cursor.execute("SELECT id, home_team, away_team, week, year FROM nfl_games WHERE week = 2 AND year = 2025")
    games = cursor.fetchall()
    
    for game in games:
        print(f"  Game {game[0]}: {game[2]} @ {game[1]}")
    
    return None, None, None

def check_current_picks(cursor, game_id):
    """Check current pick status for the game"""
    print(f"\n=== CHECKING PICKS FOR GAME {game_id} ===")
    
    cursor.execute('''
        SELECT u.username, up.selected_team, up.is_correct
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        WHERE up.game_id = ? AND u.is_admin = 0
        ORDER BY u.username
    ''', (game_id,))
    
    picks = cursor.fetchall()
    
    if not picks:
        print("❌ No picks found for this game!")
        return picks
    
    print(f"Current picks for game {game_id}:")
    for username, selected, correct in picks:
        status = "✅ CORRECT" if correct == 1 else "❌ INCORRECT"
        print(f"  {username}: picked {selected} - {status}")
    
    return picks

def fix_scoring(cursor, game_id, home_team, away_team, schema_info):
    """Fix the scoring for the WSH@GB game"""
    print(f"\n=== FIXING SCORING FOR GAME {game_id} ===")
    
    # Determine who won based on known result: GB 27, WSH 18
    print("Known result: GB 27 - WSH 18 (Green Bay won)")
    
    # GB wins, so:
    # - Users who picked GB should have is_correct = 1
    # - Users who picked WSH should have is_correct = 0
    
    gb_variations = ['GB', 'Green Bay', 'GreenBay', 'Packers']
    wsh_variations = ['WSH', 'WAS', 'Washington', 'Commanders']
    
    # Determine which team codes to use
    if home_team in gb_variations:
        gb_team = home_team
        wsh_team = away_team
    elif away_team in gb_variations:
        gb_team = away_team  
        wsh_team = home_team
    elif home_team in wsh_variations:
        wsh_team = home_team
        gb_team = away_team
    elif away_team in wsh_variations:
        wsh_team = away_team
        gb_team = home_team
    else:
        print(f"❌ Cannot determine GB/WSH team codes from {home_team} vs {away_team}")
        return False
    
    print(f"Using team codes: GB={gb_team}, WSH={wsh_team}")
    
    # Update picks for GB winners (should be correct)
    cursor.execute('''
        UPDATE user_picks 
        SET is_correct = 1 
        WHERE game_id = ? AND selected_team = ?
    ''', (game_id, gb_team))
    
    gb_updates = cursor.rowcount
    print(f"✅ Set {gb_updates} GB picks to CORRECT")
    
    # Update picks for WSH losers (should be incorrect)  
    cursor.execute('''
        UPDATE user_picks 
        SET is_correct = 0 
        WHERE game_id = ? AND selected_team = ?
    ''', (game_id, wsh_team))
    
    wsh_updates = cursor.rowcount
    print(f"✅ Set {wsh_updates} WSH picks to INCORRECT")
    
    # Update game scores if columns exist
    if schema_info['has_scores']:
        cursor.execute('''
            UPDATE nfl_games 
            SET home_score = ?, away_score = ?, is_final = 1
            WHERE id = ?
        ''', (27 if home_team == gb_team else 18, 
              18 if home_team == gb_team else 27, 
              game_id))
        print("✅ Updated game scores: GB 27, WSH 18")
    
    # Update winner if column exists
    if schema_info['has_winner']:
        cursor.execute('''
            UPDATE nfl_games 
            SET winner = ?
            WHERE id = ?
        ''', (gb_team, game_id))
        print(f"✅ Set winner to {gb_team}")
    
    return True

def verify_fix(cursor, game_id):
    """Verify the fix was applied correctly"""
    print(f"\n=== VERIFYING FIX FOR GAME {game_id} ===")
    
    cursor.execute('''
        SELECT u.username, up.selected_team, up.is_correct
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        WHERE up.game_id = ? AND u.is_admin = 0
        ORDER BY up.is_correct DESC, u.username
    ''', (game_id,))
    
    picks = cursor.fetchall()
    
    correct_count = 0
    incorrect_count = 0
    
    print("After fix:")
    for username, selected, correct in picks:
        if correct == 1:
            print(f"  ✅ {username}: picked {selected} - CORRECT (1 point)")
            correct_count += 1
        else:
            print(f"  ❌ {username}: picked {selected} - INCORRECT (0 points)")
            incorrect_count += 1
    
    print(f"\nSummary: {correct_count} correct picks, {incorrect_count} incorrect picks")
    
    return correct_count, incorrect_count

def main():
    """Main execution function"""
    print("🏈 ROBUST UBUNTU SCORING FIX SCRIPT")
    print("=" * 50)
    
    # Find database
    db_path = find_database()
    if not db_path:
        print("❌ Could not find database file!")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check schema
        schema_info = check_schema(cursor)
        
        # Find WSH@GB game
        game_id, home_team, away_team = find_wsh_gb_game(cursor)
        
        if not game_id:
            print("❌ Could not find WSH@GB game!")
            conn.close()
            sys.exit(1)
        
        print(f"\n🎯 Found target game: {game_id} ({away_team} @ {home_team})")
        
        # Check current picks
        picks_before = check_current_picks(cursor, game_id)
        
        if not picks_before:
            print("❌ No picks to fix!")
            conn.close()
            sys.exit(1)
        
        # Ask for confirmation
        print(f"\n⚠️  About to fix scoring for game {game_id}")
        print("This will update user pick correctness based on GB winning 27-18")
        
        response = input("Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Fix cancelled by user")
            conn.close()
            sys.exit(0)
        
        # Apply fix
        success = fix_scoring(cursor, game_id, home_team, away_team, schema_info)
        
        if not success:
            print("❌ Fix failed!")
            conn.rollback()
            conn.close()
            sys.exit(1)
        
        # Verify fix
        correct_count, incorrect_count = verify_fix(cursor, game_id)
        
        # Commit changes
        conn.commit()
        
        print("\n🎉 SCORING FIX COMPLETED SUCCESSFULLY!")
        print(f"   - {correct_count} users now have correct picks (GB winners)")
        print(f"   - {incorrect_count} users now have incorrect picks (WSH pickers)")
        print("   - Weekly leaderboard should now show accurate results")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    main()
