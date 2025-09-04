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

class DeadlineManager:
    """Manages game submission deadlines based on NFL schedule"""
    
    def __init__(self):
        self.ast_tz = pytz.timezone('America/Puerto_Rico')
        
        # Default deadline offsets (minutes before game start)
        self.deadline_offsets = {
            'thursday_night': 30,    # 30 minutes before TNF
            'friday_games': 30,      # 30 minutes before Friday games
            'saturday_games': 30,    # 30 minutes before Saturday games
            'sunday_games': 30,      # 30 minutes before first Sunday game (covers Sunday + Monday)
            'monday_night': 30,      # Uses same deadline as Sunday games
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
            
            # Separate games by type
            thursday_games = []
            friday_games = []
            saturday_games = []
            sunday_monday_games = []
            
            for game in games:
                try:
                    # Parse game time - ensure we handle it as UTC first
                    if isinstance(game[0], str):
                        game_time = datetime.strptime(game[0], '%Y-%m-%d %H:%M:%S')
                        # Assume stored times are in UTC, then convert to AST
                        game_time_utc = game_time.replace(tzinfo=pytz.UTC)
                        game_time_ast = game_time_utc.astimezone(self.ast_tz)
                    else:
                        game_time_ast = convert_to_ast(game[0])
                    
                    # Determine game type based on day of week and flags
                    weekday = game_time_ast.weekday()  # Monday = 0, Sunday = 6
                    
                    if game[1]:  # Thursday Night flag
                        thursday_games.append((game, game_time_ast))
                    elif weekday == 4:  # Friday = 4
                        friday_games.append((game, game_time_ast))
                    elif weekday == 5:  # Saturday = 5
                        saturday_games.append((game, game_time_ast))
                    else:  # Sunday, Monday, or other days
                        sunday_monday_games.append((game, game_time_ast))
                        
                except Exception as e:
                    print(f"Error processing game {game}: {e}")
                    continue
            
            # Process Thursday Night games
            if thursday_games:
                game, game_time_ast = thursday_games[0]  # Usually only one Thursday game
                deadline = game_time_ast - timedelta(minutes=self.deadline_offsets['thursday_night'])
                deadlines['thursday_night'] = {
                    'game_time': game_time_ast,
                    'deadline': deadline,
                    'matchup': f"{game[5]} @ {game[4]}",
                    'status': self._get_deadline_status(game_time_ast, 'thursday_night')
                }
            
            # Friday games have individual deadlines (NOT included in Sunday deadline)
            if friday_games:
                deadlines['friday_games'] = []
                for game, game_time_ast in friday_games:
                    deadline = game_time_ast - timedelta(minutes=self.deadline_offsets['friday_games'])
                    deadlines['friday_games'].append({
                        'game_time': game_time_ast,
                        'deadline': deadline,
                        'matchup': f"{game[5]} @ {game[4]}",
                        'status': self._get_deadline_status(game_time_ast, 'friday_games')
                    })
            
            # Saturday games have individual deadlines (NOT included in Sunday deadline)
            if saturday_games:
                deadlines['saturday_games'] = []
                for game, game_time_ast in saturday_games:
                    deadline = game_time_ast - timedelta(minutes=self.deadline_offsets['saturday_games'])
                    deadlines['saturday_games'].append({
                        'game_time': game_time_ast,
                        'deadline': deadline,
                        'matchup': f"{game[5]} @ {game[4]}",
                        'status': self._get_deadline_status(game_time_ast, 'saturday_games')
                    })
                    
            # Find first Sunday game for Sunday+Monday deadline
            # Only Sunday and Monday games share the same deadline: 30 minutes before first Sunday game
            # Friday and Saturday games are NOT included in this deadline
            if sunday_monday_games:
                first_sunday = min(sunday_monday_games, key=lambda x: x[1])  # x[1] is game_time_ast
                game, sunday_time_ast = first_sunday
                
                deadline = sunday_time_ast - timedelta(minutes=self.deadline_offsets['sunday_games'])
                deadlines['sunday_games'] = {
                    'game_time': sunday_time_ast,
                    'deadline': deadline,
                    'matchup': f"First Sunday Game: {game[5]} @ {game[4]}",
                    'status': self._get_deadline_status(sunday_time_ast, 'sunday_games')
                }
                
                # Monday games also use this same deadline
                monday_games = [(g, t) for g, t in sunday_monday_games if g[3]]  # Monday Night games
                if monday_games:
                    monday_game, monday_time_ast = monday_games[0]  # Usually only one Monday game
                    
                    deadlines['monday_night'] = {
                        'game_time': monday_time_ast,
                        'deadline': deadline,  # Same deadline as Sunday games
                        'matchup': f"{monday_game[5]} @ {monday_game[4]}",
                        'status': self._get_deadline_status(sunday_time_ast, 'sunday_games')  # Status based on Sunday game
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
        
        # Ensure game_time is timezone-aware (AST)
        if game_time.tzinfo is None:
            game_time = self.ast_tz.localize(game_time)
        elif game_time.tzinfo != self.ast_tz:
            game_time = game_time.astimezone(self.ast_tz)
        
        deadline = game_time - timedelta(minutes=self.deadline_offsets[game_type])
        time_until_deadline = (deadline - now).total_seconds()
        hours_until_deadline = time_until_deadline / 3600
        
        return {
            'is_closed': time_until_deadline <= 0,
            'hours_until_deadline': hours_until_deadline,
            'deadline_time': deadline,
            'game_time': game_time,
            'current_time': now
        }
    
    def _get_default_deadlines(self) -> Dict[str, Dict]:
        """Return default deadlines when no games are scheduled"""
        now = datetime.now(self.ast_tz)
        
        return {
            'thursday_night': {
                'deadline': None,
                'status': {'status': 'no_game', 'message': 'No Thursday game this week', 'css_class': 'info'}
            },
            'friday_games': {
                'deadline': None,
                'status': {'status': 'no_game', 'message': 'No Friday games this week', 'css_class': 'info'}
            },
            'saturday_games': {
                'deadline': None,
                'status': {'status': 'no_game', 'message': 'No Saturday games this week', 'css_class': 'info'}
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
            deadlines = self.get_week_deadlines(week, year)
            now = datetime.now(self.ast_tz)
            
            if game_date:
                # Check specific game
                game_time = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S')
                game_time_ast = convert_to_ast(game_time)
                
                # Determine game type based on day of week
                weekday = game_time_ast.weekday()  # Monday = 0, Sunday = 6
                
                if weekday == 3:  # Thursday
                    deadline_info = deadlines.get('thursday_night')
                    if deadline_info and deadline_info.get('deadline'):
                        return now < deadline_info['deadline']
                elif weekday == 4:  # Friday
                    friday_deadlines = deadlines.get('friday_games', [])
                    for deadline_info in friday_deadlines:
                        if deadline_info and deadline_info.get('deadline'):
                            # Find the deadline for this specific Friday game
                            game_deadline = deadline_info['deadline']
                            if abs((game_deadline + timedelta(minutes=30) - game_time_ast).total_seconds()) < 3600:  # Within 1 hour
                                return now < game_deadline
                    # If no specific Friday deadline found, default to allowing picks
                    return True
                elif weekday == 5:  # Saturday
                    saturday_deadlines = deadlines.get('saturday_games', [])
                    for deadline_info in saturday_deadlines:
                        if deadline_info and deadline_info.get('deadline'):
                            # Find the deadline for this specific Saturday game
                            game_deadline = deadline_info['deadline']
                            if abs((game_deadline + timedelta(minutes=30) - game_time_ast).total_seconds()) < 3600:  # Within 1 hour
                                return now < game_deadline
                    # If no specific Saturday deadline found, default to allowing picks
                    return True
                elif weekday == 0:  # Monday - uses same deadline as Sunday games
                    deadline_info = deadlines.get('monday_night')  # This uses Sunday deadline
                    if deadline_info and deadline_info.get('deadline'):
                        return now < deadline_info['deadline']
                else:  # Sunday and other days (assume Sunday deadline)
                    deadline_info = deadlines.get('sunday_games')
                    if deadline_info and deadline_info.get('deadline'):
                        return now < deadline_info['deadline']
            
            # If no specific game date, check if any deadline is still open
            for key, deadline_info in deadlines.items():
                if key in ['friday_games', 'saturday_games']:
                    # Handle list of deadlines for Friday/Saturday
                    if isinstance(deadline_info, list):
                        for info in deadline_info:
                            if info and info.get('deadline') and now < info['deadline']:
                                return True
                else:
                    # Handle single deadline
                    if deadline_info and deadline_info.get('deadline'):
                        if now < deadline_info['deadline']:
                            return True
            
            return False
            
        except Exception as e:
            print(f"Error checking pick availability: {e}")
            return True  # Default to allowing picks if error occurs
    
    def get_deadline_summary(self, week: int, year: int) -> Dict[str, Any]:
        """Get a user-friendly summary of deadlines with hours remaining"""
        try:
            deadlines = self.get_week_deadlines(week, year)
            now = datetime.now(self.ast_tz)
            
            summary = {
                'thursday': None,
                'friday': None,
                'saturday': None,
                'sunday': None,
                'monday': None,
                'next_deadline': None,
                'all_deadlines_passed': True
            }
            
            for key, deadline_info in deadlines.items():
                if key in ['friday_games', 'saturday_games']:
                    # Handle list of deadlines for Friday/Saturday
                    if isinstance(deadline_info, list) and deadline_info:
                        game_summaries = []
                        for info in deadline_info:
                            if info and info.get('deadline'):
                                deadline = info['deadline']
                                hours_remaining = (deadline - now).total_seconds() / 3600
                                
                                game_summary = {
                                    'deadline': deadline,
                                    'hours_remaining': hours_remaining,
                                    'passed': hours_remaining <= 0,
                                    'matchup': info.get('matchup', ''),
                                    'formatted_time': deadline.strftime('%A %-I:%M %p AST'),
                                    'urgency': 'critical' if 0 < hours_remaining <= 2 else 'warning' if 0 < hours_remaining <= 24 else 'normal'
                                }
                                game_summaries.append(game_summary)
                                
                                if hours_remaining > 0:
                                    summary['all_deadlines_passed'] = False
                                    if not summary['next_deadline'] or hours_remaining < summary['next_deadline']['hours_remaining']:
                                        summary['next_deadline'] = game_summary.copy()
                                        summary['next_deadline']['type'] = key
                        
                        if key == 'friday_games':
                            summary['friday'] = game_summaries
                        elif key == 'saturday_games':
                            summary['saturday'] = game_summaries
                            
                elif deadline_info and deadline_info.get('deadline'):
                    # Handle single deadline
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
                'friday': None,
                'saturday': None,
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
            
            # Import locally to avoid circular imports
            from deadline_override_manager import DeadlineOverrideManager
            override_manager = DeadlineOverrideManager()
            
            # Check for user-specific or global overrides
            for deadline_type in ['thursday', 'friday', 'saturday', 'sunday', 'monday']:
                if deadline_type in ['friday', 'saturday']:
                    # Handle list of deadlines for Friday/Saturday
                    game_list = base_summary.get(deadline_type, [])
                    if isinstance(game_list, list):
                        for i, game_info in enumerate(game_list):
                            if game_info:
                                original_deadline = game_info['deadline']
                                
                                # Map deadline types to database format
                                db_type = deadline_type
                                
                                # Get effective deadline (considering overrides)
                                effective_deadline = override_manager.get_user_deadline(
                                    week, year, db_type, user_id, original_deadline
                                )
                                
                                if effective_deadline != original_deadline:
                                    # Update with override deadline
                                    now = datetime.now(self.ast_tz)
                                    hours_remaining = (effective_deadline - now).total_seconds() / 3600
                                    
                                    base_summary[deadline_type][i].update({
                                        'deadline': effective_deadline,
                                        'hours_remaining': hours_remaining,
                                        'passed': hours_remaining <= 0,
                                        'formatted_time': effective_deadline.strftime('%A %-I:%M %p AST'),
                                        'urgency': 'critical' if 0 < hours_remaining <= 2 else 'warning' if 0 < hours_remaining <= 24 else 'normal',
                                        'is_override': True
                                    })
                elif base_summary[deadline_type]:
                    # Handle single deadline
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
