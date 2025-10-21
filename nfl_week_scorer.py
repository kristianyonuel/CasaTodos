#!/usr/bin/env python3
"""
NFL Fantasy Week Scoring System
Handles complete week scoring including tiebreaker analysis for Monday Night Football
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict, Optional


class NFLWeekScorer:
    """Handles scoring for an NFL fantasy week including tiebreaker resolution"""
    
    def __init__(self, db_path: str = 'nfl_fantasy.db'):
        self.db_path = db_path
    
    def connect_db(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def calculate_week_scores(self, week: int, year: int = 2025) -> Dict:
        """
        Calculate complete week scores including tiebreaker analysis
        
        Args:
            week: NFL week number
            year: Season year
            
        Returns:
            Dict with scoring results and tiebreaker winner
        """
        conn = self.connect_db()
        cursor = conn.cursor()
        
        print(f"=== CALCULATING WEEK {week} SCORES ===")
        
        # Update all pick results based on final game scores
        self._update_pick_results(cursor, week, year)
        
        # Get user standings
        standings = self._get_user_standings(cursor, week, year)
        
        # Find users tied for first place
        if standings:
            max_points = standings[0]['points']
            tied_users = [user for user in standings if user['points'] == max_points]
            
            if len(tied_users) > 1:
                print(f"\n🔥 TIE DETECTED: {len(tied_users)} users tied with {max_points} points")
                
                # Resolve tiebreaker using Monday Night Football prediction
                tiebreaker_winner = self._resolve_tiebreaker(cursor, week, year, tied_users)
                
                conn.close()
                return {
                    'standings': standings,
                    'tied_users': tied_users,
                    'tiebreaker_winner': tiebreaker_winner,
                    'week': week,
                    'year': year
                }
            else:
                print(f"\n🏆 CLEAR WINNER: {standings[0]['username']} with {max_points} points")
        
        conn.close()
        return {
            'standings': standings,
            'tied_users': None,
            'tiebreaker_winner': None,
            'week': week,
            'year': year
        }
    
    def _update_pick_results(self, cursor, week: int, year: int):
        """Update all pick results for completed games"""
        
        # Get all completed games for the week
        cursor.execute('''
            SELECT id, away_team, home_team, away_score, home_score
            FROM nfl_games 
            WHERE week = ? AND year = ? AND is_final = 1
        ''', (week, year))
        
        games = cursor.fetchall()
        
        for game in games:
            game_id = game['id']
            away_score = game['away_score']
            home_score = game['home_score']
            
            # Determine winner
            winner = game['home_team'] if home_score > away_score else game['away_team']
            
            # Update all picks for this game
            cursor.execute('''
                UPDATE user_picks 
                SET is_correct = (selected_team = ?),
                    points_earned = CASE WHEN selected_team = ? THEN 1 ELSE 0 END
                WHERE game_id = ?
            ''', (winner, winner, game_id))
        
        cursor.connection.commit()
        print(f"✅ Updated results for {len(games)} completed games")
    
    def _get_user_standings(self, cursor, week: int, year: int) -> List[Dict]:
        """Get current user standings for the week"""
        
        cursor.execute('''
            SELECT u.username, 
                   COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                   SUM(p.points_earned) as points,
                   u.id as user_id
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.week = ? AND g.year = ? AND u.id > 1
            GROUP BY u.id, u.username
            ORDER BY points DESC, correct_picks DESC, u.username
        ''', (week, year))
        
        standings = []
        for row in cursor.fetchall():
            user_data = dict(row)
            
            # Calculate accuracy
            total = user_data['total_picks'] or 0
            correct = user_data['correct_picks'] or 0
            user_data['accuracy'] = (correct / total * 100) if total > 0 else 0.0
            
            standings.append(user_data)
        
        return standings
    
    def _resolve_tiebreaker(self, cursor, week: int, year: int, tied_users: List[Dict]) -> Optional[Dict]:
        """
        Resolve tiebreaker using Monday Night Football score predictions
        
        Args:
            cursor: Database cursor
            week: NFL week number
            year: Season year
            tied_users: List of users tied for first place
            
        Returns:
            Dict with tiebreaker winner info, or None if no tiebreaker predictions
        """
        
        print(f"\n=== RESOLVING TIEBREAKER FOR WEEK {week} ===")
        
        # Find Monday Night Football game for tiebreaker (HOU @ SEA for Week 7)
        cursor.execute('''
            SELECT id, away_team, home_team, away_score, home_score
            FROM nfl_games 
            WHERE week = ? AND year = ? AND away_team = 'HOU' AND home_team = 'SEA'
            AND is_final = 1
            LIMIT 1
        ''', (week, year))
        
        mnf_game = cursor.fetchone()
        if not mnf_game:
            print("⚠️  No completed Monday Night Football game found for tiebreaker")
            return None
        
        game_id = mnf_game['id']
        actual_away = mnf_game['away_score']
        actual_home = mnf_game['home_score']
        actual_total = actual_away + actual_home
        
        print(f"MNF Tiebreaker Game: {mnf_game['away_team']} @ {mnf_game['home_team']}")
        print(f"Actual Score: {mnf_game['away_team']} {actual_away} - {mnf_game['home_team']} {actual_home}")
        print(f"Actual Total: {actual_total}")
        
        # Get tiebreaker predictions from tied users
        tied_user_ids = [user['user_id'] for user in tied_users]
        placeholders = ','.join('?' * len(tied_user_ids))
        
        cursor.execute(f'''
            SELECT u.username, u.id as user_id,
                   p.predicted_away_score, p.predicted_home_score
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            WHERE p.game_id = ? AND u.id IN ({placeholders})
            AND p.predicted_away_score IS NOT NULL 
            AND p.predicted_home_score IS NOT NULL
        ''', [game_id] + tied_user_ids)
        
        tiebreaker_predictions = cursor.fetchall()
        
        if not tiebreaker_predictions:
            print("⚠️  No tiebreaker predictions found from tied users")
            return None
        
        print(f"\n📊 TIEBREAKER PREDICTIONS:")
        
        best_prediction = None
        best_diff = float('inf')
        
        for pred in tiebreaker_predictions:
            username = pred['username']
            pred_away = pred['predicted_away_score']
            pred_home = pred['predicted_home_score']
            pred_total = pred_away + pred_home
            
            # Calculate differences
            away_diff = abs(actual_away - pred_away)
            home_diff = abs(actual_home - pred_home)
            total_diff = abs(actual_total - pred_total)
            combined_diff = away_diff + home_diff
            
            print(f"  {username}: Predicted {pred_away}-{pred_home} (Total: {pred_total})")
            print(f"    Differences: Away {away_diff}, Home {home_diff}, Total {total_diff}")
            
            # Use total score difference as primary tiebreaker
            if total_diff < best_diff:
                best_diff = total_diff
                best_prediction = {
                    'username': username,
                    'user_id': pred['user_id'],
                    'predicted_away': pred_away,
                    'predicted_home': pred_home,
                    'predicted_total': pred_total,
                    'total_difference': total_diff,
                    'combined_difference': combined_diff
                }
        
        if best_prediction:
            print(f"\n🏆 TIEBREAKER WINNER: {best_prediction['username']}")
            print(f"   Closest total score prediction (difference: {best_prediction['total_difference']})")
            
        return best_prediction
    
    def print_week_results(self, results: Dict):
        """Print formatted week results"""
        
        week = results['week']
        standings = results['standings']
        tied_users = results['tied_users']
        tiebreaker_winner = results['tiebreaker_winner']
        
        print(f"\n🏆 WEEK {week} FINAL RESULTS:")
        print("=" * 60)
        
        for i, user in enumerate(standings[:10], 1):  # Show top 10
            username = user['username']
            correct = user['correct_picks'] or 0
            total = user['total_picks'] or 0
            points = user['points'] or 0
            accuracy = user['accuracy']
            
            # Format picks info
            if total == 15:
                picks_info = f"{correct}/{total}"
            else:
                missed = 15 - total
                picks_info = f"{correct}/{total} (missed {missed})"
            
            # Add tiebreaker winner indicator
            winner_indicator = ""
            if tiebreaker_winner and user['user_id'] == tiebreaker_winner['user_id']:
                winner_indicator = " 🏆 TIEBREAKER WINNER"
            elif tied_users and len(tied_users) > 1 and user['user_id'] in [u['user_id'] for u in tied_users]:
                winner_indicator = " 🤝 TIED"
            
            print(f"{i:2d}. {username:12s}: {picks_info} ({accuracy:4.1f}%) - {points} points{winner_indicator}")
        
        if tied_users and len(tied_users) > 1:
            if tiebreaker_winner:
                print(f"\nTiebreaker resolved by Monday Night Football prediction accuracy")
            else:
                print(f"\nTie remains unresolved - no valid tiebreaker predictions")


def score_current_week():
    """Score the current NFL week"""
    
    from nfl_week_calculator import get_current_nfl_week
    
    try:
        current_week = get_current_nfl_week(2025)
        print(f"Scoring Week {current_week}...")
        
        scorer = NFLWeekScorer()
        results = scorer.calculate_week_scores(current_week, 2025)
        scorer.print_week_results(results)
        
        return results
        
    except Exception as e:
        print(f"Error scoring current week: {e}")
        return None


def score_specific_week(week: int, year: int = 2025):
    """Score a specific week"""
    
    print(f"Scoring Week {week}, {year}...")
    
    scorer = NFLWeekScorer()
    results = scorer.calculate_week_scores(week, year)
    scorer.print_week_results(results)
    
    return results


if __name__ == "__main__":
    # Example usage
    print("NFL Fantasy Week Scorer")
    print("=" * 40)
    
    # Score Week 7 as an example
    results = score_specific_week(7, 2025)