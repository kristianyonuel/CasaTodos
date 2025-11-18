import sqlite3
from datetime import datetime

def check_current_week_logic():
    """Check what determines the current week in the system"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔍 CURRENT WEEK LOGIC ANALYSIS")
    print("=" * 50)
    
    # Check current date
    now = datetime.now()
    print(f"Current Date/Time: {now}")
    
    # Check Week 9 status
    cursor.execute('''
        SELECT COUNT(*) as total_games,
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
               MAX(game_date) as last_game_date
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
    ''')
    
    week9_info = cursor.fetchone()
    if week9_info:
        total, final, last_game = week9_info
        print(f"\nWeek 9 Status: {final}/{total} games complete")
        print(f"Last Week 9 game: {last_game}")
        week9_complete = (total == final)
        print(f"Week 9 Complete: {'✅ YES' if week9_complete else '❌ NO'}")
    
    # Check Week 10 status
    cursor.execute('''
        SELECT COUNT(*) as total_games,
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
               MIN(game_date) as first_game_date
        FROM nfl_games 
        WHERE week = 10 AND year = 2025
    ''')
    
    week10_info = cursor.fetchone()
    if week10_info:
        total, final, first_game = week10_info
        print(f"\nWeek 10 Status: {final}/{total} games complete")
        print(f"First Week 10 game: {first_game}")
        
        # Check if Week 10 has started
        if first_game:
            first_game_dt = datetime.strptime(first_game, '%Y-%m-%d %H:%M:%S')
            week10_started = now >= first_game_dt
            print(f"Week 10 Started: {'✅ YES' if week10_started else '❌ NO'}")
        else:
            print("Week 10 Started: ❌ NO (no games scheduled)")
    
    # Check what the app logic should show
    print(f"\n📊 RECOMMENDATION:")
    if week9_info and week10_info:
        week9_total, week9_final, _ = week9_info
        week10_total, _, week10_first = week10_info
        
        if week9_total == week9_final:  # Week 9 complete
            if week10_first:
                week10_first_dt = datetime.strptime(week10_first, '%Y-%m-%d %H:%M:%S')
                if now >= week10_first_dt:
                    print("✅ Show Week 10 (Week 9 complete, Week 10 started)")
                else:
                    print("🔄 Show Week 10 for upcoming picks (Week 9 complete)")
            else:
                print("❌ No Week 10 games found")
        else:
            print("🔄 Show Week 9 (still in progress)")
    
    # Check if there's any setting controlling current week
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='league_settings'")
    if cursor.fetchone():
        cursor.execute("SELECT * FROM league_settings WHERE setting_name LIKE '%week%' OR setting_name LIKE '%current%'")
        settings = cursor.fetchall()
        if settings:
            print(f"\n⚙️ LEAGUE SETTINGS:")
            for setting in settings:
                print(f"  {setting}")
    
    conn.close()

if __name__ == "__main__":
    check_current_week_logic()