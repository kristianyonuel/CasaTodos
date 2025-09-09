"""
Scoring Updater Module
Automatically updates weekly results when games are finalized
"""

import sqlite3
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ScoringUpdater:
    """Handles automatic scoring updates when games are finalized"""
    
    def __init__(self, db_path: str = 'nfl_fantasy.db'):
        self.db_path = db_path
    
    def get_week_winners(self, week: int, year: int) -> List[Dict[str, Any]]:
        """
        Calculate weekly winners using simplified scoring (1 point per correct pick)
        Returns list of user results with Monday Night tiebreaker data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get users who made picks for this week with their scores
            cursor.execute('''
                SELECT u.id as user_id, u.username,
                       COUNT(p.id) as total_picks,
                       SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
                FROM users u
                JOIN user_picks p ON u.id = p.user_id
                JOIN nfl_games g ON p.game_id = g.id
                WHERE g.week = ? AND g.year = ? AND g.is_final = 1 AND u.is_admin = 0
                GROUP BY u.id, u.username
                HAVING total_picks > 0
                ORDER BY correct_picks DESC
            ''', (week, year))
            
            user_results = cursor.fetchall()
            
            if not user_results:
                conn.close()
                return []
            
            # Get Monday Night data for tiebreakers
            results = []
            for user_row in user_results:
                user_id = user_row['user_id']
                username = user_row['username']
                total_picks = user_row['total_picks']
                correct_picks = user_row['correct_picks']
                
                # Get Monday Night pick data for this user
                cursor.execute('''
                    SELECT p.predicted_home_score, p.predicted_away_score, p.selected_team,
                           g.home_score, g.away_score, p.created_at
                    FROM user_picks p
                    JOIN nfl_games g ON p.game_id = g.id
                    WHERE p.user_id = ? AND g.week = ? AND g.year = ? 
                      AND g.is_monday_night = 1 AND g.is_final = 1
                    LIMIT 1
                ''', (user_id, week, year))
                
                monday_pick = cursor.fetchone()
                
                # Calculate Monday Night tiebreaker data
                monday_tiebreaker = {
                    'correct_winner': False,
                    'home_diff': 999,
                    'away_diff': 999,
                    'total_diff': 999,
                    'submission_time': '9999-12-31 23:59:59'
                }
                
                if monday_pick:
                    pred_home = monday_pick['predicted_home_score'] or 0
                    pred_away = monday_pick['predicted_away_score'] or 0
                    actual_home = monday_pick['home_score'] or 0
                    actual_away = monday_pick['away_score'] or 0
                    
                    # Check if user predicted correct winner based on selected_team field
                    selected_team = monday_pick['selected_team']
                    actual_winner = 'MIN' if actual_away > actual_home else 'CHI'  # MIN is away, CHI is home
                    correct_winner = selected_team == actual_winner
                    
                    monday_tiebreaker = {
                        'correct_winner': correct_winner,
                        'home_diff': abs(pred_home - actual_home),
                        'away_diff': abs(pred_away - actual_away),
                        'total_diff': abs((pred_home + pred_away) - (actual_home + actual_away)),
                        'submission_time': monday_pick['created_at'] or '9999-12-31 23:59:59'
                    }
                
                results.append({
                    'user_id': user_id,
                    'username': username,
                    'total_picks': total_picks,
                    'correct_picks': correct_picks,
                    'monday_tiebreaker': monday_tiebreaker
                })
            
            conn.close()
            
            # Sort with Monday Night tiebreaker logic
            results.sort(key=lambda x: (
                -x['correct_picks'],                                    # Most games won (1 point each)
                not x['monday_tiebreaker'].get('correct_winner', False), # Correct winner first (False sorts before True)
                x['monday_tiebreaker']['home_diff'],                    # Closest to home team score
                x['monday_tiebreaker']['away_diff'],                    # Closest to away team score
                x['monday_tiebreaker']['total_diff'],                   # Closest to total score
                x['monday_tiebreaker']['submission_time'],              # Earlier submission time
                x['username']                                           # Alphabetical as final tiebreaker
            ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating week winners for Week {week}, {year}: {e}")
            return []
    
    def update_weekly_results(self, week: int, year: int) -> bool:
        """
        Update the weekly_results table with calculated results for a specific week
        """
        try:
            results = self.get_week_winners(week, year)
            if not results:
                logger.info(f"No results to update for Week {week}, {year}")
                return True
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing results for this week/year
            cursor.execute('''
                DELETE FROM weekly_results 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            # Insert new results
            for rank, result in enumerate(results, 1):
                is_winner = rank == 1  # First place is the winner
                
                cursor.execute('''
                    INSERT INTO weekly_results 
                    (user_id, week, year, total_picks, correct_picks, is_winner, weekly_rank, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['user_id'],
                    week,
                    year,
                    result['total_picks'],
                    result['correct_picks'],
                    is_winner,
                    rank,
                    datetime.now()
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated weekly results for Week {week}, {year} - {len(results)} users processed")
            return True
            
        except Exception as e:
            logger.error(f"Error updating weekly results for Week {week}, {year}: {e}")
            return False
    
    def update_all_completed_weeks(self) -> int:
        """
        Update weekly results for all weeks that have completed games
        Returns the number of weeks updated
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all weeks with completed games
            cursor.execute('''
                SELECT DISTINCT week, year 
                FROM nfl_games 
                WHERE is_final = 1
                ORDER BY year, week
            ''')
            
            completed_weeks = cursor.fetchall()
            conn.close()
            
            updated_count = 0
            for week_row in completed_weeks:
                week = week_row[0]
                year = week_row[1]
                
                if self.update_weekly_results(week, year):
                    updated_count += 1
            
            logger.info(f"Updated weekly results for {updated_count} completed weeks")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating all completed weeks: {e}")
            return 0
    
    def trigger_scoring_update_after_game_finalization(self, week: int, year: int) -> bool:
        """
        Called after games are marked as final to update scoring
        This should be called from update_live_scores when games are finalized
        """
        try:
            # Check if all games for the week are final
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       COUNT(CASE WHEN is_final = 1 THEN 1 END) as final_games
                FROM nfl_games 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            result = cursor.fetchone()
            total_games = result[0]
            final_games = result[1]
            
            conn.close()
            
            # Update weekly results if we have any final games
            # (even if not all games are final yet, for partial updates)
            if final_games > 0:
                self.update_weekly_results(week, year)
                logger.info(f"Updated scoring for Week {week}, {year} - {final_games}/{total_games} games final")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error triggering scoring update for Week {week}, {year}: {e}")
            return False

def create_weekly_results_table_if_not_exists():
    """Ensure the weekly_results table exists with proper structure"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week INTEGER NOT NULL,
                year INTEGER NOT NULL,
                total_picks INTEGER NOT NULL DEFAULT 0,
                correct_picks INTEGER NOT NULL DEFAULT 0,
                is_winner BOOLEAN NOT NULL DEFAULT FALSE,
                rank INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, week, year)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Weekly results table verified/created")
        return True
        
    except Exception as e:
        logger.error(f"Error creating weekly_results table: {e}")
        return False

if __name__ == "__main__":
    # Test the scoring updater
    logging.basicConfig(level=logging.INFO)
    
    # Ensure table exists
    create_weekly_results_table_if_not_exists()
    
    # Create updater and update all completed weeks
    updater = ScoringUpdater()
    updated_count = updater.update_all_completed_weeks()
    
    print(f"✅ Updated weekly results for {updated_count} completed weeks")
