#!/usr/bin/env python3
"""
Test the weekly leaderboard functionality
"""

import sqlite3
from datetime import datetime

def test_weekly_leaderboard_data():
    """Test if we have the necessary data for weekly leaderboard"""
    
    print("🧪 TESTING WEEKLY LEADERBOARD DATA")
    print("="*50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        user_count = cursor.fetchone()[0]
        print(f"Non-admin users: {user_count}")
        
        # Check if we have games
        cursor.execute('SELECT COUNT(*) FROM nfl_games')
        total_games = cursor.fetchone()[0]
        print(f"Total games: {total_games}")
        
        # Check if we have completed games
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final = 1')
        completed_games = cursor.fetchone()[0]
        print(f"Completed games: {completed_games}")
        
        # Check if we have user picks
        cursor.execute('SELECT COUNT(*) FROM user_picks')
        total_picks = cursor.fetchone()[0]
        print(f"Total user picks: {total_picks}")
        
        # Check weeks with completed games
        cursor.execute('''
            SELECT DISTINCT week, year, COUNT(*) as games
            FROM nfl_games 
            WHERE is_final = 1
            GROUP BY week, year
            ORDER BY year DESC, week DESC
        ''')
        completed_weeks = cursor.fetchall()
        print(f"\nWeeks with completed games:")
        for week, year, games in completed_weeks:
            print(f"  Week {week}, {year}: {games} games")
        
        # Check user picks for completed games
        if completed_weeks:
            week, year, _ = completed_weeks[0]
            cursor.execute('''
                SELECT u.username, COUNT(p.id) as picks, 
                       SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM users u
                JOIN user_picks p ON u.id = p.user_id
                JOIN nfl_games g ON p.game_id = g.id
                WHERE g.week = ? AND g.year = ? AND g.is_final = 1 AND u.is_admin = 0
                GROUP BY u.id, u.username
            ''', (week, year))
            
            user_picks = cursor.fetchall()
            print(f"\nUser picks for Week {week}, {year}:")
            for username, picks, correct in user_picks:
                print(f"  {username}: {picks} picks, {correct} correct")
        
        # Test current week calculation
        current_date = datetime.now()
        season_start = datetime(2025, 9, 4)
        days_since_start = (current_date - season_start).days
        calculated_week = max(1, min(18, (days_since_start // 7) + 1))
        print(f"\nCurrent date: {current_date.strftime('%Y-%m-%d')}")
        print(f"Days since season start: {days_since_start}")
        print(f"Calculated current week: {calculated_week}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing leaderboard data: {e}")
        return False

def create_test_data():
    """Create some test data if none exists"""
    
    print("\n🔧 CREATING TEST DATA")
    print("="*50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we need test data
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final = 1')
        if cursor.fetchone()[0] > 0:
            print("Completed games already exist, skipping test data creation")
            conn.close()
            return
        
        # Create a simple completed game for testing
        cursor.execute('''
            INSERT OR REPLACE INTO nfl_games 
            (game_id, week, year, home_team, away_team, game_date, 
             home_score, away_score, is_final, is_monday_night)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'test_game_1',
            1, 2025,
            'Chiefs', 'Bills',
            '2025-09-04 20:15:00',
            28, 21,
            1,  # is_final
            1   # is_monday_night
        ))
        
        # Add a Sunday game too
        cursor.execute('''
            INSERT OR REPLACE INTO nfl_games 
            (game_id, week, year, home_team, away_team, game_date, 
             home_score, away_score, is_final, is_thursday_night)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'test_game_2',
            1, 2025,
            'Cowboys', 'Giants',
            '2025-09-08 13:00:00',
            24, 17,
            1,  # is_final
            0   # is_thursday_night
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Test games created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return False

def main():
    """Main test function"""
    print("🏈 WEEKLY LEADERBOARD DIAGNOSTICS")
    print("="*60)
    
    # Test existing data
    test_weekly_leaderboard_data()
    
    # Create test data if needed
    create_test_data()
    
    # Test again after creating data
    print("\n" + "="*60)
    print("AFTER TEST DATA CREATION:")
    test_weekly_leaderboard_data()

if __name__ == "__main__":
    main()
