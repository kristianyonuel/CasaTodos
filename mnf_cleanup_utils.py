"""
Monday Night Football Data Cleanup Utilities

This module provides functions to automatically clean up obsolete score predictions
when the Monday Night Football detection logic changes.
"""

import sqlite3
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def cleanup_obsolete_mnf_predictions(db_path: str, week: int = None, year: int = None) -> int:
    """
    Clean up obsolete Monday Night Football score predictions.
    
    This function removes score predictions for games that are no longer considered
    the actual Monday Night Football game due to the updated detection logic.
    
    Args:
        db_path: Path to the database file
        week: Specific week to clean (optional, defaults to all weeks)
        year: Specific year to clean (optional, defaults to current year)
    
    Returns:
        Number of predictions cleaned up
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    total_cleaned = 0
    
    try:
        # Get weeks to process
        if week and year:
            weeks_query = 'SELECT DISTINCT week, year FROM nfl_games WHERE week = ? AND year = ?'
            weeks_params = (week, year)
        elif year:
            weeks_query = 'SELECT DISTINCT week, year FROM nfl_games WHERE year = ?'
            weeks_params = (year,)
        else:
            weeks_query = 'SELECT DISTINCT week, year FROM nfl_games WHERE year = 2025'
            weeks_params = ()
        
        cursor.execute(weeks_query, weeks_params)
        weeks = cursor.fetchall()
        
        for week_data in weeks:
            w = week_data['week']
            y = week_data['year']
            
            # Find all Monday games for this week
            cursor.execute('''
                SELECT id, away_team, home_team, game_date
                FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND strftime('%w', game_date) = '1'  -- Monday games
                ORDER BY game_date ASC
            ''', (w, y))
            
            monday_games = cursor.fetchall()
            
            if len(monday_games) <= 1:
                continue  # No cleanup needed if 1 or 0 Monday games
            
            # Find the actual Monday Night Football game using new logic
            cursor.execute('''
                SELECT id FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND strftime('%w', game_date) = '1'  -- Monday
                ORDER BY game_date DESC, id DESC
                LIMIT 1
            ''', (w, y))
            
            actual_mnf_game = cursor.fetchone()
            actual_mnf_id = actual_mnf_game[0] if actual_mnf_game else None
            
            if not actual_mnf_id:
                continue
            
            # Find games that have score predictions but are NOT the actual MNF game
            obsolete_game_ids = [game['id'] for game in monday_games if game['id'] != actual_mnf_id]
            
            for obsolete_game_id in obsolete_game_ids:
                # Clean up score predictions for this obsolete game
                cursor.execute('''
                    UPDATE user_picks 
                    SET predicted_home_score = NULL, predicted_away_score = NULL
                    WHERE game_id = ? 
                    AND (predicted_home_score IS NOT NULL OR predicted_away_score IS NOT NULL)
                ''', (obsolete_game_id,))
                
                cleaned_count = cursor.rowcount
                total_cleaned += cleaned_count
                
                if cleaned_count > 0:
                    # Get game details for logging
                    cursor.execute('''
                        SELECT away_team, home_team FROM nfl_games WHERE id = ?
                    ''', (obsolete_game_id,))
                    game_info = cursor.fetchone()
                    
                    if game_info:
                        logger.info(f"Cleaned {cleaned_count} obsolete MNF predictions for "
                                  f"Week {w} {game_info['away_team']} @ {game_info['home_team']}")
        
        conn.commit()
        
        if total_cleaned > 0:
            logger.info(f"MNF cleanup complete: Removed {total_cleaned} obsolete score predictions")
        
    except Exception as e:
        logger.error(f"Error during MNF cleanup: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    return total_cleaned

def get_actual_mnf_game_id(db_path: str, week: int, year: int) -> int:
    """
    Get the ID of the actual Monday Night Football game for a given week.
    
    Args:
        db_path: Path to the database file
        week: Week number
        year: Year
    
    Returns:
        Game ID of the actual MNF game, or None if no Monday games
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id FROM nfl_games 
            WHERE week = ? AND year = ? 
            AND strftime('%w', game_date) = '1'  -- Monday
            ORDER BY game_date DESC, id DESC
            LIMIT 1
        ''', (week, year))
        
        result = cursor.fetchone()
        return result[0] if result else None
        
    finally:
        conn.close()

def validate_mnf_predictions(db_path: str, week: int, year: int) -> Dict[str, Any]:
    """
    Validate that score predictions only exist for the actual MNF game.
    
    Args:
        db_path: Path to the database file
        week: Week number
        year: Year
    
    Returns:
        Dictionary with validation results
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get actual MNF game
        actual_mnf_id = get_actual_mnf_game_id(db_path, week, year)
        
        # Get all Monday games
        cursor.execute('''
            SELECT id, away_team, home_team, game_date
            FROM nfl_games 
            WHERE week = ? AND year = ? 
            AND strftime('%w', game_date) = '1'
            ORDER BY game_date ASC
        ''', (week, year))
        
        monday_games = cursor.fetchall()
        
        validation_result = {
            'week': week,
            'year': year,
            'total_monday_games': len(monday_games),
            'actual_mnf_id': actual_mnf_id,
            'is_valid': True,
            'issues': []
        }
        
        # Check each Monday game for score predictions
        for game in monday_games:
            cursor.execute('''
                SELECT COUNT(*) as prediction_count
                FROM user_picks 
                WHERE game_id = ? 
                AND (predicted_home_score IS NOT NULL OR predicted_away_score IS NOT NULL)
            ''', (game['id'],))
            
            prediction_count = cursor.fetchone()['prediction_count']
            
            game_info = {
                'game_id': game['id'],
                'game_label': f"{game['away_team']} @ {game['home_team']}",
                'is_actual_mnf': game['id'] == actual_mnf_id,
                'prediction_count': prediction_count
            }
            
            # Flag issues where non-MNF games have predictions
            if not game_info['is_actual_mnf'] and prediction_count > 0:
                validation_result['is_valid'] = False
                validation_result['issues'].append({
                    'type': 'obsolete_predictions',
                    'game_info': game_info,
                    'message': f"Non-MNF game {game_info['game_label']} has {prediction_count} score predictions"
                })
        
        return validation_result
        
    finally:
        conn.close()
