"""
Game management service for NFL Fantasy League
"""
import logging
from typing import List, Dict
from models import NFLGame, UserPick, GameRepository, PickRepository, DatabaseManager
from services.nfl_service import NFLService

logger = logging.getLogger(__name__)

class GameService:
    def __init__(self, db_manager: DatabaseManager):
        self.game_repo = GameRepository(db_manager)
        self.pick_repo = PickRepository(db_manager)
        self.nfl_service = NFLService()
    
    def ensure_games_exist(self, week: int, year: int) -> int:
        """Ensure games exist for a specific week, create if missing"""
        existing_games = self.game_repo.get_games_by_week(week, year)
        
        if existing_games:
            logger.info(f"Week {week} already has {len(existing_games)} games")
            return len(existing_games)
        
        logger.info(f"Creating games for Week {week}, {year}")
        
        # Try multiple methods to get games
        games = self._get_games_from_multiple_sources(week, year)
        
        if not games:
            logger.warning(f"No games found for Week {week}, {year}")
            return 0
        
        # Save games to database
        games_created = 0
        for game in games:
            try:
                self.game_repo.create_game(game)
                games_created += 1
            except Exception as e:
                logger.error(f"Error saving game: {e}")
                continue
        
        logger.info(f"Successfully created {games_created} games for Week {week}")
        return games_created
    
    def _get_games_from_multiple_sources(self, week: int, year: int) -> List[NFLGame]:
        """Try multiple sources to get games"""
        # Method 1: ESPN API
        games = self.nfl_service.fetch_games_from_api(week, year)
        if games:
            logger.info(f"Got {len(games)} games from ESPN API")
            return games
        
        # Method 2: Generated schedule
        games = self.nfl_service.generate_schedule_games(week, year)
        if games:
            logger.info(f"Generated {len(games)} games from schedule")
            return games
        
        logger.warning("No games available from any source")
        return []
    
    def get_games_with_picks(self, week: int, year: int, user_id: int) -> tuple:
        """Get games for a week with user's picks"""
        games = self.game_repo.get_games_by_week(week, year)
        user_picks = self.pick_repo.get_user_picks_for_week(user_id, week, year)
        
        return games, user_picks
    
    def submit_user_picks(self, user_id: int, picks_data: List[Dict]) -> int:
        """Submit user picks for games"""
        successful_picks = 0
        
        for pick_data in picks_data:
            try:
                pick = UserPick(
                    user_id=user_id,
                    game_id=pick_data.get('game_id'),
                    selected_team=pick_data.get('selected_team'),
                    predicted_home_score=pick_data.get('home_score'),
                    predicted_away_score=pick_data.get('away_score')
                )
                
                if pick.game_id and pick.selected_team:
                    self.pick_repo.create_or_update_pick(pick)
                    successful_picks += 1
                    
            except Exception as e:
                logger.error(f"Error processing pick: {e}")
                continue
        
        logger.info(f"Successfully processed {successful_picks} picks for user {user_id}")
        return successful_picks
    
    def populate_all_seasons(self) -> int:
        """Populate games for 2025-2026 seasons"""
        total_games = 0
        
        for year in [2025, 2026]:
            for week in range(1, 19):
                try:
                    games_created = self.ensure_games_exist(week, year)
                    total_games += games_created
                except Exception as e:
                    logger.error(f"Error populating {year} Week {week}: {e}")
                    continue
        
        logger.info(f"Population complete: {total_games} total games created")
        return total_games
