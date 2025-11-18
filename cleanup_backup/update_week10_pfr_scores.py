#!/usr/bin/env python3
"""
Week 10 Score Update - Manual Entry with Pro Football Reference Data

Based on PFR Week 10 data, manually update the specific games that need scores.
"""

import sqlite3
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_week10_scores_manual():
    """Manually update Week 10 with specific scores from PFR data"""
    
    print("🏈 WEEK 10 MANUAL SCORE UPDATE FROM PFR DATA")
    print("=" * 60)
    
    # Week 10 scores extracted from Pro Football Reference
    week10_scores = [
        # (away_team, away_score, home_team, home_score)
        ('LV', 7, 'DEN', 10),      # Las Vegas Raiders @ Denver Broncos
        ('ATL', 25, 'IND', 31),     # Atlanta Falcons @ Indianapolis Colts  
        ('DET', 44, 'WAS', 22),     # Detroit Lions @ Washington Commanders
        ('NO', 17, 'CAR', 7),       # New Orleans Saints @ Carolina Panthers
        ('LAR', 42, 'SF', 26),      # Los Angeles Rams @ San Francisco 49ers
        ('HOU', 36, 'JAX', 29),     # Houston Texans vs Jacksonville Jaguars
        ('ARI', 22, 'SEA', 44),     # Arizona Cardinals @ Seattle Seahawks
        ('MIN', 19, 'BAL', 27),     # Minnesota Vikings vs Baltimore Ravens
        ('TB', 23, 'NE', 28),       # Tampa Bay Buccaneers @ New England Patriots
        ('NYJ', 27, 'CLE', 20),     # New York Jets vs Cleveland Browns
        ('PIT', 10, 'LAC', 25),     # Pittsburgh Steelers @ Los Angeles Chargers
        ('CHI', 24, 'NYG', 20),     # Chicago Bears vs New York Giants
        ('MIA', 30, 'BUF', 13),     # Miami Dolphins vs Buffalo Bills
    ]
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # First, show current Week 10 status
        cursor.execute("""
            SELECT away_team, home_team, away_score, home_score, is_final 
            FROM nfl_games 
            WHERE week = 10 AND year = 2025
            ORDER BY id
        """)
        
        current_games = cursor.fetchall()
        
        print("\n📊 Current Week 10 Game Status:")
        print("   Away Team | Home Team | Away Score | Home Score | Final")
        print("   " + "-" * 60)
        
        for away, home, away_score, home_score, is_final in current_games:
            final_status = "✅" if is_final else "❌"
            away_score_str = str(away_score) if away_score is not None else "None"
            home_score_str = str(home_score) if home_score is not None else "None"
            print(f"   {away:<8} | {home:<8} | {away_score_str:>10} | {home_score_str:>10} | {final_status}")
        
        # Update games with PFR scores
        print(f"\n🔄 Updating {len(week10_scores)} games with PFR scores...")
        
        updated = 0
        for away_team, away_score, home_team, home_score in week10_scores:
            # Find the game
            cursor.execute("""
                SELECT id FROM nfl_games 
                WHERE week = 10 AND year = 2025 
                AND away_team = ? AND home_team = ?
            """, (away_team, home_team))
            
            game = cursor.fetchone()
            
            if game:
                game_id = game[0]
                
                # Update the score
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
                    logger.info(f"   ✅ Updated: {away_team} {away_score} - {home_team} {home_score}")
                else:
                    logger.warning(f"   ⚠️ No update: {away_team} @ {home_team}")
            else:
                logger.warning(f"   ❌ Game not found: {away_team} @ {home_team}")
        
        conn.commit()
        
        # Show updated status
        print(f"\n📊 Week 10 Update Complete: {updated} games updated")
        
        # Show fantasy results if any games were updated
        if updated > 0:
            print("\n🏆 Week 10 Fantasy Leaderboard:")
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
                ORDER BY correct DESC, percentage DESC
            """)
            
            results = cursor.fetchall()
            
            if results:
                print("   Username          | Correct | Total | Percentage")
                print("   " + "-" * 50)
                for username, correct, total, percentage in results:
                    print(f"   {username:<16} | {correct:>7} | {total:>5} | {percentage:>8}%")
            else:
                print("   No fantasy picks found for completed Week 10 games")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error updating Week 10 scores: {e}")

def main():
    update_week10_scores_manual()

if __name__ == "__main__":
    main()