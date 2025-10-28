#!/usr/bin/env python3
"""
Recalculate Season Standings from Weekly Leaderboards
=====================================================

This script properly calculates season standings by:
1. Looking at each week's results in weekly_results table
2. Finding who had the highest score each week
3. Handling ties properly
4. Updating is_winner flags and user_statistics accordingly

This ensures the season standings match what actually happened each week.

Created: October 28, 2025
"""

import sqlite3
from datetime import datetime

def recalculate_season_from_weekly_results():
    print("🔄 Recalculating Season Standings from Weekly Results")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Clear all existing is_winner flags
    print("🧹 Clearing all existing is_winner flags...")
    cursor.execute("UPDATE weekly_results SET is_winner = 0 WHERE year = 2025")
    
    # Get all weeks that have been played
    cursor.execute("""
        SELECT DISTINCT week 
        FROM weekly_results 
        WHERE year = 2025 AND total_picks > 0
        ORDER BY week
    """)
    
    played_weeks = [row[0] for row in cursor.fetchall()]
    print(f"📅 Weeks played: {played_weeks}")
    
    weekly_winners = {}
    
    # Process each week
    for week in played_weeks:
        print(f"\n📊 Processing Week {week}:")
        
        # Get all results for this week
        cursor.execute("""
            SELECT u.username, wr.correct_picks, wr.total_picks, wr.user_id
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = ? AND wr.year = 2025 AND wr.total_picks > 0
            ORDER BY wr.correct_picks DESC, u.username
        """, (week,))
        
        week_results = cursor.fetchall()
        
        if not week_results:
            print(f"  ⚠️ No results found for Week {week}")
            continue
        
        # Find the maximum score
        max_score = week_results[0][1]  # correct_picks of first (highest) result
        print(f"  Max score: {max_score}")
        
        # Find all players with the maximum score (handle ties)
        week_winners = []
        for username, correct, total, user_id in week_results:
            if correct == max_score:
                week_winners.append((username, user_id, correct, total))
                print(f"    {username.upper()}: {correct}/{total} 👑")
            else:
                print(f"    {username.upper()}: {correct}/{total}")
        
        # Set is_winner flags for this week's winners
        for username, user_id, correct, total in week_winners:
            cursor.execute("""
                UPDATE weekly_results 
                SET is_winner = 1 
                WHERE user_id = ? AND week = ? AND year = 2025
            """, (user_id, week))
        
        weekly_winners[week] = week_winners
        
        if len(week_winners) > 1:
            winner_names = [w[0].upper() for w in week_winners]
            print(f"  🤝 TIE: {' & '.join(winner_names)}")
        else:
            print(f"  🏆 WINNER: {week_winners[0][0].upper()}")
    
    conn.commit()
    
    # Calculate season standings
    print(f"\n📈 SEASON STANDINGS CALCULATION:")
    print("=" * 40)
    
    season_wins = {}
    for week, winners in weekly_winners.items():
        print(f"Week {week}: ", end="")
        if len(winners) > 1:
            winner_names = [w[0].upper() for w in winners]
            print(f"{' & '.join(winner_names)} (TIE)")
        else:
            print(f"{winners[0][0].upper()}")
        
        for username, user_id, correct, total in winners:
            username_upper = username.upper()
            season_wins[username_upper] = season_wins.get(username_upper, 0) + 1
    
    print(f"\n🏆 FINAL SEASON STANDINGS:")
    print("-" * 30)
    sorted_standings = sorted(season_wins.items(), key=lambda x: x[1], reverse=True)
    
    for i, (username, wins) in enumerate(sorted_standings, 1):
        if i == 1:
            emoji = "🏆"
        elif i == 2:
            emoji = "🥈"
        elif i == 3:
            emoji = "🥉"
        else:
            emoji = f"{i}."
        print(f"  {emoji} {username}: {wins} wins")
    
    # Update user_statistics table
    print(f"\n🔄 Updating user_statistics table...")
    
    # Reset all wins to 0 first
    cursor.execute("UPDATE user_statistics SET total_wins = 0 WHERE 1=1")
    
    # Update with calculated wins
    for username, wins in season_wins.items():
        cursor.execute("""
            UPDATE user_statistics 
            SET total_wins = ?, updated_at = datetime('now')
            WHERE user_id = (SELECT id FROM users WHERE UPPER(username) = ?)
        """, (wins, username))
        print(f"  {username}: {wins} wins ✅")
    
    conn.commit()
    
    # Verification - show all weekly winners
    print(f"\n✅ VERIFICATION - All Weekly Winners:")
    print("-" * 50)
    cursor.execute("""
        SELECT wr.week, u.username, wr.correct_picks, wr.total_picks
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.year = 2025 AND wr.is_winner = 1
        ORDER BY wr.week, u.username
    """)
    
    all_winners = cursor.fetchall()
    for week, username, correct, total in all_winners:
        print(f"  Week {week}: {username.upper()} ({correct}/{total})")
    
    # Final user_statistics verification
    print(f"\n📊 FINAL USER_STATISTICS TABLE:")
    cursor.execute("""
        SELECT u.username, us.total_wins
        FROM user_statistics us
        JOIN users u ON us.user_id = u.id
        WHERE us.total_wins > 0
        ORDER BY us.total_wins DESC, u.username
    """)
    
    final_stats = cursor.fetchall()
    for username, wins in final_stats:
        print(f"  {username.upper()}: {wins} wins")
    
    conn.close()
    
    print(f"\n🎉 SEASON STANDINGS RECALCULATED!")
    print("=" * 40)
    print("✅ Season standings now correctly calculated from weekly results")
    print("✅ All is_winner flags updated")
    print("✅ user_statistics table updated")
    print()
    print("🔄 Restart your app to see the corrected leaderboard!")

if __name__ == "__main__":
    recalculate_season_from_weekly_results()