"""
BallDontLie NFL API Service
Real-time NFL data fetching and game updates
"""
import requests
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# BallDontLie NFL API configuration
BALLDONTLIE_BASE = "https://api.balldontlie.io/nfl/v1"
API_KEY = "900cc1d2-bf47-4ff8-a88c-92000ddeaa5e"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_season_schedule(year: int = 2025) -> List[Dict]:
    """Get complete season schedule from BallDontLie"""
    try:
        all_games = []
        
        # BallDontLie NFL API uses specific season parameter
        for week in range(1, 19):
            week_games = get_week_games(week, year)
            all_games.extend(week_games)
            import time
            time.sleep(0.1)  # Respect API limits
            
        return all_games
        
    except Exception as e:
        logger.error(f"Error fetching season schedule for {year}: {e}")
        return []

def get_week_games(week: int, year: int = 2025) -> List[Dict]:
    """Get games for specific week from BallDontLie"""
    try:
        url = f"{BALLDONTLIE_BASE}/games"
        
        # Ensure we're requesting the correct year
        params = {
            'season': year,          # Explicitly set the season year
            'season_type': 'regular', # Regular season games
            'week': week,
            'per_page': 100
        }
        
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        games = data.get('data', [])
        
        logger.info(f"BallDontLie API returned {len(games)} games for Week {week}, {year}")
        
        return normalize_games(games, week, year)
        
    except Exception as e:
        logger.error(f"Error fetching week {week} games for {year}: {e}")
        return []

def get_live_scores(week: int, year: int = 2025) -> List[Dict]:
    """Get live scores from BallDontLie"""
    return get_week_games(week, year)

def get_teams() -> List[Dict]:
    """Get all NFL teams from BallDontLie"""
    try:
        url = f"{BALLDONTLIE_BASE}/teams"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return data.get('data', [])
        
    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        return []

def normalize_games(games_data: List[Dict], week: int, year: int) -> List[Dict]:
    """Normalize BallDontLie game data"""
    normalized = []
    
    for game in games_data:
        try:
            # Parse game date
            game_date_str = game.get('date')
            if game_date_str:
                game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
            else:
                continue
            
            # Teams
            visitor_team = game.get('visitor_team', {})
            home_team = game.get('home_team', {})
            
            away_team = visitor_team.get('abbreviation')
            home_team_abbr = home_team.get('abbreviation')
            
            # Scores
            away_score = game.get('visitor_team_score')
            home_score = game.get('home_team_score')
            
            # Game status
            status = game.get('status', '')
            game_status = normalize_status(status)
            is_final = status.lower() in ['final', 'final/ot']
            
            # Determine game type
            weekday = game_date.weekday()
            hour = game_date.hour
            is_thursday = weekday == 3
            is_monday = weekday == 0
            is_sunday_night = weekday == 6 and hour >= 19
            
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
                'quarter': game.get('period'),
                'time_remaining': game.get('time'),
                'tv_network': None,
                'stadium': None,
                'weather': None
            }
            
            normalized.append(normalized_game)
            
        except Exception as e:
            logger.error(f"Error normalizing game: {e}")
            continue
    
    return normalized

def normalize_status(status: str) -> str:
    """Normalize game status"""
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

