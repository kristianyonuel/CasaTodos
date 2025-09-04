import sqlite3
import os
from werkzeug.security import check_password_hash

def debug_dashboard():
    print("Dashboard Debug Script")
    print("=" * 30)
    
    # Check database file
    if not os.path.exists('nfl_fantasy.db'):
        print("❌ Database file missing!")
        return
    
    print("✓ Database file exists")
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Tables found: {tables}")
        
        # Check users
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"✓ Users: {user_count}")
        
        # Check admin user
        cursor.execute('SELECT id, username FROM users WHERE is_admin = 1')
        admin = cursor.fetchone()
        if admin:
            print(f"✓ Admin user: ID {admin[0]}, Username: {admin[1]}")
        else:
            print("❌ No admin user found")
        
        # Check games
        cursor.execute('SELECT COUNT(*) FROM nfl_games')
        game_count = cursor.fetchone()[0]
        print(f"✓ NFL Games: {game_count}")
        
        if game_count == 0:
            print("ℹ Creating sample games...")
            from app import create_sample_games
            import datetime
            
            current_year = datetime.datetime.now().year
            sample_games = create_sample_games(1, current_year)
            
            for game in sample_games:
                cursor.execute('''
                    INSERT INTO nfl_games 
                    (game_id, week, year, home_team, away_team, game_date, is_monday_night, is_thursday_night)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (game['game_id'], game['week'], game['year'], game['home_team'], 
                      game['away_team'], game['game_date'], game['is_monday_night'], game['is_thursday_night']))
            
            conn.commit()
            print(f"✓ Created {len(sample_games)} sample games")
        
        # Check picks
        cursor.execute('SELECT COUNT(*) FROM user_picks')
        pick_count = cursor.fetchone()[0]
        print(f"✓ User Picks: {pick_count}")
        
        conn.close()
        print("\n✓ Dashboard should work now!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dashboard()
