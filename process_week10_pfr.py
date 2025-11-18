#!/usr/bin/env python3
"""
Process Week 10 PFR Data - Extract and Update Scores

From the PFR data fetched, extract the following Week 10 scores:
- Las Vegas Raiders 7, Denver Broncos 10 (Final)
- Atlanta Falcons 25, Indianapolis Colts (25?)
- Detroit Lions 44, Washington Commanders 22 (Final)
- New Orleans Saints 17, Carolina Panthers 7 (Final)
- Los Angeles Rams 42, San Francisco 49ers 26 (Final)
- Houston Texans 36, Jacksonville Jaguars 29 (Final)
- Arizona Cardinals 22, Seattle Seahawks 44 (Final)
- Minnesota Vikings 19, Baltimore Ravens 27 (Final)  
- Tampa Bay Buccaneers 23, New England Patriots 28 (Final)
- New York Jets 27, Cleveland Browns 20 (Final)
- Los Angeles Chargers 25, Pittsburgh Steelers 10 (Final)
- Chicago Bears 24, New York Giants 20 (Final)
- Indianapolis Colts 31, Atlanta Falcons 25 (Final)
- Miami Dolphins 30, Buffalo Bills 13 (Final)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vscode_pfr_integration import VSCodePFRIntegration

def process_week10_scores():
    """Process Week 10 scores from PFR data"""
    
    print("🏈 PROCESSING WEEK 10 PFR SCORES")
    print("=" * 50)
    
    # Initialize the system
    system = VSCodePFRIntegration()
    
    # Extracted scores from PFR data
    week10_content = """
    Las Vegas Raiders 7, Denver Broncos 10 Final
    Atlanta Falcons 25, Indianapolis Colts 31 Final
    Detroit Lions 44, Washington Commanders 22 Final
    New Orleans Saints 17, Carolina Panthers 7 Final
    Los Angeles Rams 42, San Francisco 49ers 26 Final
    Houston Texans 36, Jacksonville Jaguars 29 Final
    Arizona Cardinals 22, Seattle Seahawks 44 Final
    Minnesota Vikings 19, Baltimore Ravens 27 Final
    Tampa Bay Buccaneers 23, New England Patriots 28 Final
    New York Jets 27, Cleveland Browns 20 Final
    Los Angeles Chargers 25, Pittsburgh Steelers 10 Final
    Chicago Bears 24, New York Giants 20 Final
    Miami Dolphins 30, Buffalo Bills 13 Final
    Indianapolis Colts 31, Atlanta Falcons 25 Final
    """
    
    # Process the content for Week 10
    updated = system.process_pfr_content_for_week(10, week10_content)
    
    print(f"\n📊 WEEK 10 UPDATE COMPLETE")
    print(f"✅ Updated {updated} games from Pro Football Reference data")
    
    if updated > 0:
        # Show updated leaderboard 
        import sqlite3
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            print("\n📊 Updated Week 10 Fantasy Leaderboard:")
            cursor.execute("""
                SELECT users.username, 
                       COUNT(CASE WHEN user_picks.is_correct = 1 THEN 1 END) as correct,
                       COUNT(*) as total,
                       ROUND(COUNT(CASE WHEN user_picks.is_correct = 1 THEN 1 END) * 100.0 / COUNT(*), 1) as percentage
                FROM users 
                JOIN user_picks ON users.id = user_picks.user_id 
                JOIN nfl_games ON user_picks.game_id = nfl_games.id 
                WHERE nfl_games.week = 10 AND nfl_games.year = 2025 AND nfl_games.is_final = 1
                GROUP BY users.id, users.username 
                ORDER BY correct DESC, percentage DESC
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            
            if results:
                print("\n   Username          | Correct | Total | Percentage")
                print("   " + "-" * 50)
                for username, correct, total, percentage in results:
                    print(f"   {username:<16} | {correct:>7} | {total:>5} | {percentage:>8}%")
            else:
                print("   No fantasy results found for Week 10")
                
            conn.close()
            
        except Exception as e:
            print(f"❌ Error showing leaderboard: {e}")

def main():
    process_week10_scores()

if __name__ == "__main__":
    main()