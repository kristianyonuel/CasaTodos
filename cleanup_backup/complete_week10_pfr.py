#!/usr/bin/env python3
"""
Update Remaining Week 10 Games

Update the 5 games that still need scores based on PFR data:
- New York Giants @ Chicago Bears 
- New Orleans Saints @ Carolina Panthers
- Cleveland Browns @ New York Jets
- Baltimore Ravens @ Minnesota Vikings  
- Philadelphia Eagles @ Green Bay Packers
"""

import sqlite3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def update_remaining_week10():
    """Update the 5 remaining Week 10 games with PFR scores"""
    
    print("🏈 UPDATING REMAINING WEEK 10 GAMES")
    print("=" * 50)
    
    # Remaining games from PFR data (exact database format)
    remaining_scores = [
        ('New York Giants', 20, 'Chicago Bears', 24),        # CHI 24, NYG 20
        ('New Orleans Saints', 17, 'Carolina Panthers', 7),   # NO 17, CAR 7  
        ('Cleveland Browns', 20, 'New York Jets', 27),       # NYJ 27, CLE 20
        ('Baltimore Ravens', 27, 'Minnesota Vikings', 19),    # BAL 27, MIN 19
        ('Philadelphia Eagles', None, 'Green Bay Packers', None)  # Not in PFR data yet
    ]
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        print("\n🔄 Updating remaining games...")
        
        updated = 0
        for away_team, away_score, home_team, home_score in remaining_scores:
            if away_score is None or home_score is None:
                print(f"   ⏳ Skipping: {away_team} @ {home_team} (no PFR data yet)")
                continue
                
            # Find and update the game
            cursor.execute("""
                SELECT id FROM nfl_games 
                WHERE week = 10 AND year = 2025 
                AND away_team = ? AND home_team = ?
            """, (away_team, home_team))
            
            game = cursor.fetchone()
            
            if game:
                game_id = game[0]
                
                cursor.execute("""
                    UPDATE nfl_games SET 
                        away_score = ?,
                        home_score = ?,
                        is_final = 1,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (away_score, home_score, game_id))
                
                if cursor.rowcount > 0:
                    updated += 1
                    print(f"   ✅ Updated: {away_team} {away_score} - {home_team} {home_score}")
            else:
                print(f"   ❌ Game not found: {away_team} @ {home_team}")
        
        conn.commit()
        
        print(f"\n📊 Update Complete: {updated} games updated")
        
        # Show final Week 10 status
        cursor.execute("""
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games
            FROM nfl_games 
            WHERE week = 10 AND year = 2025
        """)
        
        total, final = cursor.fetchone()
        
        print(f"📊 Week 10 Final Status: {final}/{total} games complete")
        
        if final > 10:  # Show leaderboard if most games are done
            print("\n🏆 Week 10 Current Fantasy Leaderboard:")
            cursor.execute("""
                SELECT 
                    users.username,
                    COUNT(CASE WHEN user_picks.is_correct = 1 THEN 1 END) as correct,
                    COUNT(*) as total,
                    ROUND(COUNT(CASE WHEN user_picks.is_correct = 1 THEN 1 END) * 100.0 / COUNT(*), 1) as percentage
                FROM users 
                JOIN user_picks ON users.id = user_picks.user_id 
                JOIN nfl_games ON user_picks.game_id = nfl_games.id 
                WHERE nfl_games.week = 10 AND nfl_games.year = 2025 AND nfl_games.is_final = 1
                GROUP BY users.id, users.username 
                HAVING total > 0
                ORDER BY correct DESC, percentage DESC
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            
            if results:
                print("   Username          | Correct | Total | Percentage")
                print("   " + "-" * 50)
                for username, correct, total, percentage in results:
                    print(f"   {username:<16} | {correct:>7} | {total:>5} | {percentage:>8}%")
            else:
                print("   No fantasy picks found for Week 10")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error updating Week 10: {e}")

def main():
    update_remaining_week10()

if __name__ == "__main__":
    main()