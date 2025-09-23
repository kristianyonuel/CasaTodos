#!/usr/bin/env python3
"""
CORRECT Server Database Fix Script
Run this on Ubuntu server - handles actual database schema
"""

import sqlite3

def fix_server_database():
    print("=== APPLYING CORRECT SERVER FIXES ===")
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Fix 1: Check current game times that need fixing
        print("\n1. Checking current Sunday game times...")
        
        cursor.execute("""
            SELECT game_date, home_team, away_team 
            FROM nfl_games 
            WHERE date(game_date) = '2025-09-21'
            AND time(game_date) = '13:00:00'
        """)
        
        games_to_fix = cursor.fetchall()
        
        if games_to_fix:
            print(f"   Found {len(games_to_fix)} games with 13:00 time that need fixing:")
            for game_date, home, away in games_to_fix:
                print(f"     {game_date} - {home} vs {away}")
            
            # Update the games (change 13:00 to 17:00 on Sept 21)
            cursor.execute("""
                UPDATE nfl_games 
                SET game_date = '2025-09-21 17:00:00'
                WHERE date(game_date) = '2025-09-21' 
                AND time(game_date) = '13:00:00'
            """)
            
            fixed_games = cursor.rowcount
            print(f"   ✅ Updated {fixed_games} games from 13:00 to 17:00 UTC")
        else:
            print("   ✅ No games need time fixing (already correct)")
        
        # Fix 2: Clear premature Week 3 winners
        print("\n2. Checking Week 3 winner status...")
        
        cursor.execute("""
            SELECT u.username 
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = 3 AND wr.year = 2025 AND wr.is_winner = 1
        """)
        
        premature_winners = cursor.fetchall()
        
        if premature_winners:
            winner_names = [w[0] for w in premature_winners]
            print(f"   Found premature winners: {winner_names}")
            
            cursor.execute("""
                UPDATE weekly_results 
                SET is_winner = 0 
                WHERE week = 3 AND year = 2025 AND is_winner = 1
            """)
            
            cleared = cursor.rowcount
            print(f"   ✅ Cleared {cleared} premature Week 3 winners")
        else:
            print("   ✅ No premature winners found")
        
        # Commit all changes
        conn.commit()
        
        # Verification
        print("\n=== VERIFICATION ===")
        
        # Check Sunday game times
        cursor.execute("""
            SELECT COUNT(*) 
            FROM nfl_games 
            WHERE date(game_date) = '2025-09-21' 
            AND time(game_date) = '17:00:00'
        """)
        correct_times = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM nfl_games 
            WHERE date(game_date) = '2025-09-21' 
            AND time(game_date) = '13:00:00'
        """)
        wrong_times = cursor.fetchone()[0]
        
        print(f"✅ Sunday games with 17:00 UTC (correct): {correct_times}")
        print(f"❌ Sunday games with 13:00 UTC (wrong): {wrong_times}")
        
        # Check Week 3 status
        cursor.execute("""
            SELECT COUNT(*) 
            FROM weekly_results 
            WHERE week = 3 AND year = 2025 AND is_winner = 1
        """)
        week3_winners = cursor.fetchone()[0]
        print(f"✅ Week 3 premature winners: {week3_winners} (should be 0)")
        
        conn.close()
        
        print(f"\n🎉 SERVER DATABASE FIXES COMPLETE!")
        print(f"Your server will now show:")
        print(f"  - Sunday games at 1:00 PM AST (not 9:00 AM)")
        print(f"  - Only legitimate weekly winners in leaderboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_server_database()
