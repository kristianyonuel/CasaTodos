#!/usr/bin/env python3
"""
Display all Week 9 picks for all users in a clear format
"""

import sqlite3

def show_week9_picks():
    """Display all Week 9 picks for all users"""
    
    print("🏈 WEEK 9 PICKS FOR ALL USERS")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all Week 9 games in order
    cursor.execute("""
        SELECT game_id, away_team, home_team, away_score, home_score
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_id
    """)
    
    games = cursor.fetchall()
    
    # Get all users
    cursor.execute("SELECT username FROM users ORDER BY username")
    users = [row[0].upper() for row in cursor.fetchall()]
    
    print(f"📊 {len(games)} games, {len(users)} users")
    print()
    
    # Display picks for each game
    for i, (game_id, away, home, away_score, home_score) in enumerate(games, 1):
        winner = away if away_score > home_score else home
        print(f"🏈 GAME {i}: {away} {away_score} - {home_score} {home}")
        print(f"   Winner: {winner}")
        print("   Picks:", end=" ")
        
        # Get picks for this game
        cursor.execute("""
            SELECT u.username, up.selected_team, up.is_correct
            FROM user_picks up
            JOIN users u ON up.user_id = u.id
            WHERE up.game_id = ?
            ORDER BY u.username
        """, (game_id,))
        
        picks = cursor.fetchall()
        
        for username, pick, is_correct in picks:
            status = "✅" if is_correct else "❌"
            team_short = pick.split()[-1] if pick else "None"
            print(f"{username.upper()}={team_short}{status}", end=" ")
        
        print()  # New line after each game
        print()
    
    # Show overall results
    print("📈 OVERALL WEEK 9 RESULTS:")
    cursor.execute("""
        SELECT u.username, 
               SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
               COUNT(*) as total,
               SUM(up.points_earned) as points
        FROM users u
        JOIN user_picks up ON u.id = up.user_id
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.year = 2025
        GROUP BY u.username
        ORDER BY points DESC, correct DESC
    """)
    
    results = cursor.fetchall()
    
    for rank, (username, correct, total, points) in enumerate(results, 1):
        print(f"   {rank}. {username.upper()}: {correct}/{total} correct ({points} points)")
    
    conn.close()

if __name__ == "__main__":
    show_week9_picks()