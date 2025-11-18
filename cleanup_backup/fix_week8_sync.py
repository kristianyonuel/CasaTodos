"""
Simple fix for database_sync emoji encoding issues on Windows
"""
import sqlite3
from database_sync import sync_week_from_api as original_sync_week

def sync_games_for_week(week: int, year: int = 2025) -> int:
    """Safe wrapper for sync_week_from_api that handles encoding issues"""
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr
    
    # Capture output to avoid emoji encoding issues
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    try:
        # Redirect output temporarily
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            result = original_sync_week(week, year)
        
        print(f"Attempting to sync Week {week} games from API...")
        print(f"Sync completed: {result} games processed")
        return result
        
    except Exception as e:
        print(f"Sync failed for Week {week}: {str(e)}")
        return 0

if __name__ == "__main__":
    # Test Week 8 sync
    result = sync_games_for_week(8, 2025)
    
    # Check results
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 8 AND year = 2025")
    count = cursor.fetchone()[0]
    
    print(f"Week 8 games in database: {count}")
    
    if count > 0:
        cursor.execute("SELECT home_team, away_team, game_date FROM nfl_games WHERE week = 8 AND year = 2025 LIMIT 5")
        games = cursor.fetchall()
        print("\nFirst few Week 8 games:")
        for home, away, date in games:
            print(f"  {away} @ {home} - {date}")
    
    conn.close()