import sqlite3
import os
from database import init_database
from game_manager import ensure_games_exist, auto_populate_all_games

def fix_dashboard_issues():
    print("Fixing Dashboard Issues...")
    print("=" * 40)
    
    # Check database file
    if not os.path.exists('nfl_fantasy.db'):
        print("❌ Database missing - creating...")
        init_database()
    else:
        print("✓ Database exists")
    
    # Check critical tables
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ Users: {user_count}")
        
        # Check games table
        cursor.execute("SELECT COUNT(*) FROM nfl_games")
        game_count = cursor.fetchone()[0]
        print(f"✓ Games: {game_count}")
        
        if game_count == 0:
            print("Creating games...")
            auto_populate_all_games()
        
        # Check for current week games
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = 2025")
        week1_count = cursor.fetchone()[0]
        print(f"✓ Week 1 games: {week1_count}")
        
        if week1_count == 0:
            print("Creating Week 1 games...")
            ensure_games_exist(1, 2025)
        
        conn.close()
        print("✅ Dashboard should work now!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_dashboard_issues()
