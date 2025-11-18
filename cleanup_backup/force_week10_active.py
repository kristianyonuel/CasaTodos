import sqlite3
from datetime import datetime, timedelta

def force_week10_active():
    """Force the app to show Week 10 by adjusting game times"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔧 FORCING WEEK 10 TO BE ACTIVE")
    print("=" * 50)
    
    # Get current time
    now = datetime.now()
    print(f"Current time: {now}")
    
    # Move the first Week 10 game to 1 hour ago so the app thinks Week 10 is "current"
    one_hour_ago = now - timedelta(hours=1)
    one_hour_ago_str = one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"Setting first Week 10 game to: {one_hour_ago_str}")
    
    # Update only the FIRST Week 10 game to be 1 hour ago
    cursor.execute('''
        UPDATE nfl_games 
        SET game_date = ? 
        WHERE week = 10 AND year = 2025 
        AND game_date = (
            SELECT MIN(game_date) 
            FROM nfl_games 
            WHERE week = 10 AND year = 2025
        )
    ''', (one_hour_ago_str,))
    
    games_updated = cursor.rowcount
    print(f"Updated {games_updated} game(s)")
    
    # Verify the change
    cursor.execute('''
        SELECT home_team, away_team, game_date 
        FROM nfl_games 
        WHERE week = 10 AND year = 2025 
        ORDER BY game_date 
        LIMIT 3
    ''')
    first_games = cursor.fetchall()
    
    print(f"\nFirst 3 Week 10 games after update:")
    for away, home, game_date in first_games:
        status = "PAST" if game_date < now.strftime('%Y-%m-%d %H:%M:%S') else "FUTURE"
        print(f"   {away} @ {home}: {game_date} ({status})")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Week 10 should now be active!")
    print(f"The app's logic (game_date >= now) should now detect Week 10 as current")
    
    return True

if __name__ == "__main__":
    force_week10_active()