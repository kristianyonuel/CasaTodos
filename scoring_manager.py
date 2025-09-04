"""
Enhanced Scoring System for NFL Fantasy League
Implements the closest total points logic for determining winners
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Any

class NFLScoringManager:
    """Manages scoring logic for NFL fantasy picks"""
    
    def __init__(self, db_path: str = 'nfl_fantasy.db'):
        self.db_path = db_path
        
        # Scoring configuration
        self.scoring_config = {
            'exact_team_prediction': 10,     # Points for exact team score
            'proximity_max_points': 5,       # Max points for close team prediction
            'total_proximity_max': 15,       # Max bonus for close total prediction
            'perfect_week_bonus': 20,        # Bonus for perfect week
            'monday_night_multiplier': 1.5   # Monday night confidence multiplier
        }
    
    def calculate_team_proximity_points(self, predicted: int, actual: int) -> int:
        """
        Calculate proximity points for a single team prediction
        Closer predictions get more points
        """
        difference = abs(predicted - actual)
        
        if difference == 0:
            return self.scoring_config['exact_team_prediction']
        elif difference <= 3:
            return 4
        elif difference <= 5:
            return 3
        elif difference <= 7:
            return 2
        elif difference <= 10:
            return 1
        else:
            return 0
    
    def calculate_total_proximity_bonus(self, predicted_total: int, actual_total: int) -> int:
        """
        Calculate bonus points for getting close to the combined total score
        This is the key feature you requested - rewarding closest total predictions
        """
        difference = abs(predicted_total - actual_total)
        
        if difference == 0:
            return 15  # Perfect total prediction
        elif difference <= 2:
            return 10  # Very close
        elif difference <= 5:
            return 7   # Close
        elif difference <= 10:
            return 5   # Somewhat close
        elif difference <= 15:
            return 3   # Getting there
        elif difference <= 20:
            return 1   # At least in the ballpark
        else:
            return 0   # Too far off
    
    def calculate_user_week_score(self, user_id: int, week: int, year: int) -> Dict[str, Any]:
        """
        Calculate a user's total score for a week based on their predictions
        and actual game results
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user's picks for the week with actual game results
            cursor.execute('''
                SELECT p.predicted_home_score, p.predicted_away_score,
                       p.confidence_level, p.is_correct,
                       g.home_team, g.away_team, g.home_score, g.away_score,
                       g.is_final, g.is_monday_night, g.game_date
                FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE p.user_id = ? AND g.week = ? AND g.year = ? AND g.is_final = 1
                ORDER BY g.game_date
            ''', (user_id, week, year))
            
            picks = cursor.fetchall()
            
            if not picks:
                return {
                    'total_score': 0,
                    'breakdown': {},
                    'message': 'No completed games found for this week'
                }
            
            # Initialize scoring breakdown
            breakdown = {
                'exact_predictions': 0,
                'proximity_points': 0,
                'total_proximity_bonus': 0,
                'monday_night_bonus': 0,
                'perfect_week_bonus': 0,
                'games_scored': 0,
                'total_score': 0
            }
            
            total_predicted_points = 0
            total_actual_points = 0
            exact_predictions_count = 0
            total_games = len(picks)
            
            # Score each game
            for pick in picks:
                # Skip if game isn't final
                if not pick['is_final']:
                    continue
                
                breakdown['games_scored'] += 1
                
                # Get predicted and actual scores
                pred_home = pick['predicted_home_score'] or 0
                pred_away = pick['predicted_away_score'] or 0
                actual_home = pick['home_score'] or 0
                actual_away = pick['away_score'] or 0
                
                # Add to totals for proximity bonus calculation
                total_predicted_points += pred_home + pred_away
                total_actual_points += actual_home + actual_away
                
                # Calculate points for home team prediction
                home_points = self.calculate_team_proximity_points(pred_home, actual_home)
                if pred_home == actual_home:
                    exact_predictions_count += 1
                    breakdown['exact_predictions'] += home_points
                else:
                    breakdown['proximity_points'] += home_points
                
                # Calculate points for away team prediction  
                away_points = self.calculate_team_proximity_points(pred_away, actual_away)
                if pred_away == actual_away:
                    exact_predictions_count += 1
                    breakdown['exact_predictions'] += away_points
                else:
                    breakdown['proximity_points'] += away_points
                
                # Monday night bonus (if enabled)
                if pick['is_monday_night']:
                    monday_bonus = int((home_points + away_points) * (self.scoring_config['monday_night_multiplier'] - 1))
                    breakdown['monday_night_bonus'] += monday_bonus
            
            # Calculate total proximity bonus (your key requirement)
            total_proximity_bonus = self.calculate_total_proximity_bonus(
                total_predicted_points, total_actual_points
            )
            breakdown['total_proximity_bonus'] = total_proximity_bonus
            
            # Perfect week bonus
            if exact_predictions_count == total_games * 2:  # 2 teams per game
                breakdown['perfect_week_bonus'] = self.scoring_config['perfect_week_bonus']
            
            # Calculate final total score
            breakdown['total_score'] = (
                breakdown['exact_predictions'] +
                breakdown['proximity_points'] +
                breakdown['total_proximity_bonus'] +
                breakdown['monday_night_bonus'] +
                breakdown['perfect_week_bonus']
            )
            
            # Add summary info
            breakdown['total_predicted_points'] = total_predicted_points
            breakdown['total_actual_points'] = total_actual_points
            breakdown['total_points_difference'] = abs(total_predicted_points - total_actual_points)
            
            conn.close()
            return breakdown
            
        except Exception as e:
            print(f"Error calculating user week score: {e}")
            return {
                'total_score': 0,
                'breakdown': {},
                'error': str(e)
            }
    
    def get_monday_night_tiebreaker_data(self, user_id: int, week: int, year: int) -> Dict[str, Any]:
        """
        Get Monday Night Football tiebreaker data for a user
        Returns home team difference, away team difference, and total difference
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get Monday Night game prediction and result
            cursor.execute('''
                SELECT p.predicted_home_score, p.predicted_away_score,
                       g.home_score, g.away_score, g.home_team, g.away_team
                FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE p.user_id = ? AND g.week = ? AND g.year = ? 
                  AND g.is_monday_night = 1 AND g.is_final = 1
                LIMIT 1
            ''', (user_id, week, year))
            
            monday_pick = cursor.fetchone()
            conn.close()
            
            if not monday_pick:
                return {
                    'has_monday_pick': False,
                    'home_difference': 999,
                    'away_difference': 999,
                    'total_difference': 999
                }
            
            # Calculate differences for tiebreaker
            pred_home = monday_pick['predicted_home_score'] or 0
            pred_away = monday_pick['predicted_away_score'] or 0
            actual_home = monday_pick['home_score'] or 0
            actual_away = monday_pick['away_score'] or 0
            
            home_diff = abs(pred_home - actual_home)
            away_diff = abs(pred_away - actual_away)
            total_diff = abs((pred_home + pred_away) - (actual_home + actual_away))
            
            return {
                'has_monday_pick': True,
                'home_difference': home_diff,
                'away_difference': away_diff,
                'total_difference': total_diff,
                'predicted_home': pred_home,
                'predicted_away': pred_away,
                'actual_home': actual_home,
                'actual_away': actual_away,
                'home_team': monday_pick['home_team'],
                'away_team': monday_pick['away_team']
            }
            
        except Exception as e:
            print(f"Error getting Monday night tiebreaker data: {e}")
            return {
                'has_monday_pick': False,
                'home_difference': 999,
                'away_difference': 999,
                'total_difference': 999
            }

    def determine_week_winner(self, week: int, year: int) -> List[Dict[str, Any]]:
        """
        Determine the winner(s) for a specific week based on scoring
        Returns sorted list of users with their scores
        Includes Monday Night tiebreaker logic
        """
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all users who made picks this week
            cursor.execute('''
                SELECT DISTINCT u.id, u.username
                FROM users u
                JOIN user_picks p ON u.id = p.user_id
                JOIN nfl_games g ON p.game_id = g.id
                WHERE g.week = ? AND g.year = ? AND u.is_admin = 0
            ''', (week, year))
            
            users = cursor.fetchall()
            user_scores = []
            
            # Calculate score for each user
            for user_id, username in users:
                score_data = self.calculate_user_week_score(user_id, week, year)
                monday_data = self.get_monday_night_tiebreaker_data(user_id, week, year)
                
                user_scores.append({
                    'user_id': user_id,
                    'username': username,
                    'total_score': score_data['total_score'],
                    'breakdown': score_data.get('breakdown', score_data),
                    'total_points_difference': score_data.get('total_points_difference', 999),
                    'monday_tiebreaker': monday_data
                })
            
            # Sort with Monday Night tiebreaker logic
            # 1. Highest total score first
            # 2. If tied, use Monday Night tiebreakers:
            #    a. Closest to home team score
            #    b. Closest to away team score  
            #    c. Closest to total combined score
            # 3. If still tied, use overall total points difference
            user_scores.sort(key=lambda x: (
                -x['total_score'],                                    # Highest score first
                x['monday_tiebreaker']['home_difference'],           # Closest to MNF home team
                x['monday_tiebreaker']['away_difference'],           # Closest to MNF away team
                x['monday_tiebreaker']['total_difference'],          # Closest to MNF total
                x['total_points_difference']                         # Overall total difference
            ))
            
            conn.close()
            return user_scores
            
        except Exception as e:
            print(f"Error determining week winner: {e}")
            return []
    
    def update_weekly_results(self, week: int, year: int) -> bool:
        """
        Update the weekly_results table with calculated scores
        """
        
        try:
            user_scores = self.determine_week_winner(week, year)
            
            if not user_scores:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update each user's weekly results
            for i, user_data in enumerate(user_scores):
                # Determine if this user is the winner (rank 1)
                is_winner = i == 0
                weekly_rank = i + 1
                
                breakdown = user_data['breakdown']
                
                cursor.execute('''
                    INSERT OR REPLACE INTO weekly_results
                    (user_id, week, year, total_points, weekly_rank, is_winner,
                     correct_picks, confidence_points, bonus_points, exact_score_bonus)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['user_id'],
                    week,
                    year,
                    breakdown['total_score'],
                    weekly_rank,
                    is_winner,
                    breakdown.get('exact_predictions', 0) // 10,  # Convert points back to count
                    breakdown.get('proximity_points', 0),
                    breakdown.get('total_proximity_bonus', 0) + breakdown.get('monday_night_bonus', 0),
                    breakdown.get('perfect_week_bonus', 0)
                ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Updated weekly results for Week {week}, {year}")
            print(f"   Winner: {user_scores[0]['username']} with {user_scores[0]['total_score']} points")
            
            return True
            
        except Exception as e:
            print(f"Error updating weekly results: {e}")
            return False

# Global instance
scoring_manager = NFLScoringManager()
