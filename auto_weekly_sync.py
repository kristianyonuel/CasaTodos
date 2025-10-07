#!/usr/bin/env python3
"""
Automatic Weekly Game Sync
Runs after Monday Night Football to fetch next week's games
"""

import logging
import sqlite3
from datetime import datetime, timedelta
import pytz
from database_sync import sync_week_from_api
from nfl_week_calculator import get_current_nfl_week
from api_rate_limiter import check_api_rate_limit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_weekly_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def is_post_monday_night():
    """Check if it's Tuesday morning after Monday Night Football"""
    est_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(est_tz)
    
    # Tuesday (weekday 1) after 6 AM EST (8+ hours after MNF typically ends)
    if current_time.weekday() == 1 and current_time.hour >= 6:
        return True
    
    # Wednesday (weekday 2) any time (backup window)
    if current_time.weekday() == 2:
        return True
        
    return False


def check_week_games_exist(week, year=2025):
    """Check if games already exist for a given week"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?',
            (week, year)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        logger.error(f"Error checking week {week} games: {e}")
        return False


def auto_sync_next_week():
    """Automatically sync the next week's games if needed"""
    try:
        # Check if it's the right time
        if not is_post_monday_night():
            logger.info("Not post-Monday night time, skipping auto sync")
            return False
            
        # Get current NFL week
        current_week = get_current_nfl_week()
        logger.info(f"Current NFL week: {current_week}")
        
        # Check if current week games already exist
        if check_week_games_exist(current_week):
            logger.info(f"Week {current_week} games already exist, no sync needed")
            return True
            
        # Check API rate limit
        if not check_api_rate_limit():
            logger.warning("API rate limit exceeded, cannot sync")
            return False
            
        # Sync the current week games
        logger.info(f"Syncing Week {current_week} games...")
        result = sync_week_from_api(current_week, 2025)
        
        if result > 0:
            logger.info(f"✅ Successfully synced {result} games for Week {current_week}")
            return True
        else:
            logger.warning(f"❌ Failed to sync Week {current_week} games")
            return False
            
    except Exception as e:
        logger.error(f"Error in auto sync: {e}")
        return False


def check_and_sync_missing_weeks():
    """Check for any missing weeks up to current week and sync them"""
    try:
        current_week = get_current_nfl_week()
        missing_weeks = []
        
        # Check weeks 1 through current week
        for week in range(1, current_week + 1):
            if not check_week_games_exist(week):
                missing_weeks.append(week)
                
        if missing_weeks:
            logger.info(f"Found missing weeks: {missing_weeks}")
            
            for week in missing_weeks:
                if not check_api_rate_limit():
                    logger.warning(f"API rate limit hit, stopping at week {week}")
                    break
                    
                logger.info(f"Syncing missing Week {week}...")
                result = sync_week_from_api(week, 2025)
                if result > 0:
                    logger.info(f"✅ Synced {result} games for Week {week}")
                else:
                    logger.warning(f"❌ Failed to sync Week {week}")
                    
        return len(missing_weeks) == 0
        
    except Exception as e:
        logger.error(f"Error checking missing weeks: {e}")
        return False


if __name__ == "__main__":
    logger.info("🏈 Starting automatic weekly sync check...")
    
    # First check for any missing weeks
    check_and_sync_missing_weeks()
    
    # Then do the main auto sync
    auto_sync_next_week()
    
    logger.info("🏁 Auto sync check completed")