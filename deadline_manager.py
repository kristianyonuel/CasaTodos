"""
NFL Game Deadline Management System
Handles dynamic deadlines based on actual game times and league rules
"""
from __future__ import annotations

import sqlite3
import pytz
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from utils.timezone_utils import convert_to_ast
from deadline_override_manager import DeadlineOverrideManager

class DeadlineManager:
    """Manages game submission deadlines based on NFL schedule"""
    
    def __init__(self):
        self.ast_tz = pytz.timezone('America/Puerto_Rico')
        
        # Default deadline offsets (minutes before game start)
        self.deadline_offsets = {
            'thursday_night': 5,     # 5 minutes before TNF (more lenient)
            'sunday_games': 15,      # 15 minutes before first Sunday game  
            'monday_night': 5,       # 5 minutes before MNF (more lenient)
            'elimination': 10080     # 7 days (7 * 24 * 60) before Saturday
        }
    
    def get_week_deadlines(self, week: int, year: int) -> Dict[str, Dict]:
        """Get all deadlines for a specific week"""
        
        deadlines = {
            'thursday_night': None,
            'sunday_games': None, 
            'monday_night': None,
            'elimination': None
        }
        
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all games for the week
            cursor.execute('''
                SELECT game_date, is_thursday_night, is_sunday_night, is_monday_night,
                       home_team, away_team, game_id
                FROM nfl_games 
                WHERE week = ? AND year = ?
                ORDER BY game_date
            ''', (week, year))
            
            games = cursor.fetchall()
            
            if not games:
                return self._get_default_deadlines()
            
            # Process each game type
            for game in games:
                game_time = datetime.strptime(game[0], '%Y-%m-%d %H:%M:%S')
                game_time_ast = convert_to_ast(game_time)
                
                if game[1]:  # Thursday Night
                    deadlines['thursday_night'] = {
                        'game_time': game_time_ast,
                        'deadline': game_time_ast - timedelta(minutes=self.deadline_offsets['thursday_night']),
                        'matchup': f"{game[5]} @ {game[4]}",
                        'status': self._get_deadline_status(game_time_ast, 'thursday_night')
                    }
                
                elif game[3]:  # Monday Night  
                    deadlines['monday_night'] = {
                        'game_time': game_time_ast,
                        'deadline': game_time_ast - timedelta(minutes=self.deadline_offsets['monday_night']),
                        'matchup': f"{game[5]} @ {game[4]}",
                        'status': self._get_deadline_status(game_time_ast, 'monday_night')
                    }
            
            # Find first Sunday game for Sunday deadline
            sunday_games = [g for g in games if not g[1] and not g[2] and not g[3]]
            if sunday_games:
                first_sunday = min(sunday_games, key=lambda x: x[0])
                sunday_time = datetime.strptime(first_sunday[0], '%Y-%m-%d %H:%M:%S')
                sunday_time_ast = convert_to_ast(sunday_time)
                
                deadlines['sunday_games'] = {
                    'game_time': sunday_time_ast,
                    'deadline': sunday_time_ast - timedelta(minutes=self.deadline_offsets['sunday_games']),
                    'matchup': f"First Sunday Game: {first_sunday[5]} @ {first_sunday[4]}",
                    'status': self._get_deadline_status(sunday_time_ast, 'sunday_games')
                }
            
            # Calculate elimination deadline (7 days before Saturday)
            if games:
                first_game = min(games, key=lambda x: x[0])
                first_game_time = datetime.strptime(first_game[0], '%Y-%m-%d %H:%M:%S')
                # Find the Saturday before the week
                days_until_saturday = (5 - first_game_time.weekday()) % 7
                saturday = first_game_time - timedelta(days=days_until_saturday)
                elimination_deadline = saturday - timedelta(days=7)
                
                deadlines['elimination'] = {
                    'game_time': convert_to_ast(first_game_time),
                    'deadline': convert_to_ast(elimination_deadline),
                    'matchup': f"Week {week} Elimination Format",
                    'status': self._get_deadline_status(elimination_deadline, 'elimination')
                }
            
            conn.close()
        
        except Exception as e:
            print(f"Error calculating deadlines: {e}")
            return self._get_default_deadlines()
        
        return deadlines
    
    def _get_deadline_status(self, game_time: datetime, game_type: str) -> Dict[str, any]:
        """Determine if deadline is open, closing soon, or closed"""
        now = datetime.now(self.ast_tz)
        deadline = game_time - timedelta(minutes=self.deadline_offsets[game_type])
        
        if now < deadline:
            time_until_deadline = deadline - now
            
            if time_until_deadline.total_seconds() < 3600:  # Less than 1 hour
                return {
                    'status': 'closing_soon',
                    'message': f"Closes in {int(time_until_deadline.total_seconds() // 60)} minutes",
                    'css_class': 'warning'
                }
            else:
                return {
                    'status': 'open', 
                    'message': f"Open until {deadline.strftime('%a %I:%M %p AST')}",
                    'css_class': 'success'
                }
        else:
            return {
                'status': 'closed',
                'message': f"Closed since {deadline.strftime('%a %I:%M %p AST')}",
                'css_class': 'danger'
            }
    
    def _get_default_deadlines(self) -> Dict[str, Dict]:
        """Return default deadlines when no games are scheduled"""
        now = datetime.now(self.ast_tz)
        
        return {
            'thursday_night': {
                'deadline': None,
                'status': {'status': 'no_game', 'message': 'No Thursday game this week', 'css_class': 'info'}
            },
            'sunday_games': {
                'deadline': None, 
                'status': {'status': 'no_game', 'message': 'No Sunday games scheduled', 'css_class': 'info'}
            },
            'monday_night': {
                'deadline': None,
                'status': {'status': 'no_game', 'message': 'No Monday game this week', 'css_class': 'info'}
            },
            'elimination': {
                'deadline': None,
                'status': {'status': 'no_game', 'message': 'Elimination format not active', 'css_class': 'info'}
            }
        }
    
    def is_picks_allowed(self, week: int, year: int, game_type: str = 'sunday_games') -> Tuple[bool, str]:
        """Check if picks are still allowed for a specific game type"""
        deadlines = self.get_week_deadlines(week, year)
        
        if game_type not in deadlines or not deadlines[game_type]:
            return True, "No deadline set"
        
        deadline_info = deadlines[game_type]
        status = deadline_info.get('status', {})
        
        if status.get('status') == 'closed':
            return False, status.get('message', 'Deadline has passed')
        
        return True, status.get('message', 'Picks are open')
    
    def get_next_deadline(self, week: int, year: int) -> Optional[Dict]:
        """Get the next upcoming deadline"""
        deadlines = self.get_week_deadlines(week, year)
        now = datetime.now(self.ast_tz)
        
        upcoming_deadlines = []
        
        for game_type, deadline_info in deadlines.items():
            if deadline_info and deadline_info.get('deadline'):
                deadline = deadline_info['deadline']
                if deadline > now:
                    upcoming_deadlines.append({
                        'type': game_type,
                        'deadline': deadline,
                        'info': deadline_info
                    })
        
        if upcoming_deadlines:
            return min(upcoming_deadlines, key=lambda x: x['deadline'])
        
        return None
    
    def can_make_picks(self, week: int, year: int, game_date: str = None) -> bool:
        """Check if picks can still be made for a specific game or week"""
        try:
            now = datetime.now(self.ast_tz)
            
            if game_date:
                # Check specific game
                game_time = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S')
                game_time_ast = convert_to_ast(game_time)
                
                # Determine game type and use appropriate deadline offset
                weekday = game_time_ast.weekday()  # Monday = 0, Sunday = 6
                
                if weekday == 3:  # Thursday
                    offset_minutes = self.deadline_offsets['thursday_night']
                elif weekday == 0:  # Monday  
                    offset_minutes = self.deadline_offsets['monday_night']
                else:  # Sunday and other days
                    offset_minutes = self.deadline_offsets['sunday_games']
                
                # Calculate deadline using appropriate offset
                deadline = game_time_ast - timedelta(minutes=offset_minutes)
                
                # Debug logging
                print(f"DEBUG: Game time (AST): {game_time_ast}")
                print(f"DEBUG: Current time (AST): {now}")
                print(f"DEBUG: Deadline ({offset_minutes} min before): {deadline}")
                print(f"DEBUG: Minutes until deadline: {(deadline - now).total_seconds() / 60:.1f}")
                print(f"DEBUG: Can make picks: {now < deadline}")
                
                return now < deadline
            
            # If no specific game date, check general week deadlines
            deadlines = self.get_week_deadlines(week, year)
            
            # If no specific game date, check if any deadline is still open
            for key, deadline_info in deadlines.items():
                if deadline_info and deadline_info.get('deadline'):
                    if now < deadline_info['deadline']:
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking pick availability: {e}")
            # Default to allowing picks if error occurs (safer for users)
            return True
    
    def get_deadline_summary(self, week: int, year: int) -> Dict[str, Any]:
        """Get a user-friendly summary of deadlines with hours remaining"""
        try:
            deadlines = self.get_week_deadlines(week, year)
            now = datetime.now(self.ast_tz)
            
            summary = {
                'thursday': None,
                'sunday': None,
                'monday': None,
                'next_deadline': None,
                'all_deadlines_passed': True
            }
            
            for key, deadline_info in deadlines.items():
                if deadline_info and deadline_info.get('deadline'):
                    deadline = deadline_info['deadline']
                    hours_remaining = (deadline - now).total_seconds() / 3600
                    
                    deadline_summary = {
                        'deadline': deadline,
                        'hours_remaining': hours_remaining,
                        'passed': hours_remaining <= 0,
                        'matchup': deadline_info.get('matchup', ''),
                        'formatted_time': deadline.strftime('%A %-I:%M %p AST'),
                        'urgency': 'critical' if 0 < hours_remaining <= 2 else 'warning' if 0 < hours_remaining <= 24 else 'normal'
                    }
                    
                    if key == 'thursday_night':
                        summary['thursday'] = deadline_summary
                    elif key == 'sunday_games':
                        summary['sunday'] = deadline_summary
                    elif key == 'monday_night':
                        summary['monday'] = deadline_summary
                    
                    if hours_remaining > 0:
                        summary['all_deadlines_passed'] = False
                        if not summary['next_deadline'] or hours_remaining < summary['next_deadline']['hours_remaining']:
                            summary['next_deadline'] = deadline_summary.copy()
                            summary['next_deadline']['type'] = key
            
            return summary
            
        except Exception as e:
            print(f"Error getting deadline summary: {e}")
            return {
                'thursday': None,
                'sunday': None, 
                'monday': None,
                'next_deadline': None,
                'all_deadlines_passed': False
            }
    
    def get_user_deadline_summary(self, week: int, year: int, user_id: int) -> Dict[str, Any]:
        """Get deadline summary for a specific user, considering overrides"""
        try:
            # Get base deadlines
            base_summary = self.get_deadline_summary(week, year)
            override_manager = DeadlineOverrideManager()
            
            # Check for user-specific or global overrides
            for deadline_type in ['thursday', 'sunday', 'monday']:
                if base_summary[deadline_type]:
                    original_deadline = base_summary[deadline_type]['deadline']
                    
                    # Map deadline types to database format
                    db_type = deadline_type
                    if deadline_type == 'thursday':
                        db_type = 'thursday'
                    elif deadline_type == 'sunday':
                        db_type = 'sunday'
                    elif deadline_type == 'monday':
                        db_type = 'monday'
                    
                    # Get effective deadline (considering overrides)
                    effective_deadline = override_manager.get_user_deadline(
                        week, year, db_type, user_id, original_deadline
                    )
                    
                    if effective_deadline != original_deadline:
                        # Update with override deadline
                        now = datetime.now(self.ast_tz)
                        hours_remaining = (effective_deadline - now).total_seconds() / 3600
                        
                        base_summary[deadline_type].update({
                            'deadline': effective_deadline,
                            'hours_remaining': hours_remaining,
                            'passed': hours_remaining <= 0,
                            'formatted_time': effective_deadline.strftime('%A %-I:%M %p AST'),
                            'urgency': 'critical' if 0 < hours_remaining <= 2 else 'warning' if 0 < hours_remaining <= 24 else 'normal',
                            'is_override': True
                        })
            
            return base_summary
            
        except Exception as e:
            print(f"Error getting user deadline summary: {e}")
            return self.get_deadline_summary(week, year)

# Global instance
deadline_manager = DeadlineManager()
