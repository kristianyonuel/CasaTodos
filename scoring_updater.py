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
                           g.home_score, g.away_score, p.created_at,
                           g.home_team, g.away_team
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
                
                # Get earliest pick submission time for this user for ANY game this week
                cursor.execute('''
                    SELECT MIN(p.created_at) as earliest_pick
                    FROM user_picks p
                    JOIN nfl_games g ON p.game_id = g.id
                    WHERE p.user_id = ? AND g.week = ? AND g.year = ?
                ''', (user_id, week, year))
                
                earliest_pick_row = cursor.fetchone()
                earliest_submission = earliest_pick_row['earliest_pick'] if earliest_pick_row and earliest_pick_row['earliest_pick'] else '9999-12-31 23:59:59'
                
                if monday_pick:
                    pred_home = monday_pick['predicted_home_score'] or 0
                    pred_away = monday_pick['predicted_away_score'] or 0
                    actual_home = monday_pick['home_score'] or 0
                    actual_away = monday_pick['away_score'] or 0
                    home_team = monday_pick['home_team']
                    away_team = monday_pick['away_team']
                    
                    # Check if user predicted correct winner based on selected_team field
                    selected_team = monday_pick['selected_team']
                    # Determine actual winner from the game scores
                    if actual_home > actual_away:
                        actual_winner = home_team  # Home team won
                        winner_score = actual_home
                        loser_score = actual_away
                        pred_winner_score = pred_home
                        pred_loser_score = pred_away
                    elif actual_away > actual_home:
                        actual_winner = away_team  # Away team won
                        winner_score = actual_away
                        loser_score = actual_home
                        pred_winner_score = pred_away
                        pred_loser_score = pred_home
                    else:
                        actual_winner = None  # Tie game (rare in NFL)
                        winner_score = actual_home
                        loser_score = actual_away
                        pred_winner_score = pred_home
                        pred_loser_score = pred_away
                    
                    correct_winner = selected_team == actual_winner
                    
                    # NEW TIEBREAKER RULES: 1) Total points, 2) Winner score, 3) Loser score
                    total_diff = abs((pred_home + pred_away) - (actual_home + actual_away))
                    winner_diff = abs(pred_winner_score - winner_score)
                    loser_diff = abs(pred_loser_score - loser_score)
                    
                    monday_tiebreaker = {
                        'correct_winner': correct_winner,
                        'home_diff': abs(pred_home - actual_home),
                        'away_diff': abs(pred_away - actual_away),
                        'total_diff': total_diff,
                        'winner_diff': winner_diff,  # NEW: Closest to winner score
                        'loser_diff': loser_diff,    # NEW: Closest to loser score
                        'submission_time': earliest_submission
                    }
                else:
                    # No Monday Night pick - use earliest submission time as tiebreaker
                    monday_tiebreaker['submission_time'] = earliest_submission
                
                results.append({
                    'user_id': user_id,
                    'username': username,
                    'total_picks': total_picks,
                    'correct_picks': correct_picks,
                    'monday_tiebreaker': monday_tiebreaker
                })
            
            conn.close()
            
            # Sort with NEW Monday Night tiebreaker logic
            # NEW RULES: 1) Most wins, 2) Total points closest, 3) Winner closest, 4) Loser closest
            results.sort(key=lambda x: (
                -x['correct_picks'],                                    # Most games won
                not x['monday_tiebreaker'].get('correct_winner', False),  # Correct winner first
                x['monday_tiebreaker'].get('total_diff', 999),          # 1st: Closest to total
                x['monday_tiebreaker'].get('winner_diff', 999),         # 2nd: Closest to winner
                x['monday_tiebreaker'].get('loser_diff', 999),          # 3rd: Closest to loser
                x['monday_tiebreaker']['submission_time'],              # Earlier submission
                x['username']                                           # Alphabetical final
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

            # Check if the week is completely finished before declaring winners
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       COUNT(CASE WHEN is_final = 1 THEN 1 END) as completed_games
                FROM nfl_games 
                WHERE week = ? AND year = ?
            ''', (week, year))

            total_games, completed_games = cursor.fetchone()
            week_completed = (total_games == completed_games and total_games > 0)

            logger.info(f"Week {week}, {year}: {completed_games}/{total_games} games completed - Week completed: {week_completed}")

            # Clear existing results for this week/year
            cursor.execute('''
                DELETE FROM weekly_results 
                WHERE week = ? AND year = ?
            ''', (week, year))

            # Insert new results
            for rank, result in enumerate(results, 1):
                # Mark as winner if they're ranked #1 and the week is completed
                # OR if they have a clear lead in points (no ties at the top)
                is_winner = False
                if rank == 1 and week_completed:
                    # Check if there's a tie at the top
                    top_score = results[0]['correct_picks']
                    tied_count = sum(1 for r in results if r['correct_picks'] == top_score)
                    
                    if tied_count == 1:
                        # Clear winner - no ties
                        is_winner = True
                    else:
                        # Tie exists - use tiebreaker logic
                        # First player in the sorted results wins the tiebreaker
                        is_winner = True
                        logger.info(f"Week {week}: Tiebreaker resolved - {result['username']} wins with {top_score} points")

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
