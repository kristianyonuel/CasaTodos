#!/usr/bin/env python3
"""
Complete scoring for all Week 9 picks to resolve leaderboard display
The web app might be waiting for ALL picks to be scored before showing results
"""

import sqlite3

def complete_week9_scoring():
    """Complete scoring for all remaining Week 9 picks"""
    
    print("🎯 COMPLETING WEEK 9 SCORING")
    print("=" * 40)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check unscored picks
    cursor.execute("""
        SELECT COUNT(*) as unscored
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND up.is_correct IS NULL
    """)
    
    unscored = cursor.fetchone()[0]
    print(f"📊 Unscored picks: {unscored}")
    
    if unscored == 0:
        print("✅ All picks already scored!")
        return
    
    # Get all finalized games that need scoring
    cursor.execute("""
        SELECT DISTINCT g.game_id, g.away_team, g.home_team, g.away_score, g.home_score
        FROM nfl_games g
        JOIN user_picks up ON g.game_id = up.game_id
        WHERE g.week = 9 AND g.is_final = 1 AND up.is_correct IS NULL
    """)
    
    games_to_score = cursor.fetchall()
    print(f"🏈 Games needing pick scoring: {len(games_to_score)}")
    
    total_picks_scored = 0
    
    for game_id, away_team, home_team, away_score, home_score in games_to_score:
        print(f"\n🎮 Scoring: {away_team} @ {home_team} ({away_score}-{home_score})")
        
        # Determine winner
        if home_score > away_score:
            winner = home_team
        elif away_score > home_score:
            winner = away_team
        else:
            winner = None  # Tie
        
        if winner:
            # Update all picks for this game
            cursor.execute("""
                UPDATE user_picks
                SET is_correct = CASE 
                    WHEN selected_team = ? THEN 1 
                    ELSE 0 
                END,
                points_earned = CASE 
                    WHEN selected_team = ? THEN 1 
                    ELSE 0 
                END
                WHERE game_id = ? AND is_correct IS NULL
            """, (winner, winner, game_id))
            
            picks_updated = cursor.rowcount
            total_picks_scored += picks_updated
            print(f"   ✅ Winner: {winner} | Picks scored: {picks_updated}")
        else:
            # Handle tie - mark all as incorrect (no points)
            cursor.execute("""
                UPDATE user_picks
                SET is_correct = 0, points_earned = 0
                WHERE game_id = ? AND is_correct IS NULL
            """, (game_id,))
            
            picks_updated = cursor.rowcount
            total_picks_scored += picks_updated
            print(f"   🤝 Tie game | Picks scored: {picks_updated}")
    
    conn.commit()
    print(f"\n✅ Total picks scored: {total_picks_scored}")
    
    # Verify all picks are now scored
    cursor.execute("""
        SELECT COUNT(*) as unscored
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND up.is_correct IS NULL
    """)
    
    remaining_unscored = cursor.fetchone()[0]
    print(f"📊 Remaining unscored picks: {remaining_unscored}")
    
    if remaining_unscored == 0:
        print("🎉 ALL WEEK 9 PICKS NOW SCORED!")
        
        # Show final leaderboard
        cursor.execute("""
            SELECT u.username, 
                   COUNT(up.id) as total_picks,
                   SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                   SUM(up.points_earned) as points
            FROM users u
            JOIN user_picks up ON u.id = up.user_id
            JOIN nfl_games g ON up.game_id = g.game_id
            WHERE g.week = 9
            GROUP BY u.username
            ORDER BY points DESC, correct DESC
        """)
        
        leaderboard = cursor.fetchall()
        print(f"\n🏆 FINAL WEEK 9 LEADERBOARD:")
        for rank, (username, total, correct, points) in enumerate(leaderboard, 1):
            print(f"   {rank}. {username}: {correct}/{total} correct ({points} pts)")
        
        print(f"\n💡 SOLUTION:")
        print("Now that ALL picks are scored, try refreshing the web page.")
        print("The leaderboard should now display correctly!")
    
    conn.close()

if __name__ == "__main__":
    complete_week9_scoring()