"""
NFL API Service using BallDontLie API (Free)
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
        # ESPN as primary (free and reliable for NFL)
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        
        # NFL.com API (free, no auth required)
        self.nfl_base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        
        self.current_season = 2025
        
    def get_season_schedule(self, year: int = 2025) -> List[Dict]:
        """Get complete season schedule"""
        try:
            # Use ESPN as primary for NFL (BallDontLie is NBA-focused)
            schedule = self._get_espn_schedule(year)
            if schedule:
                return schedule
            
            # Try alternative NFL sources
            return self._get_nfl_schedule_fallback(year)
            
        except Exception as e:
            logger.error(f"Error fetching season schedule: {e}")
            return []
    
    def get_week_games(self, week: int, year: int = 2025) -> List[Dict]:
        """Get games for specific week"""
        try:
            # ESPN is most reliable for NFL
            games = self._get_espn_week(week, year)
            if games:
                return games
            
            # Try NFL.com backup
            return self._get_nfl_week_fallback(week, year)
            
        except Exception as e:
            logger.error(f"Error fetching week {week} games: {e}")
            return []
    
    def get_live_scores(self, week: int, year: int = 2025) -> List[Dict]:
        """Get live scores and game updates"""
        try:
            # ESPN for live NFL scores
            scores = self._get_espn_scores(week, year)
            if scores:
                return scores
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching live scores: {e}")
            return []
    
    def _get_espn_week(self, week: int, year: int) -> List[Dict]:
        """Get week games from ESPN API"""
        try:
            url = f"{self.espn_base}/scoreboard"
            params = {
                'seasontype': 2,  # Regular season
                'week': week,
                'year': year
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._normalize_espn_games(data.get('events', []), week, year)
            
        except Exception as e:
            logger.error(f"ESPN week error: {e}")
            return []
    
    def _get_espn_schedule(self, year: int) -> List[Dict]:
        """Get full season schedule from ESPN API"""
        try:
            all_games = []
            
            # Fetch all 18 weeks
            for week in range(1, 19):
                week_games = self._get_espn_week(week, year)
                all_games.extend(week_games)
                # Small delay to be respectful to free API
                import time
                time.sleep(0.1)
                
            return all_games
            
        except Exception as e:
            logger.error(f"ESPN schedule error: {e}")
            return []
    
    def _get_espn_scores(self, week: int, year: int) -> List[Dict]:
        """Get live scores from ESPN"""
        return self._get_espn_week(week, year)
    
    def _get_nfl_schedule_fallback(self, year: int) -> List[Dict]:
        """Fallback schedule method"""
        try:
            # Alternative: Use a different endpoint or manual data
            all_games = []
            for week in range(1, 19):
                week_games = self._get_nfl_week_fallback(week, year)
                all_games.extend(week_games)
            return all_games
        except Exception as e:
            logger.error(f"NFL fallback schedule error: {e}")
            return []
    
    def _get_nfl_week_fallback(self, week: int, year: int) -> List[Dict]:
        """Fallback week games method"""
        try:
            # Could use alternative NFL endpoints here
            # For now, return empty to let ESPN handle it
            return []
        except Exception as e:
            logger.error(f"NFL fallback week error: {e}")
            return []
    
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
                        home_score = int(score) if score and str(score).isdigit() else None
                    else:
                        away_team = team_abbr
                        away_score = int(score) if score and str(score).isdigit() else None
                
                # Parse game date
                game_date_str = event.get('date')
                if game_date_str:
                    game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                else:
                    game_date = None
                
                # Determine game type based on day and time
                if game_date:
                    weekday = game_date.weekday()
                    hour = game_date.hour
                    is_thursday = weekday == 3  # Thursday
                    is_monday = weekday == 0    # Monday
                    is_sunday_night = weekday == 6 and hour >= 19  # Sunday night
                else:
                    is_thursday = is_monday = is_sunday_night = False
                
                # Game status
                status = competition.get('status', {})
                status_type = status.get('type', {})
                game_status = self._normalize_espn_status(status_type.get('name', ''))
                is_final = status_type.get('completed', False)
                
                # Get additional info
                broadcasts = competition.get('broadcasts', [])
                tv_network = broadcasts[0].get('media', {}).get('shortName') if broadcasts else None
                
                venue = competition.get('venue', {})
                stadium = venue.get('fullName')
                
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
                    'tv_network': tv_network,
                    'stadium': stadium,
                    'weather': None
                }
                
                normalized.append(normalized_game)
                
            except Exception as e:
                logger.error(f"Error normalizing ESPN game: {e}")
                continue
        
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
