"""
NFL API Service using free APIs: BallDontLie and MySportsFeeds
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
        # BallDontLie API (Free)
        self.balldontlie_base = "https://api.balldontlie.io/v1/nfl"
        
        # MySportsFeeds API (Free tier)
        self.msf_base = "https://api.mysportsfeeds.com/v2.1/pull/nfl"
        self.msf_username = "kristiany"  # Replace with your username
        self.msf_password = "Genesis123!@#"  # Replace with your password
        
        # ESPN as backup (free)
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        
        self.current_season = 2025
        
    def get_season_schedule(self, year: int = 2025) -> List[Dict]:
        """Get complete season schedule"""
        try:
            # Try MySportsFeeds first
            schedule = self._get_msf_schedule(year)
            if schedule:
                return schedule
            
            # Try BallDontLie
            schedule = self._get_balldontlie_schedule(year)
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
            # Try MySportsFeeds first
            games = self._get_msf_week(week, year)
            if games:
                return games
            
            # Try BallDontLie
            games = self._get_balldontlie_week(week, year)
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
            # Try MySportsFeeds for live data
            scores = self._get_msf_scores(week, year)
            if scores:
                return scores
            
            # Try BallDontLie
            scores = self._get_balldontlie_scores(week, year)
            if scores:
                return scores
            
            # Fallback to ESPN
            return self._get_espn_scores(week, year)
            
        except Exception as e:
            logger.error(f"Error fetching live scores: {e}")
            return []
    
    def _get_msf_schedule(self, year: int) -> List[Dict]:
        """Get schedule from MySportsFeeds"""
        if not self._has_msf_credentials():
            return []
        
        try:
            url = f"{self.msf_base}/{year}-regular/games.json"
            auth = (self.msf_username, self.msf_password)
            
            response = requests.get(url, auth=auth, timeout=15)
            if response.status_code == 401:
                logger.warning("MySportsFeeds authentication failed")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            return self._normalize_msf_games(data.get('games', []))
            
        except Exception as e:
            logger.error(f"MySportsFeeds schedule error: {e}")
            return []
    
    def _get_msf_week(self, week: int, year: int) -> List[Dict]:
        """Get week games from MySportsFeeds"""
        if not self._has_msf_credentials():
            return []
        
        try:
            url = f"{self.msf_base}/{year}-regular/week/{week}/games.json"
            auth = (self.msf_username, self.msf_password)
            
            response = requests.get(url, auth=auth, timeout=15)
            if response.status_code == 401:
                return []
            
            response.raise_for_status()
            data = response.json()
            
            return self._normalize_msf_games(data.get('games', []))
            
        except Exception as e:
            logger.error(f"MySportsFeeds week error: {e}")
            return []
    
    def _get_msf_scores(self, week: int, year: int) -> List[Dict]:
        """Get live scores from MySportsFeeds"""
        return self._get_msf_week(week, year)
    
    def _get_balldontlie_schedule(self, year: int) -> List[Dict]:
        """Get schedule from BallDontLie"""
        try:
            all_games = []
            
            # BallDontLie doesn't have full season endpoint, fetch week by week
            for week in range(1, 19):
                week_games = self._get_balldontlie_week(week, year)
                all_games.extend(week_games)
                
            return all_games
            
        except Exception as e:
            logger.error(f"BallDontLie schedule error: {e}")
            return []
    
    def _get_balldontlie_week(self, week: int, year: int) -> List[Dict]:
        """Get week games from BallDontLie"""
        try:
            url = f"{self.balldontlie_base}/games"
            params = {
                'season': year,
                'week': week,
                'per_page': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._normalize_balldontlie_games(data.get('data', []), week, year)
            
        except Exception as e:
            logger.error(f"BallDontLie week error: {e}")
            return []
    
    def _get_balldontlie_scores(self, week: int, year: int) -> List[Dict]:
        """Get live scores from BallDontLie"""
        return self._get_balldontlie_week(week, year)
    
    def _get_espn_week(self, week: int, year: int) -> List[Dict]:
        """Get week games from ESPN API (backup)"""
        try:
            url = f"{self.espn_base}/scoreboard"
            params = {
                'seasontype': 2,
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
        """Get schedule from ESPN API"""
        try:
            all_games = []
            for week in range(1, 19):
                week_games = self._get_espn_week(week, year)
                all_games.extend(week_games)
            return all_games
        except Exception as e:
            logger.error(f"ESPN schedule error: {e}")
            return []
    
    def _get_espn_scores(self, week: int, year: int) -> List[Dict]:
        """Get live scores from ESPN"""
        return self._get_espn_week(week, year)
    
    def _normalize_msf_games(self, games_data: List[Dict]) -> List[Dict]:
        """Normalize MySportsFeeds game data"""
        normalized = []
        
        for game in games_data:
            try:
                schedule = game.get('schedule', {})
                score = game.get('score', {})
                
                # Parse game date
                game_date_str = schedule.get('startTime')
                if game_date_str:
                    game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                else:
                    continue
                
                # Teams
                away_team = schedule.get('awayTeam', {}).get('abbreviation')
                home_team = schedule.get('homeTeam', {}).get('abbreviation')
                
                # Scores
                away_score = score.get('awayScoreTotal')
                home_score = score.get('homeScoreTotal')
                
                # Game status
                game_status = self._normalize_msf_status(schedule.get('playedStatus'))
                is_final = game_status == 'final'
                
                # Determine game type
                weekday = game_date.weekday()
                hour = game_date.hour
                
                normalized_game = {
                    'api_game_id': game.get('schedule', {}).get('id'),
                    'week': schedule.get('week'),
                    'year': schedule.get('season'),
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
                    'quarter': score.get('currentPeriod'),
                    'time_remaining': score.get('currentPeriodTimeRemaining'),
                    'tv_network': None,
                    'stadium': schedule.get('venue', {}).get('name')
                }
                
                normalized.append(normalized_game)
                
            except Exception as e:
                logger.error(f"Error normalizing MySportsFeeds game: {e}")
                continue
        
        return normalized
    
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
