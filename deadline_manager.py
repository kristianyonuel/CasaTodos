"""
NFL Game Deadline Management System
Handles dynamic deadlines based on actual game times and league rules
"""
from __future__ import annotations

import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.timezone_utils import convert_to_ast

class DeadlineManager:
    """Manages game submission deadlines based on NFL schedule"""
    
    def __init__(self):
        self.ast_tz = pytz.timezone('America/Puerto_Rico')
        
        # Default deadline offsets (minutes before game start)
        self.deadline_offsets = {
            'thursday_night': 30,    # 30 minutes before TNF
            'sunday_games': 60,      # 1 hour before first Sunday game  
            'monday_night': 30,      # 30 minutes before MNF
            'elimination': 10080     # 7 days (7 * 24 * 60) before Saturday
        }
    
    def get_week_deadlines(self, week: int, year: int) -> Dict[str, Dict]:
        """Get all deadlines for a specific week"""
        from database import get_db
        
        deadlines = {
            'thursday_night': None,
            'sunday_games': None, 
            'monday_night': None,
            'elimination': None
        }
        
        try:
            with get_db() as conn:
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

# Global instance
deadline_manager = DeadlineManager()
