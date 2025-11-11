#!/usr/bin/env python3

import sqlite3
from datetime import datetime
import logging

class WeeklyWinnerManager:
    """Automatically determines and saves weekly winners when a week completes"""
    
    def __init__(self, db_path='nfl_fantasy.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def check_week_completion(self, week, year=2025):
        """Check if a week is complete (all games are final)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_games,
                   SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games
            FROM nfl_games 
            WHERE week = ? AND year = ?
        ''', (week, year))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            total_games, final_games = result
            return total_games > 0 and total_games == final_games
        return False
    
    def is_weekly_results_saved(self, week, year=2025):
        """Check if weekly results are already saved for this week"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM weekly_results 
            WHERE week = ? AND year = ?
        ''', (week, year))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_week_standings(self, week, year=2025):
        """Get week standings with all user results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, 
                   COUNT(*) as total_picks,
                   SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
            FROM user_picks up
            JOIN nfl_games ng ON up.game_id = ng.game_id
            JOIN users u ON up.user_id = u.id
            WHERE ng.week = ? AND ng.year = ?
            GROUP BY u.id, u.username
            ORDER BY correct_picks DESC, u.username
        ''', (week, year))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_monday_night_info(self, user_id, week, year=2025):
        """Get Monday Night Football pick and result for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ng.home_team, ng.away_team, ng.home_score, ng.away_score,
                   up.selected_team, up.predicted_home_score, up.predicted_away_score
            FROM user_picks up
            JOIN nfl_games ng ON up.game_id = ng.game_id
            WHERE up.user_id = ? AND ng.week = ? AND ng.year = ? 
              AND ng.is_monday_night = 1
        ''', (user_id, week, year))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            home_team, away_team, home_score, away_score, selected_team, pred_home, pred_away = result
            
            # Determine actual winner
            if home_score > away_score:
                actual_winner = home_team
            else:
                actual_winner = away_team
            
            # Check if pick was correct
            pick_correct = selected_team == actual_winner
            
            return {
                'game': f"{away_team} {away_score} - {home_team} {home_score}",
                'pick': selected_team,
                'pick_correct': pick_correct,
                'prediction': f"{pred_away} - {pred_home}" if pred_away and pred_home else "No prediction",
                'actual_score': f"{away_score} - {home_score}"
            }
        
        return None
    
    def save_weekly_results(self, week, year=2025):
        """Save weekly results to weekly_results table"""
        standings = self.get_week_standings(week, year)
        
        if not standings:
            self.logger.warning(f"No standings found for Week {week}, {year}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete existing records for this week (in case of re-calculation)
        cursor.execute('DELETE FROM weekly_results WHERE week = ? AND year = ?', (week, year))
        
        # Determine rankings and winners
        current_rank = 1
        prev_score = None
        winner_found = False
        saved_count = 0
        
        self.logger.info(f"📊 Saving Week {week} Results:")
        
        for i, (user_id, username, total_picks, correct_picks) in enumerate(standings):
            # Handle ties in ranking
            if prev_score is not None and correct_picks < prev_score:
                current_rank = i + 1
            
            # Winner is anyone with the highest score (handles ties)
            is_winner = (not winner_found and (prev_score is None or correct_picks == standings[0][3]))
            
            # Insert into weekly_results
            cursor.execute('''
                INSERT INTO weekly_results (
                    user_id, week, year, correct_picks, total_picks,
                    is_winner, weekly_rank, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, week, year, correct_picks, total_picks, 
                  is_winner, current_rank, datetime.now()))
            
            winner_emoji = "🏆" if is_winner else ""
            self.logger.info(f"  {current_rank:2d}. {username:12s}: {correct_picks:2d}/{total_picks:2d} {winner_emoji}")
            
            # If this is the winner, get Monday Night info
            if is_winner and not winner_found:
                mnf_info = self.get_monday_night_info(user_id, week, year)
                if mnf_info:
                    self.logger.info(f"     Monday Night Pick: {mnf_info['pick']}")
                    self.logger.info(f"     Game Result: {mnf_info['game']}")
                    self.logger.info(f"     Pick Result: {'✅ CORRECT' if mnf_info['pick_correct'] else '❌ WRONG'}")
                    if mnf_info['prediction'] != "No prediction":
                        self.logger.info(f"     Score Prediction: {mnf_info['prediction']} (Actual: {mnf_info['actual_score']})")
                
                winner_found = True
            
            prev_score = correct_picks
            saved_count += 1
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"✅ Week {week} results saved: {saved_count} records")
        return True
    
    def process_completed_weeks(self, start_week=1, end_week=18, year=2025):
        """Process all completed weeks that haven't been saved yet"""
        processed = []
        
        for week in range(start_week, end_week + 1):
            # Check if week is complete
            if not self.check_week_completion(week, year):
                continue
            
            # Check if already saved
            if self.is_weekly_results_saved(week, year):
                self.logger.info(f"Week {week} already processed, skipping")
                continue
            
            # Save weekly results
            self.logger.info(f"🏆 Processing completed Week {week}...")
            if self.save_weekly_results(week, year):
                processed.append(week)
        
        return processed

def main():
    """Main function to check and process completed weeks"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    manager = WeeklyWinnerManager()
    
    print("🏈 AUTOMATIC WEEKLY WINNER PROCESSOR")
    print("=" * 50)
    
    # Process all completed weeks
    processed = manager.process_completed_weeks()
    
    if processed:
        print(f"\n✅ Processed weeks: {processed}")
    else:
        print("\n✅ No new weeks to process")

if __name__ == "__main__":
    main()