"""
Run scoring system without emoji encoding issues
"""
import sqlite3
import sys
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Import the scoring function
sys.path.append(os.getcwd())
from nfl_week_scorer import score_specific_week

def safe_score_week(week, year=2025):
    """Score a week while suppressing emoji output"""
    # Capture all output to avoid emoji encoding errors
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    
    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            result = score_specific_week(week, year)
        
        print(f"Week {week} scored successfully")
        return True
        
    except Exception as e:
        print(f"Error scoring Week {week}: {str(e)}")
        return False

def main():
    print("Updating all weekly scores...")
    
    # Score weeks 1-6
    for week in [1, 2, 3, 4, 5, 6]:
        print(f"Scoring Week {week}...")
        safe_score_week(week, 2025)
    
    # Check updated leaderboard
    print("\nChecking updated leaderboard...")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            u.username,
            SUM(COALESCE(wr.total_points, 0)) as season_points,
            SUM(COALESCE(wr.correct_picks, 0)) as season_correct,
            SUM(CASE WHEN wr.is_winner = 1 THEN 1 ELSE 0 END) as weeks_won
        FROM users u
        LEFT JOIN weekly_results wr ON u.id = wr.user_id AND wr.year = 2025
        GROUP BY u.id, u.username
        HAVING season_correct > 0
        ORDER BY season_points DESC, season_correct DESC
    """)
    
    leaderboard = cursor.fetchall()
    print(f"\nSEASON LEADERBOARD:")
    print(f"{'Rank':<4} {'User':<12} {'Points':<7} {'Correct':<8} {'Wins':<5}")
    print("-" * 40)
    
    for i, (username, points, correct, wins) in enumerate(leaderboard, 1):
        highlight = " <-- RAYMOND" if username == "raymond" else ""
        print(f"{i:<4} {username:<12} {points:<7} {correct:<8} {wins:<5}{highlight}")
    
    # Check Raymond specifically
    cursor.execute("""
        SELECT week, total_points, correct_picks, weekly_rank, is_winner
        FROM weekly_results 
        WHERE user_id = 17 AND year = 2025
        ORDER BY week
    """)
    
    raymond_weeks = cursor.fetchall()
    print(f"\nRaymond's weekly performance:")
    for week, points, correct, rank, is_winner in raymond_weeks:
        win_status = " (WON!)" if is_winner else ""
        print(f"  Week {week}: {correct} correct, {points} points, Rank #{rank}{win_status}")
    
    # Summary
    total_points = sum(row[1] for row in raymond_weeks if row[1])
    total_correct = sum(row[2] for row in raymond_weeks if row[2])
    wins = sum(1 for row in raymond_weeks if row[4])
    
    print(f"\nRaymond's season summary:")
    print(f"  Total Points: {total_points}")
    print(f"  Total Correct Picks: {total_correct}")
    print(f"  Weeks Won: {wins}")
    
    raymond_rank = next((i for i, (username, _, _, _) in enumerate(leaderboard, 1) if username == "raymond"), None)
    if raymond_rank:
        print(f"  Season Rank: #{raymond_rank} out of {len(leaderboard)}")
    else:
        print(f"  Raymond not found in leaderboard!")
    
    conn.close()

if __name__ == "__main__":
    main()