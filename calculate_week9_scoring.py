#!/usr/bin/env python3
"""
Check Week 9 game results and calculate correct picks for all users
"""

import sqlite3

def check_week9_game_results():
    """Check the actual Week 9 game results and scoring"""
    print("=" * 70)
    print("CHECKING WEEK 9 GAME RESULTS AND SCORING")
    print("=" * 70)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check Week 9 game results
    print("\n1. Week 9 Game Results:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT 
            id,
            away_team,
            home_team,
            away_score,
            home_score,
            is_final,
            game_status
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    
    games = cursor.fetchall()
    final_games = 0
    
    for game in games:
        if game['is_final'] and game['away_score'] is not None and game['home_score'] is not None:
            away_score = game['away_score']
            home_score = game['home_score']
            winner = game['home_team'] if home_score > away_score else game['away_team']
            final_games += 1
            
            print(f"Game {game['id']}: {game['away_team']} {away_score} - {home_score} {game['home_team']}")
            print(f"    Winner: {winner}")
        else:
            print(f"Game {game['id']}: {game['away_team']} @ {game['home_team']}")
            print(f"    Status: {game['game_status']} (No final score)")
        print()
    
    print(f"Final games with scores: {final_games}/14")
    
    # Check current scoring status
    print("\n2. Current Pick Scoring Status:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT 
            u.username,
            COUNT(up.id) as total_picks,
            SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
            SUM(CASE WHEN up.is_correct = 0 THEN 1 ELSE 0 END) as wrong_picks
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.id
        WHERE g.week = 9 AND g.year = 2025 AND NOT u.is_admin
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, u.username
    """)
    
    scoring_status = cursor.fetchall()
    
    for user in scoring_status:
        win_pct = (user['correct_picks'] / user['total_picks'] * 100) if user['total_picks'] > 0 else 0
        print(f"{user['username']:12}: {user['correct_picks']:2}/{user['total_picks']:2} correct ({win_pct:5.1f}%)")
    
    # Check if scoring needs to be calculated
    print("\n3. Sample Pick Analysis:")
    print("-" * 50)
    
    # Look at a specific game and user picks
    cursor.execute("""
        SELECT 
            g.id,
            g.away_team,
            g.home_team,
            g.away_score,
            g.home_score,
            g.is_final,
            COUNT(up.id) as total_user_picks,
            SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_count
        FROM nfl_games g
        LEFT JOIN user_picks up ON g.id = up.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY g.id
        ORDER BY g.game_date
        LIMIT 3
    """)
    
    sample_games = cursor.fetchall()
    
    for game in sample_games:
        print(f"Game {game['id']}: {game['away_team']} vs {game['home_team']}")
        if game['is_final']:
            print(f"  Final Score: {game['away_score']}-{game['home_score']}")
        print(f"  User picks for this game: {game['total_user_picks']}")
        print(f"  Marked as correct: {game['correct_count']}")
        print()
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS")
    print("=" * 50)
    print("The issue is likely that:")
    print("1. Game results exist in database")
    print("2. User picks exist in database") 
    print("3. BUT the scoring calculation hasn't been run")
    print("4. All is_correct fields are still 0 (default)")
    print("\nNext step: Run scoring calculation to update is_correct based on game results")

def calculate_week9_scoring():
    """Calculate Week 9 scoring for all users"""
    print("\n" + "=" * 70)
    print("CALCULATING WEEK 9 SCORING FOR ALL USERS")
    print("=" * 70)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all final games with results
    cursor.execute("""
        SELECT 
            id,
            away_team,
            home_team,
            away_score,
            home_score
        FROM nfl_games 
        WHERE week = 9 AND year = 2025 AND is_final = 1 
        AND away_score IS NOT NULL AND home_score IS NOT NULL
        ORDER BY game_date
    """)
    
    final_games = cursor.fetchall()
    print(f"\nFound {len(final_games)} games with final scores")
    
    total_picks_updated = 0
    
    for game in final_games:
        game_id = game[0]
        away_team = game[1] 
        home_team = game[2]
        away_score = game[3]
        home_score = game[4]
        
        # Determine winner
        if away_score > home_score:
            winning_team = away_team
        elif home_score > away_score:
            winning_team = home_team
        else:
            winning_team = None  # Tie
        
        print(f"\nGame {game_id}: {away_team} {away_score} - {home_score} {home_team}")
        print(f"Winner: {winning_team}")
        
        if winning_team:
            # Update all picks for this game
            cursor.execute("""
                UPDATE user_picks 
                SET is_correct = (CASE WHEN selected_team = ? THEN 1 ELSE 0 END),
                    points_earned = (CASE WHEN selected_team = ? THEN 1 ELSE 0 END)
                WHERE game_id = ?
            """, (winning_team, winning_team, game_id))
            
            picks_updated = cursor.rowcount
            total_picks_updated += picks_updated
            print(f"Updated {picks_updated} user picks for this game")
            
            # Show some sample picks for this game
            cursor.execute("""
                SELECT u.username, up.selected_team, up.is_correct
                FROM user_picks up
                JOIN users u ON up.user_id = u.id
                WHERE up.game_id = ? AND NOT u.is_admin
                ORDER BY u.username
                LIMIT 5
            """, (game_id,))
            
            sample_picks = cursor.fetchall()
            for pick in sample_picks:
                status = "✅ Correct" if pick[2] else "❌ Wrong"
                print(f"  {pick[0]:10}: {pick[1]:20} - {status}")
        else:
            print("  Tie game - no points awarded")
    
    # Commit changes
    conn.commit()
    
    # Show updated leaderboard
    print(f"\n" + "=" * 50)
    print("UPDATED WEEK 9 LEADERBOARD")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            u.username,
            SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
            SUM(CASE WHEN up.is_correct = 0 THEN 1 ELSE 0 END) as wrong_picks,
            COUNT(up.id) as total_picks
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.id
        WHERE g.week = 9 AND g.year = 2025 AND NOT u.is_admin
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, wrong_picks ASC, u.username
    """)
    
    leaderboard = cursor.fetchall()
    
    rank = 1
    for user in leaderboard:
        win_pct = (user[1] / user[3] * 100) if user[3] > 0 else 0
        print(f"{rank:2}. {user[0]:12}: {user[1]:2}/{user[3]:2} correct ({win_pct:5.1f}%)")
        rank += 1
    
    conn.close()
    
    print(f"\n✅ Updated {total_picks_updated} picks total")
    print("🎯 Week 9 scoring calculation complete!")

if __name__ == "__main__":
    check_week9_game_results()
    calculate_week9_scoring()