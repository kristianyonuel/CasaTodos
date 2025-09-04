"""
NFL API Service using SportsDataIO and ESPN APIs
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
        # Primary API: SportsDataIO (requires subscription)
        self.sportsdata_key = "YOUR_SPORTSDATA_API_KEY"  # Replace with actual key
        self.sportsdata_base = "https://api.sportsdata.io/v3/nfl"
        
        # Backup API: ESPN (free)
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        
        # Current season
        self.current_season = 2025
        
    def get_season_schedule(self, year: int = 2025) -> List[Dict]:
        """Get complete season schedule"""
        try:
            # Try SportsDataIO first
            schedule = self._get_sportsdata_schedule(year)
            if schedule:
                return schedule
            
            # Fallback to ESPN
            return self._get_espn_schedule(year)
            
        except Exception as e:
            logger.error(f"Error fetching season schedule: {e}")
            return []
    
    def get_week_games(self, week: int, year: int = 2025) -> List[Dict]:
        """Get games for specific week"""
        try:
            # Try SportsDataIO first
            games = self._get_sportsdata_week(week, year)
            if games:
                return games
            
            # Fallback to ESPN
            return self._get_espn_week(week, year)
            
        except Exception as e:
            logger.error(f"Error fetching week {week} games: {e}")
            return []
    
    def get_live_scores(self, week: int, year: int = 2025) -> List[Dict]:
        """Get live scores and game updates"""
        try:
            # Try SportsDataIO first for live data
            scores = self._get_sportsdata_scores(week, year)
            if scores:
                return scores
            
            # Fallback to ESPN
            return self._get_espn_scores(week, year)
            
        except Exception as e:
            logger.error(f"Error fetching live scores: {e}")
            return []
    
    def _get_sportsdata_schedule(self, year: int) -> List[Dict]:
        """Get schedule from SportsDataIO"""
        if not self.sportsdata_key or self.sportsdata_key == "YOUR_SPORTSDATA_API_KEY":
            return []
        
        try:
            url = f"{self.sportsdata_base}/scores/json/Schedules/{year}REG"
            headers = {"Ocp-Apim-Subscription-Key": self.sportsdata_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            games_data = response.json()
            return self._normalize_sportsdata_games(games_data)
            
        except Exception as e:
            logger.error(f"SportsDataIO schedule error: {e}")
            return []
    
    def _get_sportsdata_week(self, week: int, year: int) -> List[Dict]:
        """Get week games from SportsDataIO"""
        if not self.sportsdata_key or self.sportsdata_key == "YOUR_SPORTSDATA_API_KEY":
            return []
        
        try:
            url = f"{self.sportsdata_base}/scores/json/ScoresByWeek/{year}REG/{week}"
            headers = {"Ocp-Apim-Subscription-Key": self.sportsdata_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            games_data = response.json()
            return self._normalize_sportsdata_games(games_data)
            
        except Exception as e:
            logger.error(f"SportsDataIO week error: {e}")
            return []
    
    def _get_sportsdata_scores(self, week: int, year: int) -> List[Dict]:
        """Get live scores from SportsDataIO"""
        return self._get_sportsdata_week(week, year)
    
    def _get_espn_schedule(self, year: int) -> List[Dict]:
        """Get schedule from ESPN API"""
        try:
            all_games = []
            
            # ESPN doesn't have full season endpoint, so fetch week by week
            for week in range(1, 19):
                week_games = self._get_espn_week(week, year)
                all_games.extend(week_games)
                
            return all_games
            
        except Exception as e:
            logger.error(f"ESPN schedule error: {e}")
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
    
    def _get_espn_scores(self, week: int, year: int) -> List[Dict]:
        """Get live scores from ESPN"""
        return self._get_espn_week(week, year)
    
    def _normalize_sportsdata_games(self, games_data: List[Dict]) -> List[Dict]:
        """Normalize SportsDataIO game data"""
        normalized = []
        
        for game in games_data:
            try:
                # Parse game date
                game_date = datetime.fromisoformat(game.get('DateTime', '').replace('Z', '+00:00'))
                
                # Determine game type
                weekday = game_date.weekday()
                hour = game_date.hour
                
                is_thursday = weekday == 3 and hour >= 18
                is_monday = weekday == 0 and hour >= 18
                is_sunday_night = weekday == 6 and hour >= 18
                
                normalized_game = {
                    'api_game_id': game.get('GameKey'),
                    'week': game.get('Week'),
                    'year': game.get('Season'),
                    'away_team': game.get('AwayTeam'),
                    'home_team': game.get('HomeTeam'),
                    'game_date': game_date,
                    'is_thursday_night': is_thursday,
                    'is_monday_night': is_monday,
                    'is_sunday_night': is_sunday_night,
                    'away_score': game.get('AwayScore'),
                    'home_score': game.get('HomeScore'),
                    'game_status': self._normalize_game_status(game.get('Status')),
                    'is_final': game.get('IsFinal', False),
                    'quarter': game.get('Quarter'),
                    'time_remaining': game.get('TimeRemainingMinutes'),
                    'tv_network': game.get('Channel'),
                    'stadium': game.get('Stadium', {}).get('Name'),
                    'weather': game.get('Weather', {}).get('Description')
                }
                
                normalized.append(normalized_game)
                
            except Exception as e:
                logger.error(f"Error normalizing SportsDataIO game: {e}")
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
                    'stadium': competition.get('venue', {}).get('fullName'),
                    'weather': None  # ESPN doesn't always provide weather
                }
                
                normalized.append(normalized_game)
                
            except Exception as e:
                logger.error(f"Error normalizing ESPN game: {e}")
                continue
        
        return normalized
    
    def _normalize_game_status(self, status: str) -> str:
        """Normalize game status from SportsDataIO"""
        status_map = {
            'Scheduled': 'scheduled',
            'InProgress': 'in_progress',
            'Final': 'final',
            'Postponed': 'postponed',
            'Canceled': 'canceled'
        }
        return status_map.get(status, 'scheduled')
    
    def _normalize_espn_status(self, status: str) -> str:
        """Normalize game status from ESPN"""
        status_map = {
            'STATUS_SCHEDULED': 'scheduled',
            'STATUS_IN_PROGRESS': 'in_progress',
            'STATUS_FINAL': 'final',
            'STATUS_POSTPONED': 'postponed',
            'STATUS_CANCELED': 'canceled'
        }
        return status_map.get(status, 'scheduled')

# Global API service instance
nfl_api = NFLAPIService()
