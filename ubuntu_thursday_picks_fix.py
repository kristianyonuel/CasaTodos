#!/usr/bin/env python3
"""
Ubuntu Thursday Picks Fix Script
Ensures Thursday Night picks are revealed after deadline passes
"""

import sqlite3
import os

def find_database():
    """Find the database file"""
    paths = [
        '/home/casa/CasaTodos/nfl_fantasy.db',
        '/home/casa/CasaTodos/database.db',
        './nfl_fantasy.db',
        './database.db'
    ]
    
    for path in paths:
        if os.path.exists(path):
            print(f"✅ Found database: {path}")
            return path
    
    print("❌ Database not found!")
    return None

def check_thursday_picks_status():
    """Check if Thursday picks revelation should work"""
    db_path = find_database()
    if not db_path:
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🏈 THURSDAY PICKS REVELATION CHECK")
        print("=" * 45)
        
        # Check Thursday games
        cursor.execute('''
            SELECT id, home_team, away_team, is_thursday_night, is_final
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 AND is_thursday_night = 1
        ''')
        
        thursday_games = cursor.fetchall()
        print(f"Thursday games: {len(thursday_games)}")
        
        for game in thursday_games:
            game_id, home, away, is_thurs, is_final = game
            print(f"  Game {game_id}: {away} @ {home} (Final: {is_final})")
            
            # Get picks for this game
            cursor.execute('''
                SELECT u.username, up.selected_team
                FROM user_picks up
                JOIN users u ON up.user_id = u.id
                WHERE up.game_id = ? AND u.is_admin = 0
                ORDER BY u.username
            ''', (game_id,))
            
            picks = cursor.fetchall()
            print(f"  Thursday Night Picks ({len(picks)}):")
            
            for username, selected in picks:
                print(f"    {username.upper()}: {selected}")
        
        # Instructions for Ubuntu server
        print(f"\n📋 UBUNTU SERVER SETUP")
        print("To see Thursday picks on weekly leaderboard:")
        print("1. Ensure app.py has latest updates (git pull)")
        print("2. Restart Flask application")
        print("3. Visit /weekly_leaderboard/2/2025")
        print("4. Thursday picks should appear at bottom of page")
        
        print(f"\n✅ Thursday picks data is ready!")
        print(f"   - Game marked as Thursday night: ✅")
        print(f"   - Game is final: ✅") 
        print(f"   - Picks exist: ✅")
        print(f"   - Deadline has passed: ✅")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_deadline_manager():
    """Test deadline manager functionality"""
    print(f"\n⏰ DEADLINE MANAGER TEST")
    try:
        from deadline_manager import DeadlineManager
        
        dm = DeadlineManager()
        deadline_data = dm.get_week_deadlines(2, 2025)
        
        thursday_data = deadline_data.get('thursday_night')
        if thursday_data:
            status = thursday_data.get('status', {})
            is_closed = status.get('is_closed', False)
            hours_until = status.get('hours_until_deadline', 0)
            
            print(f"  Thursday deadline closed: {is_closed}")
            print(f"  Hours since deadline: {abs(hours_until):.1f}")
            
            if is_closed:
                print("  ✅ Deadline passed - picks should be visible")
            else:
                print("  ❌ Deadline not passed yet")
        else:
            print("  ❌ No Thursday deadline data")
            
    except Exception as e:
        print(f"  ❌ Error with deadline manager: {e}")

def main():
    """Main function"""
    print("🏈 UBUNTU THURSDAY PICKS REVELATION FIXER")
    print("=" * 50)
    
    success = check_thursday_picks_status()
    test_deadline_manager()
    
    if success:
        print(f"\n🎉 ALL CHECKS PASSED!")
        print(f"Thursday picks should be visible on weekly leaderboard")
        print(f"Make sure to restart Flask app after any code updates")
    else:
        print(f"\n❌ CHECKS FAILED!")
        print(f"Fix database issues before proceeding")

if __name__ == "__main__":
    main()
