"""
Fix Week 7 scoring and determine correct winners
"""
import sqlite3
import sys
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Import the scoring function
sys.path.append(os.getcwd())
from nfl_week_scorer import score_specific_week

def check_week7_winners():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== WEEK 7 WINNER ANALYSIS ===")
    
    # Get actual Week 7 game count
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 7 AND year = 2025")
    total_games = cursor.fetchone()[0]
    print(f"Week 7 has {total_games} games")
    
    # Check each user's Week 7 performance correctly
    cursor.execute("""
        SELECT 
            u.username,
            u.id,
            COUNT(up.game_id) as picks_made,
            SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
            SUM(CASE WHEN up.is_correct = 0 THEN 1 ELSE 0 END) as wrong_picks
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games g ON up.game_id = g.id AND g.week = 7 AND g.year = 2025
        WHERE u.id > 1
        GROUP BY u.id, u.username
        HAVING picks_made > 0
        ORDER BY correct_picks DESC, wrong_picks ASC
    """)
    
    results = cursor.fetchall()
    print(f"\nACTUAL WEEK 7 PERFORMANCE:")
    print(f"Rank  User          Picks  Correct  Wrong")
    print("-" * 40)
    
    for i, (username, user_id, picks, correct, wrong) in enumerate(results, 1):
        highlight = ""
        if username in ["raymond", "robert"]:
            highlight = " <-- Potential winners?"
        elif username == "ramfis":
            highlight = " <-- Ramfis (3 losses like Kristian?)"
        elif username == "kristian": 
            highlight = " <-- Kristian (3 losses?)"
        
        print(f"{i:2d}.   {username:12} {picks:3d}    {correct:3d}     {wrong:3d}{highlight}")
    
    # Score Week 7 properly
    print(f"\nRunning Week 7 scoring system...")
    try:
        # Suppress output to avoid encoding issues
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            score_specific_week(7, 2025)
        
        print("Week 7 scored successfully")
        
        # Check the results
        cursor.execute("""
            SELECT 
                u.username,
                wr.correct_picks,
                wr.total_points,
                wr.weekly_rank,
                wr.is_winner
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.week = 7 AND wr.year = 2025
            ORDER BY wr.weekly_rank
        """)
        
        scored_results = cursor.fetchall()
        if scored_results:
            print(f"\nWEEK 7 OFFICIAL RESULTS:")
            print(f"Rank  User          Correct  Points  Winner")
            print("-" * 40)
            
            winners = []
            for username, correct, points, rank, is_winner in scored_results:
                winner_status = "YES" if is_winner else "NO"
                if is_winner:
                    winners.append(username)
                
                highlight = ""
                if username in ["raymond", "robert"]:
                    highlight = " <-- Should be winners?"
                elif username == "ramfis":
                    highlight = " <-- Ramfis"
                
                print(f"{rank:2d}.   {username:12} {correct:3d}     {points:3d}     {winner_status}{highlight}")
            
            print(f"\nCurrent winners: {winners}")
            
            # Check if Raymond or Robert should be winning instead
            if results:
                max_correct = max(row[3] for row in results)  # Max correct from actual data
                actual_leaders = [row[0] for row in results if row[3] == max_correct]
                
                print(f"Based on performance analysis:")
                print(f"  Max correct picks: {max_correct}")
                print(f"  Should be winning: {actual_leaders}")
                
                if set(actual_leaders) != set(winners):
                    print(f"  MISMATCH! Current winners: {winners}")
                    print(f"  Should be winners: {actual_leaders}")
                    
                    # Check for tiebreaker situation
                    if len(actual_leaders) > 1:
                        print(f"\nTIEBREAKER NEEDED for: {actual_leaders}")
                        
                        # Run tiebreaker analysis
                        cursor.execute("""
                            SELECT u.username, up.tiebreaker_total
                            FROM users u
                            JOIN user_picks up ON u.id = up.user_id
                            JOIN nfl_games g ON up.game_id = g.id
                            WHERE g.week = 7 AND g.year = 2025 AND g.is_monday_night = 1
                            AND u.username IN ({})
                            AND up.tiebreaker_total IS NOT NULL
                        """.format(','.join(['?' for _ in actual_leaders])), actual_leaders)
                        
                        tiebreakers = cursor.fetchall()
                        if tiebreakers:
                            print("Tiebreaker predictions:")
                            for user, prediction in tiebreakers:
                                print(f"  {user}: {prediction}")
        
    except Exception as e:
        print(f"Error scoring Week 7: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_week7_winners()