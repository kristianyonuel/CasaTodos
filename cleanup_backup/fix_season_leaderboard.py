#!/usr/bin/env python3

"""
Automatic Weekly Results Updater
Finds and updates all weeks that have completed games but may be missing weekly results
"""

import sqlite3
from scoring_updater import ScoringUpdater
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_all_missing_weekly_results():
    """Find and update all weeks that have completed games but missing/incomplete weekly results"""
    
    print("🔄 Automatic Weekly Results Updater")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Find weeks with completed games that might need results updates
    cursor.execute('''
        SELECT DISTINCT g.week, g.year,
               COUNT(*) as total_games,
               SUM(CASE WHEN g.is_final = 1 THEN 1 ELSE 0 END) as completed_games,
               (SELECT COUNT(*) FROM weekly_results wr 
                WHERE wr.week = g.week AND wr.year = g.year) as result_records,
               (SELECT COUNT(*) FROM weekly_results wr 
                WHERE wr.week = g.week AND wr.year = g.year AND wr.is_winner = 1) as winners
        FROM nfl_games g
        WHERE g.year = 2025
        GROUP BY g.week, g.year
        HAVING completed_games > 0
        ORDER BY g.week DESC
    ''')
    
    weeks_data = cursor.fetchall()
    conn.close()
    
    updater = ScoringUpdater('nfl_fantasy.db')
    updated_weeks = []
    
    print("📊 Checking weeks for results updates:")
    
    for week, year, total_games, completed_games, result_records, winners in weeks_data:
        week_complete = total_games == completed_games
        needs_update = False
        
        print(f"\n📅 Week {week}, {year}:")
        print(f"   Games: {completed_games}/{total_games} completed")
        print(f"   Results: {result_records} records, {winners} winner(s)")
        
        # Determine if update is needed
        if completed_games > 0 and result_records == 0:
            print("   🔄 NEEDS UPDATE: No results records found")
            needs_update = True
        elif week_complete and winners == 0:
            print("   🔄 NEEDS UPDATE: Week complete but no winner declared")
            needs_update = True
        elif completed_games > 0:
            print("   ✅ UPDATE: Refresh results for completed games")
            needs_update = True
        else:
            print("   ⏸️ SKIP: No completed games")
        
        if needs_update:
            print(f"   🔧 Updating Week {week} results...")
            success = updater.update_weekly_results(week, year)
            
            if success:
                print(f"   ✅ Week {week} updated successfully")
                updated_weeks.append((week, year))
            else:
                print(f"   ❌ Failed to update Week {week}")
    
    print(f"\n🏁 Summary: Updated {len(updated_weeks)} weeks")
    for week, year in updated_weeks:
        print(f"   ✅ Week {week}, {year}")
    
    # Show final current standings
    print(f"\n🏆 Updated Season Leaderboard:")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.username,
               COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) as weekly_wins
        FROM users u
        LEFT JOIN weekly_results wr ON u.id = wr.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username
        ORDER BY weekly_wins DESC, u.username
    ''')
    
    leaderboard = cursor.fetchall()
    
    for rank, (username, wins) in enumerate(leaderboard, 1):
        print(f"   {rank}. {username}: {wins} weekly wins")
    
    conn.close()

if __name__ == "__main__":
    update_all_missing_weekly_results()