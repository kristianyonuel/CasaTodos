import sqlite3
from datetime import datetime

def debug_current_week_issue():
    """Debug why the app still thinks it's Week 9"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔍 DEBUGGING CURRENT WEEK ISSUE")
    print("=" * 50)
    
    # Check current_week setting
    cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
    current_week_setting = cursor.fetchone()
    print(f"1. current_week setting: {current_week_setting[0] if current_week_setting else 'NOT FOUND'}")
    
    # Check what week has the most recent game
    cursor.execute('''
        SELECT week, COUNT(*) as games, 
               MAX(game_date) as latest_game,
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games
        FROM nfl_games 
        WHERE year = 2025 AND game_date <= datetime('now')
        GROUP BY week 
        ORDER BY week DESC 
        LIMIT 3
    ''')
    recent_weeks = cursor.fetchall()
    
    print(f"\n2. Recent weeks by game date:")
    for week, games, latest, final in recent_weeks:
        status = "Complete" if games == final else f"{final}/{games} done"
        print(f"   Week {week}: {latest} ({status})")
    
    # Check which week has games starting soon
    now = datetime.now()
    cursor.execute('''
        SELECT week, MIN(game_date) as first_game, COUNT(*) as games
        FROM nfl_games 
        WHERE year = 2025 AND game_date >= datetime('now')
        GROUP BY week 
        ORDER BY week 
        LIMIT 3
    ''')
    upcoming_weeks = cursor.fetchall()
    
    print(f"\n3. Upcoming weeks:")
    for week, first_game, games in upcoming_weeks:
        print(f"   Week {week}: {first_game} ({games} games)")
    
    # Check if there's any specific logic for "current week" calculation
    print(f"\n4. Current time: {now}")
    
    # The app might be using ESPN API or another method to determine current week
    # Let's check what Week 10's first game time is
    cursor.execute('''
        SELECT MIN(game_date), MAX(game_date), COUNT(*)
        FROM nfl_games 
        WHERE week = 10 AND year = 2025
    ''')
    week10_info = cursor.fetchone()
    
    if week10_info and week10_info[0]:
        first_game = datetime.strptime(week10_info[0], '%Y-%m-%d %H:%M:%S')
        print(f"\n5. Week 10 starts: {week10_info[0]}")
        print(f"   Time until Week 10: {first_game - now}")
        
        if now >= first_game:
            print("   ✅ Week 10 should be active (first game time passed)")
        else:
            print("   ⏰ Week 10 not yet active (first game is future)")
    
    conn.close()
    
    print(f"\n🎯 DIAGNOSIS:")
    print(f"The app might be:")
    print(f"1. Ignoring the current_week setting")
    print(f"2. Using ESPN API to determine current week")
    print(f"3. Using game dates to auto-calculate current week")
    print(f"4. Hardcoded to Week 9 somewhere")

if __name__ == "__main__":
    debug_current_week_issue()