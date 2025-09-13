#!/usr/bin/env python3
"""
Fix Weekly Leaderboard Scoring - Ubuntu Server Script

This script fixes the incorrect is_correct values in the user_picks table.
The issue was that all users appeared to have correct picks even when they picked the wrong team.

Usage: python3 fix_scoring_ubuntu.py
"""

import sqlite3
import os

def fix_wsh_gb_scoring():
    """Fix the specific WSH@GB game scoring"""
    
    # Use the database path for Ubuntu server
    db_path = '/path/to/your/nfl_fantasy.db'  # Update this path
    
    # Check if database exists
    if not os.path.exists(db_path):
        # Try common paths
        possible_paths = [
            './nfl_fantasy.db',
            '../nfl_fantasy.db', 
            '/home/ubuntu/CasaTodos/nfl_fantasy.db',
            '/var/www/html/nfl_fantasy.db'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        else:
            print("❌ Could not find nfl_fantasy.db database file")
            print("Please update the db_path variable in this script")
            return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔍 Checking WSH@GB game scoring...")
    
    # Find the WSH@GB game
    cursor.execute('''
        SELECT id, game_id, home_team, away_team, home_score, away_score, is_final
        FROM nfl_games 
        WHERE week = 2 AND year = 2025 
        AND ((home_team = 'WSH' AND away_team = 'GB') OR (home_team = 'GB' AND away_team = 'WSH'))
    ''')
    
    game = cursor.fetchone()
    
    if not game:
        print("❌ WSH@GB game not found in database")
        conn.close()
        return False
    
    db_id = game['id']
    home_team = game['home_team']
    away_team = game['away_team']
    home_score = game['home_score']
    away_score = game['away_score']
    is_final = game['is_final']
    
    print(f"📊 Game found: {away_team} @ {home_team}")
    print(f"📊 Score: {away_score} - {home_score}")
    print(f"📊 Final: {is_final}")
    
    if not is_final:
        print("⚠️  Game is not marked as final")
        conn.close()
        return False
    
    # Determine winner
    if home_score > away_score:
        winning_team = home_team
    elif away_score > home_score:
        winning_team = away_team
    else:
        winning_team = None  # Tie
    
    if not winning_team:
        print("⚠️  Game ended in a tie")
        conn.close()
        return False
    
    print(f"🏆 Winner: {winning_team}")
    
    # Check current picks
    cursor.execute('''
        SELECT u.username, p.selected_team, p.is_correct
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.is_admin = 0
        ORDER BY u.username
    ''', (db_id,))
    
    picks = cursor.fetchall()
    
    if not picks:
        print("❌ No user picks found for this game")
        conn.close()
        return False
    
    print("\n🎯 Current picks (before fix):")
    incorrect_count = 0
    for pick in picks:
        username = pick['username']
        selected = pick['selected_team']
        is_correct = pick['is_correct']
        should_be_correct = selected == winning_team
        
        status = '✅' if is_correct == 1 else '❌' if is_correct == 0 else '?'
        should_status = '✅' if should_be_correct else '❌'
        
        if (is_correct == 1) != should_be_correct:
            incorrect_count += 1
            
        print(f"  {username:12} picked {selected:3} | DB: {status} | Should: {should_status}")
    
    if incorrect_count == 0:
        print("✅ All picks are already correctly scored!")
        conn.close()
        return True
    
    print(f"\n🔧 Found {incorrect_count} incorrectly scored picks. Fixing...")
    
    # Fix the scoring
    # Update correct picks
    cursor.execute('''
        UPDATE user_picks 
        SET is_correct = 1
        WHERE game_id = ? AND selected_team = ?
    ''', (db_id, winning_team))
    
    correct_updates = cursor.rowcount
    
    # Update incorrect picks
    cursor.execute('''
        UPDATE user_picks 
        SET is_correct = 0
        WHERE game_id = ? AND selected_team != ?
    ''', (db_id, winning_team))
    
    incorrect_updates = cursor.rowcount
    
    conn.commit()
    
    print(f"✅ Updated {correct_updates} picks to CORRECT")
    print(f"✅ Updated {incorrect_updates} picks to INCORRECT")
    
    # Verify the fix
    print("\n🎯 Picks after fix:")
    cursor.execute('''
        SELECT u.username, p.selected_team, p.is_correct
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.is_admin = 0
        ORDER BY p.is_correct DESC, u.username
    ''', (db_id,))
    
    picks = cursor.fetchall()
    
    for pick in picks:
        username = pick['username']
        selected = pick['selected_team']
        is_correct = pick['is_correct']
        
        status = '✅' if is_correct == 1 else '❌'
        print(f"  {username:12} picked {selected:3} {status}")
    
    conn.close()
    return True

def main():
    """Main function to fix scoring issues"""
    print("🏈 Weekly Leaderboard Scoring Fix")
    print("=" * 50)
    
    success = fix_wsh_gb_scoring()
    
    if success:
        print("\n✅ Scoring fix completed successfully!")
        print("📱 The weekly leaderboard should now show correct results")
        print("🚀 Only users who picked the winning team will have points")
    else:
        print("\n❌ Scoring fix failed")
        print("💡 Please check the error messages above")

if __name__ == "__main__":
    main()
