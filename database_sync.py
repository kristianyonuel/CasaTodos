"""
Database synchronization with BallDontLie NFL API
Includes rate limiting to avoid API abuse (max 5 calls per hour)
"""
import sqlite3
from datetime import datetime
from nfl_api_service import get_season_schedule, get_week_games, get_live_scores
from utils.timezone_utils import format_ast_time
from api_rate_limiter import check_api_rate_limit, record_api_call, get_api_calls_remaining
import logging

logger = logging.getLogger(__name__)

def sync_season_from_api(year: int = 2025) -> int:
    """Sync complete season from BallDontLie API with AST timezone and rate limiting"""
    try:
        # Check rate limit before making API call
        if not check_api_rate_limit():
            remaining = get_api_calls_remaining()
            logger.warning(f"API rate limit exceeded. Calls remaining: {remaining}")
            return 0
        
        print(f"🔄 Syncing {year} NFL season from BallDontLie API (times in AST)...")
        print(f"📊 API calls remaining this hour: {get_api_calls_remaining()}")
        
        # Ensure we're syncing the correct year
        if year < 2020:
            print(f"❌ Year {year} not supported. Using 2025 instead.")
            year = 2025
        
        # Get season schedule from API
        games_data = get_season_schedule(year)
        record_api_call()  # Record the API call
        
        if not games_data:
            print(f"❌ No games data received from BallDontLie API for {year}")
            return 0
        
        # Clear existing games for the year
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM nfl_games WHERE year = ?', (year,))
        
        games_added = 0
        
        for game in games_data:
            try:
                game_id = f"bdl_{year}_w{game['week']}_{game['away_team']}_{game['home_team']}"
                
                # Store game date in AST format
                game_date_str = format_ast_time(game['game_date'], '%Y-%m-%d %H:%M:%S') if game['game_date'] else None
                
                cursor.execute('''
                    INSERT INTO nfl_games 
                    (week, year, game_id, away_team, home_team, game_date, 
                     is_thursday_night, is_monday_night, is_sunday_night,
                     away_score, home_score, game_status, is_final,
                     quarter, time_remaining, tv_network, stadium)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game['week'], game['year'], game_id,
                    game['away_team'], game['home_team'],
                    game_date_str,  # Already converted to AST
                    game['is_thursday_night'], game['is_monday_night'], game['is_sunday_night'],
                    game['away_score'], game['home_score'],
                    game['game_status'], game['is_final'],
                    game['quarter'], game['time_remaining'], game['tv_network'], game['stadium']
                ))
                
                games_added += 1
                
            except Exception as e:
                logger.error(f"Error inserting game: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully synced {games_added} games for {year}")
        return games_added
        
    except Exception as e:
        logger.error(f"Season sync error for {year}: {e}")
        print(f"❌ Season sync failed for {year}: {e}")
        return 0

def sync_week_from_api(week: int, year: int = 2025) -> int:
    """Sync specific week from BallDontLie API with rate limiting"""
    try:
        # Check rate limit before making API call
        if not check_api_rate_limit():
            remaining = get_api_calls_remaining()
            logger.warning(f"API rate limit exceeded. Cannot sync Week {week}. Calls remaining: {remaining}")
            return 0
        
        print(f"🔄 Syncing Week {week}, {year} from BallDontLie API...")
        print(f"📊 API calls remaining this hour: {get_api_calls_remaining()}")
        
        # Ensure we're syncing the correct year  
        if year < 2020:
            print(f"❌ Year {year} not supported. Using 2025 instead.")
            year = 2025
        
        # Get week games from API
        games_data = get_week_games(week, year)
        record_api_call()  # Record the API call
        
        if not games_data:
            print(f"❌ No games data for Week {week}")
            return 0
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        games_updated = 0
        
        for game in games_data:
            try:
                game_id = f"bdl_{year}_w{week}_{game['away_team']}_{game['home_team']}"
                
                # Check if game exists
                cursor.execute('SELECT id FROM nfl_games WHERE game_id = ?', (game_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing game
                    cursor.execute('''
                        UPDATE nfl_games SET
                        game_date = ?, away_score = ?, home_score = ?,
                        game_status = ?, is_final = ?, quarter = ?,
                        time_remaining = ?, tv_network = ?, stadium = ?
                        WHERE game_id = ?
                    ''', (
                        game['game_date'].strftime('%Y-%m-%d %H:%M:%S') if game['game_date'] else None,
                        game['away_score'], game['home_score'],
                        game['game_status'], game['is_final'], game['quarter'],
                        game['time_remaining'], game['tv_network'], game['stadium'],
                        game_id
                    ))
                else:
                    # Insert new game
                    cursor.execute('''
                        INSERT INTO nfl_games 
                        (week, year, game_id, away_team, home_team, game_date, 
                         is_thursday_night, is_monday_night, is_sunday_night,
                         away_score, home_score, game_status, is_final,
                         quarter, time_remaining, tv_network, stadium)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        game['week'], game['year'], game_id,
                        game['away_team'], game['home_team'],
                        game['game_date'].strftime('%Y-%m-%d %H:%M:%S') if game['game_date'] else None,
                        game['is_thursday_night'], game['is_monday_night'], game['is_sunday_night'],
                        game['away_score'], game['home_score'],
                        game['game_status'], game['is_final'],
                        game['quarter'], game['time_remaining'], game['tv_network'], game['stadium']
                    ))
                
                games_updated += 1
                
            except Exception as e:
                logger.error(f"Error updating game: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ Updated {games_updated} games for Week {week}, {year}")
        return games_updated
        
    except Exception as e:
        logger.error(f"Week sync error for {week}, {year}: {e}")
        print(f"❌ Week sync failed for Week {week}, {year}: {e}")
        return 0

