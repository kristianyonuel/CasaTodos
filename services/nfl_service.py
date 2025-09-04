"""
NFL data service for fetching games and managing schedules
"""
import requests
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from models import NFLGame
from config import Config

logger = logging.getLogger(__name__)

class NFLService:
    def __init__(self):
        self.base_url = Config.ESPN_API_BASE
        self.timeout = Config.API_TIMEOUT
    
    def fetch_games_from_api(self, week: int, year: int) -> List[NFLGame]:
        """Fetch NFL games from ESPN API"""
        try:
            url = f"{self.base_url}/scoreboard"
            params = {'seasontype': 2, 'week': week, 'year': year}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            games = []
            for event in data.get('events', []):
                try:
                    game = self._parse_game_event(event, week, year)
                    if game:
                        games.append(game)
                except Exception as e:
                    logger.error(f"Error parsing game event: {e}")
                    continue
            
            logger.info(f"Fetched {len(games)} games for week {week}, year {year}")
            return games
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching games: {e}")
            return []
    
    def _parse_game_event(self, event: dict, week: int, year: int) -> Optional[NFLGame]:
        """Parse a single game event from ESPN API"""
        try:
            game_date_str = event['date']
            if game_date_str.endswith('Z'):
                game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
            else:
                game_date = datetime.fromisoformat(game_date_str)
            
            # Determine game type
            weekday = game_date.weekday()
            hour = game_date.hour
            
            is_monday_night = (weekday == 0 and hour >= 18)
            is_thursday_night = (weekday == 3 and hour >= 18)
            
            competitors = event['competitions'][0]['competitors']
            home_team = competitors[0]['team']['abbreviation']
            away_team = competitors[1]['team']['abbreviation']
            
            game = NFLGame(
                game_id=event['id'],
                week=week,
                year=year,
                home_team=home_team,
                away_team=away_team,
                game_date=game_date,
                is_monday_night=is_monday_night,
                is_thursday_night=is_thursday_night,
                is_final=event['status']['type']['completed']
            )
            
            if game.is_final:
                game.home_score = int(competitors[0].get('score', 0))
                game.away_score = int(competitors[1].get('score', 0))
            
            return game
            
        except Exception as e:
            logger.error(f"Error parsing game event: {e}")
            return None
    
    def get_current_nfl_week(self) -> int:
        """Calculate current NFL week"""
        now = datetime.now()
        
        if now.year >= 2025:
            season_start = datetime(2025, 9, 4)
            season_end = datetime(2026, 1, 12)
        else:
            season_start = datetime(2024, 9, 5)
            season_end = datetime(2025, 1, 8)
        
        if now < season_start:
            return 1
        elif now > season_end:
            return 18
        else:
            days_since_start = (now - season_start).days
            week = min(18, max(1, (days_since_start // 7) + 1))
            return week
    
    def generate_schedule_games(self, week: int, year: int) -> List[NFLGame]:
        """Generate scheduled games based on NFL calendar"""
        if year == 2025:
            season_start = datetime(2025, 9, 4)
        elif year == 2026:
            season_start = datetime(2026, 9, 10)
        else:
            season_start = datetime(year, 9, 7)
        
        week_start = season_start + timedelta(weeks=week-1)
        games = []
        
        # NFL teams for rotation
        teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 
                'MIA', 'NYJ', 'CIN', 'CLE', 'HOU', 'IND', 'JAX', 'TEN', 'NO', 'ATL',
                'CAR', 'TB', 'MIN', 'DET', 'PHI', 'WAS', 'ARI', 'SEA', 'LAR', 'LV', 'NYG', 'CHI']
        
        # Thursday Night Football (weeks 2-17)
        used_teams = set()
        if 2 <= week <= 17:
            thursday = week_start + timedelta(days=3)
            home_team = teams[(week * 2) % len(teams)]
            away_team = teams[(week * 2 + 1) % len(teams)]
            used_teams.update([home_team, away_team])
            
            games.append(NFLGame(
                game_id=f'tnf_{year}_week_{week}',
                week=week,
                year=year,
                home_team=home_team,
                away_team=away_team,
                game_date=thursday.replace(hour=20, minute=15),
                is_thursday_night=True
            ))
        
        # Sunday games
        sunday = week_start + timedelta(days=6)
        available_teams = [t for t in teams if t not in used_teams]
        
        for i in range(0, min(26, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                game_time = sunday.replace(hour=13, minute=0) if i < 16 else sunday.replace(hour=16, minute=25)
                games.append(NFLGame(
                    game_id=f'sun_{year}_week_{week}_game_{i//2}',
                    week=week,
                    year=year,
                    home_team=available_teams[i],
                    away_team=available_teams[i + 1],
                    game_date=game_time
                ))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Monday Night Football (weeks 1-17)
        if week <= 17:
            remaining_teams = [t for t in teams if t not in used_teams]
            if len(remaining_teams) >= 2:
                monday = week_start + timedelta(days=7)
                games.append(NFLGame(
                    game_id=f'mnf_{year}_week_{week}',
                    week=week,
                    year=year,
                    home_team=remaining_teams[0],
                    away_team=remaining_teams[1],
                    game_date=monday.replace(hour=20, minute=15),
                    is_monday_night=True
                ))
        
        return games
