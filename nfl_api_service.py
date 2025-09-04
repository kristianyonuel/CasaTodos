"""
NFL API Service using BallDontLie NFL API (Free)
Real-time NFL data fetching and game updates
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class NFLAPIService:
    def __init__(self):
        # BallDontLie NFL API (Free with API key)
        self.balldontlie_base = "https://api.balldontlie.io/nfl/v1"
        self.api_key = "900cc1d2-bf47-4ff8-a88c-92000ddeaa5e"
        
        self.current_season = 2025
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def get_season_schedule(self, year: int = 2025) -> List[Dict]:
        """Get complete season schedule"""
        try:
            schedule = self._get_balldontlie_schedule(year)
            if schedule:
                return schedule
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching season schedule: {e}")
            return []
    
    def get_week_games(self, week: int, year: int = 2025) -> List[Dict]:
        """Get games for specific week"""
        try:
            games = self._get_balldontlie_week(week, year)
            if games:
                return games
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching week {week} games: {e}")
            return []
    
    def get_live_scores(self, week: int, year: int = 2025) -> List[Dict]:
        """Get live scores and game updates"""
        try:
            scores = self._get_balldontlie_scores(week, year)
            if scores:
                return scores
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching live scores: {e}")
            return []
    
    def _get_balldontlie_schedule(self, year: int) -> List[Dict]:
        """Get full season schedule from BallDontLie NFL API"""
        try:
            all_games = []
            
            # Get all 18 weeks
            for week in range(1, 19):
                week_games = self._get_balldontlie_week(week, year)
                all_games.extend(week_games)
                # Small delay to respect API limits
                import time
                time.sleep(0.1)
                
            return all_games
            
        except Exception as e:
            logger.error(f"BallDontLie schedule error: {e}")
            return []
    
    def _get_balldontlie_week(self, week: int, year: int) -> List[Dict]:
        """Get week games from BallDontLie NFL API"""
        try:
            url = f"{self.balldontlie_base}/games"
            params = {
                'season': year,
                'week': week,
                'per_page': 100  # Get all games for the week
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return self._normalize_balldontlie_games(data.get('data', []), week, year)
            
        except Exception as e:
            logger.error(f"BallDontLie week error: {e}")
            return []
    
    def _get_balldontlie_scores(self, week: int, year: int) -> List[Dict]:
        """Get live scores from BallDontLie NFL API"""
        try:
            # Use the same games endpoint but focus on scores
            url = f"{self.balldontlie_base}/games"
            params = {
                'season': year,
                'week': week,
                'per_page': 100
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return self._normalize_balldontlie_games(data.get('data', []), week, year)
            
        except Exception as e:
            logger.error(f"BallDontLie scores error: {e}")
            return []
    
    def _normalize_balldontlie_games(self, games_data: List[Dict], week: int, year: int) -> List[Dict]:
        """Normalize BallDontLie NFL game data"""
        normalized = []
        
        for game in games_data:
            try:
                # Parse game date
                game_date_str = game.get('date')
                if game_date_str:
                    game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                else:
                    continue
                
                # Teams - BallDontLie NFL API structure
                visitor_team = game.get('visitor_team', {})
                home_team = game.get('home_team', {})
                
                away_team = visitor_team.get('abbreviation')
                home_team_abbr = home_team.get('abbreviation')
                
                # Scores
                away_score = game.get('visitor_team_score')
                home_score = game.get('home_team_score')
                
                # Game status
                status = game.get('status', '')
                game_status = self._normalize_balldontlie_status(status)
                is_final = status.lower() in ['final', 'final/ot']
                
                # Determine game type based on day and time
                if game_date:
                    weekday = game_date.weekday()
                    hour = game_date.hour
                    is_thursday = weekday == 3  # Thursday
                    is_monday = weekday == 0    # Monday  
                    is_sunday_night = weekday == 6 and hour >= 19  # Sunday night
                else:
                    is_thursday = is_monday = is_sunday_night = False
                
                # Additional game info
                period = game.get('period')
                time_remaining = game.get('time')
                
                normalized_game = {
                    'api_game_id': game.get('id'),
                    'week': week,
                    'year': year,
                    'away_team': away_team,
                    'home_team': home_team_abbr,
                    'game_date': game_date,
                    'is_thursday_night': is_thursday,
                    'is_monday_night': is_monday,
                    'is_sunday_night': is_sunday_night,
                    'away_score': int(away_score) if away_score is not None else None,
                    'home_score': int(home_score) if home_score is not None else None,
                    'game_status': game_status,
                    'is_final': is_final,
                    'quarter': period,
                    'time_remaining': time_remaining,
                    'tv_network': None,  # BallDontLie may not provide this
                    'stadium': None,     # BallDontLie may not provide this
                    'weather': None
                }
                
                normalized.append(normalized_game)
                
            except Exception as e:
                logger.error(f"Error normalizing BallDontLie game: {e}")
                continue
        
        return normalized
    
    def _normalize_balldontlie_status(self, status: str) -> str:
        """Normalize BallDontLie game status"""
        status_lower = status.lower()
        
        status_map = {
            'scheduled': 'scheduled',
            'pregame': 'scheduled',
            'in progress': 'in_progress',
            'inprogress': 'in_progress',
            'halftime': 'in_progress',
            'final': 'final',
            'final/ot': 'final',
            'postponed': 'postponed',
            'delayed': 'delayed',
            'suspended': 'suspended'
        }
        
        return status_map.get(status_lower, 'scheduled')

# Global API service instance
nfl_api = NFLAPIService()
        return normalized
    
    def _normalize_espn_status(self, status: str) -> str:
        """Normalize ESPN game status"""
        status_map = {
            'STATUS_SCHEDULED': 'scheduled',
            'STATUS_IN_PROGRESS': 'in_progress', 
            'STATUS_HALFTIME': 'in_progress',
            'STATUS_FINAL': 'final',
            'STATUS_FINAL_OVERTIME': 'final',
            'STATUS_POSTPONED': 'postponed',
            'STATUS_DELAYED': 'delayed',
            'STATUS_SUSPENDED': 'suspended'
        }
        return status_map.get(status, 'scheduled')

# Global API service instance
nfl_api = NFLAPIService()

    # The following methods were incorrectly indented; fix by unindenting them to be inside the class.

class NFLAPIService:
    # ... previous methods ...

    def _normalize_balldontlie_games(self, games_data: List[Dict], week: int, year: int) -> List[Dict]:
        """Normalize BallDontLie game data"""
        normalized = []
        
        for game in games_data:
            try:
                # Parse game date
                game_date_str = game.get('date')
                if game_date_str:
                    game_date = datetime.fromisoformat(game_date_str)
                else:
                    continue
                
                # Teams
                away_team = game.get('visitor_team', {}).get('abbreviation')
                home_team = game.get('home_team', {}).get('abbreviation')
                
                # Scores
                away_score = game.get('visitor_team_score')
                home_score = game.get('home_team_score')
                
                # Game status
                game_status = self._normalize_balldontlie_status(game.get('status'))
                is_final = game.get('status') == 'Final'
                
                # Determine game type
                weekday = game_date.weekday()
                hour = game_date.hour
                
                normalized_game = {
                    'api_game_id': game.get('id'),
                    'week': week,
                    'year': year,
                    'away_team': away_team,
                    'home_team': home_team,
                    'game_date': game_date,
                    'is_thursday_night': weekday == 3 and hour >= 18,
                    'is_monday_night': weekday == 0 and hour >= 18,
                    'is_sunday_night': weekday == 6 and hour >= 18,
                    'away_score': away_score,
                    'home_score': home_score,
                    'game_status': game_status,
                    'is_final': is_final,
                    'quarter': game.get('period'),
                    'time_remaining': game.get('time'),
                    'tv_network': None,
                    'stadium': None
                }
                
                normalized.append(normalized_game)
                
            except Exception as e:
                logger.error(f"Error normalizing BallDontLie game: {e}")
                continue
        
        return normalized

    def _normalize_espn_games(self, games_data: List[Dict], week: int, year: int) -> List[Dict]:
        """Normalize ESPN game data"""
        normalized = []
        
        for event in games_data:
            try:
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) != 2:
                    continue
                
                # Find home/away teams
                home_team = away_team = None
                home_score = away_score = None
                
                for comp in competitors:
                    team_abbr = comp.get('team', {}).get('abbreviation')
                    score = comp.get('score')
                    
                    if comp.get('homeAway') == 'home':
                        home_team = team_abbr
                        home_score = int(score) if score and score.isdigit() else None
                    else:
                        away_team = team_abbr
                        away_score = int(score) if score and score.isdigit() else None
                
                # Parse game date
                game_date_str = event.get('date')
                if game_date_str:
                    game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                else:
                    game_date = None
                
                # Determine game type
                if game_date:
                    weekday = game_date.weekday()
                    hour = game_date.hour
                    is_thursday = weekday == 3 and hour >= 18
                    is_monday = weekday == 0 and hour >= 18
                    is_sunday_night = weekday == 6 and hour >= 18
                else:
                    is_thursday = is_monday = is_sunday_night = False
                
                # Game status
                status = competition.get('status', {})
                game_status = self._normalize_espn_status(status.get('type', {}).get('name', ''))
                is_final = status.get('type', {}).get('completed', False)
                
                normalized_game = {
                    'api_game_id': event.get('id'),
                    'week': week,
                    'year': year,
                    'away_team': away_team,
                    'home_team': home_team,
                    'game_date': game_date,
                    'is_thursday_night': is_thursday,
                    'is_monday_night': is_monday,
                    'is_sunday_night': is_sunday_night,
                    'away_score': away_score,
                    'home_score': home_score,
                    'game_status': game_status,
                    'is_final': is_final,
                    'quarter': status.get('period'),
                    'time_remaining': status.get('displayClock'),
                    'tv_network': competition.get('broadcasts', [{}])[0].get('market', {}).get('media', {}).get('shortName'),
                    'stadium': competition.get('venue', {}).get('fullName')
                }
                
                normalized.append(normalized_game)
                
            except Exception as e:
                logger.error(f"Error normalizing ESPN game: {e}")
                continue
        
        return normalized

    def _has_msf_credentials(self) -> bool:
        """Check if MySportsFeeds credentials are configured"""
        return (self.msf_username != "YOUR_MSF_USERNAME" and 
                self.msf_password != "YOUR_MSF_PASSWORD" and
                self.msf_username and self.msf_password)

    def _normalize_msf_status(self, status: str) -> str:
        """Normalize MySportsFeeds game status"""
        status_map = {
            'UNPLAYED': 'scheduled',
            'LIVE': 'in_progress',
            'COMPLETED': 'final',
            'POSTPONED': 'postponed'
        }
        return status_map.get(status, 'scheduled')

    def _normalize_balldontlie_status(self, status: str) -> str:
        """Normalize BallDontLie game status"""
        status_map = {
            'Scheduled': 'scheduled',
            'InProgress': 'in_progress',
            'Final': 'final',
            'Postponed': 'postponed'
        }
        return status_map.get(status, 'scheduled')

    def _normalize_espn_status(self, status: str) -> str:
        """Normalize ESPN game status"""
        status_map = {
            'STATUS_SCHEDULED': 'scheduled',
            'STATUS_IN_PROGRESS': 'in_progress',
            'STATUS_FINAL': 'final',
            'STATUS_POSTPONED': 'postponed'
        }
        return status_map.get(status, 'scheduled')

# Global API service instance
nfl_api = NFLAPIService()