def update_live_scores(week: int, year: int = 2025) -> int:
    """Update live scores from BallDontLie API with rate limiting and trigger scoring updates"""
    try:
        # Check rate limit before making API call
        if not check_api_rate_limit():
            remaining = get_api_calls_remaining()
            logger.info(f"API rate limit reached. Skipping live scores update. Calls remaining: {remaining}")
            # Return 0 but don't log as error since this is normal rate limiting
            return 0
        
        logger.info(f"Updating live scores for Week {week}, {year}. API calls remaining: {get_api_calls_remaining()}")
        
        # Get live scores from API
        scores_data = get_live_scores(week, year)
        record_api_call()  # Record the API call
        
        if not scores_data:
            logger.info(f"No live scores data received for Week {week}, {year}")
            return 0
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        games_updated = 0
        games_newly_finalized = 0
        
        for game in scores_data:
            try:
                # Check if game was already final before this update
                cursor.execute('''
                    SELECT is_final FROM nfl_games 
                    WHERE away_team = ? AND home_team = ? AND week = ? AND year = ?
                ''', (game['away_team'], game['home_team'], week, year))
                
                current_game = cursor.fetchone()
                was_final_before = current_game[0] if current_game else False
                
                # Update scores and status
                cursor.execute('''
                    UPDATE nfl_games SET
                    away_score = ?, home_score = ?, game_status = ?, 
                    is_final = ?, quarter = ?, time_remaining = ?
                    WHERE away_team = ? AND home_team = ? AND week = ? AND year = ?
                ''', (
                    game['away_score'], game['home_score'], game['game_status'],
                    game['is_final'], game['quarter'], game['time_remaining'],
                    game['away_team'], game['home_team'], week, year
                ))
                
                if cursor.rowcount > 0:
                    games_updated += 1
                    
                    # Track if this game was newly finalized
                    if not was_final_before and game['is_final']:
                        games_newly_finalized += 1
                
            except Exception as e:
                logger.error(f"Error updating live score: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        # Trigger scoring update if any games were newly finalized
        if games_newly_finalized > 0:
            try:
                from scoring_updater import ScoringUpdater
                updater = ScoringUpdater()
                updater.trigger_scoring_update_after_game_finalization(week, year)
                logger.info(f"Triggered scoring update for Week {week}, {year} - {games_newly_finalized} games newly finalized")
            except Exception as e:
                logger.error(f"Error triggering scoring update: {e}")
        
        return games_updated
        
    except Exception as e:
        logger.error(f"Live scores update error: {e}")
        return 0
