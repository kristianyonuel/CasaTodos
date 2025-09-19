"""
ESPN API Service Module
Provides NFL game data and live scores from ESPN API
"""

import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ESPNAPIService:
    """Service for fetching NFL data from ESPN API"""
    
    def __init__(self):
        self.base_url = ("https://site.api.espn.com/apis/site/v2/sports/"
                         "football/nfl")
        self.headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36')
        }
        
    def get_week_games(self, week: int, year: int = 2025) -> List[Dict]:
        """Get games for a specific NFL week from ESPN"""
        try:
            # ESPN API endpoint for scoreboard
            url = f"{self.base_url}/scoreboard"
            
            # ESPN uses different week numbering for some endpoints
            # For now, get current week games
            params = {
                'seasontype': 2,  # Regular season
                'week': week,
                'year': year
            }
            
            response = requests.get(url, headers=self.headers, 
                                   params=params, timeout=15, verify=False)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            normalized_games = []
            for event in events:
                try:
                    game_data = self._normalize_espn_game(event, week, year)
                    if game_data:
                        normalized_games.append(game_data)
                except Exception as e:
                    logger.error(f"Error normalizing ESPN game data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(normalized_games)} games from ESPN "
                       f"for Week {week}, {year}")
            return normalized_games
            
        except Exception as e:
            logger.error(f"Error fetching games from ESPN for "
                        f"Week {week}: {e}")
            return []
    
    def get_current_week_games(self, year: int = 2025) -> List[Dict]:
        """Get current week games from ESPN scoreboard"""
        try:
            url = f"{self.base_url}/scoreboard"
            
            response = requests.get(url, headers=self.headers, timeout=15, 
                                   verify=False)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            # Try to determine week from the games
            week = self._determine_week_from_games(events, year)
            
            normalized_games = []
            for event in events:
                try:
                    game_data = self._normalize_espn_game(event, week, year)
                    if game_data:
                        normalized_games.append(game_data)
                except Exception as e:
                    logger.error(f"Error normalizing ESPN game data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(normalized_games)} current week games from ESPN")
            return normalized_games
            
        except Exception as e:
            logger.error(f"Error fetching current week games from ESPN: {e}")
            return []
    
    def _normalize_espn_game(self, event: Dict, week: int, year: int) -> Optional[Dict]:
        """Normalize ESPN game data to our format"""
        try:
            # Get basic game info
            game_id = event.get('id')
            date_str = event.get('date')
            
            # Parse game date
            if date_str:
                game_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return None
            
            # Get teams
            competitions = event.get('competitions', [])
            if not competitions:
                return None
                
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) != 2:
                return None
            
            # ESPN typically has home team first, away team second
            home_team_data = next((c for c in competitors if c.get('homeAway') == 'home'), None)
            away_team_data = next((c for c in competitors if c.get('homeAway') == 'away'), None)
            
            if not home_team_data or not away_team_data:
                return None
            
            # Get team abbreviations
            home_team = home_team_data.get('team', {}).get('abbreviation')
            away_team = away_team_data.get('team', {}).get('abbreviation')
            
            # Get scores
            home_score = int(home_team_data.get('score', 0))
            away_score = int(away_team_data.get('score', 0))
            
            # Get game status
            status = competition.get('status', {})
            status_type = status.get('type', {})
            status_name = status_type.get('name', '').lower()
            status_description = status_type.get('description', '').lower()
            completed = status_type.get('completed', False)
            
            # Determine if game is final - improved logic to handle ESPN's different status formats
            is_final = (
                completed or
                status_name in ['final', 'final/ot', 'status_final'] or
                status_description == 'final' or
                'final' in status_name
            )
            
            # Get game status details
            game_status = status.get('type', {}).get('description', 'Scheduled')
            quarter = status.get('period', 0)
            clock = status.get('displayClock', '')
            
            # Determine game type based on day of week and time
            weekday = game_date.weekday()
            hour = game_date.hour
            
            is_thursday = weekday == 3
            is_monday = weekday == 0
            is_sunday_night = weekday == 6 and hour >= 19
            
            game_type = 'REG'
            if is_thursday:
                game_type = 'TNF'
            elif is_monday:
                game_type = 'MNF'
            elif is_sunday_night:
                game_type = 'SNF'
            
            return {
                'game_id': game_id,
                'away_team': away_team,
                'home_team': home_team,
                'away_score': away_score,
                'home_score': home_score,
                'game_date': game_date.isoformat(),
                'game_status': game_status,
                'is_final': is_final,
                'quarter': quarter,
                'time_remaining': clock,
                'week': week,
                'year': year,
                'game_type': game_type
            }
            
        except Exception as e:
            logger.error(f"Error normalizing ESPN game: {e}")
            return None
    
    def _determine_week_from_games(self, events: List[Dict], year: int) -> int:
        """Determine NFL week from game dates"""
        try:
            if not events:
                return 1
            
            # Get the earliest game date
            earliest_date = None
            for event in events:
                date_str = event.get('date')
                if date_str:
                    game_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    # Convert to naive datetime for comparison
                    game_date = game_date.replace(tzinfo=None)
                    if earliest_date is None or game_date < earliest_date:
                        earliest_date = game_date
            
            if earliest_date is None:
                return 1
            
            # NFL 2025 season starts around September 5-8
            season_start = datetime(year, 9, 5)
            
            if earliest_date < season_start:
                return 1
            
            # Calculate week number
            days_since_start = (earliest_date - season_start).days
            week = (days_since_start // 7) + 1
            
            return min(max(week, 1), 18)  # NFL has 18 weeks
            
        except Exception as e:
            logger.error(f"Error determining week from games: {e}")
            return 1

# Global ESPN service instance
espn_service = ESPNAPIService()

def get_espn_live_scores(week: int, year: int = 2025) -> List[Dict]:
    """Get live scores from ESPN API"""
    return espn_service.get_week_games(week, year)

def get_espn_current_week_games(year: int = 2025) -> List[Dict]:
    """Get current week games from ESPN"""
    return espn_service.get_current_week_games(year)

if __name__ == "__main__":
    # Test ESPN API
    service = ESPNAPIService()
    
    # Test current week games
    games = service.get_current_week_games()
    print(f"Found {len(games)} current week games:")
    
    for game in games[:3]:  # Show first 3 games
        print(f"  {game['away_team']} @ {game['home_team']} - Week {game['week']}")
        print(f"    Score: {game['away_score']}-{game['home_score']} ({game['game_status']})")
