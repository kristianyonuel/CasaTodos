"""
Background Game Results Updater
Automatically updates game scores every 15 minutes during game days
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from database_sync import update_live_scores
from api_rate_limiter import check_api_rate_limit

logger = logging.getLogger(__name__)

class BackgroundGameUpdater:
    """Handles automatic game score updates every 15 minutes"""
    
    def __init__(self, update_interval: int = 15):
        self.update_interval = update_interval * 60  # Convert minutes to seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
    def start(self):
        """Start the background updater"""
        if self.running:
            logger.warning("Background updater is already running")
            return
            
        self.running = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        logger.info(f"Background game updater started (updates every {self.update_interval//60} minutes)")
        
    def stop(self):
        """Stop the background updater"""
        if not self.running:
            return
            
        self.running = False
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        logger.info("Background game updater stopped")
        
    def _update_loop(self):
        """Main update loop that runs in background thread"""
        while self.running and not self.stop_event.is_set():
            try:
                self._update_games()
            except Exception as e:
                logger.error(f"Error in background game update: {e}")
                
            # Wait for next update interval or stop event
            self.stop_event.wait(self.update_interval)
            
    def _update_games(self):
        """Update game scores for current week"""
        try:
            # Check API rate limits first
            if not check_api_rate_limit():
                logger.warning("API rate limit reached, skipping update")
                return
                
            # Get current week
            current_week = self._get_current_nfl_week()
            if current_week is None:
                logger.info("No current NFL week determined, skipping update")
                return
                
            # Update during game days (Thursday, Sunday, Monday) and Tuesday (for MNF results)
            current_day = datetime.now().weekday()  # 0=Monday, 1=Tuesday, ..., 6=Sunday
            game_days = [3, 6, 0, 1]  # Thursday, Sunday, Monday, Tuesday
            
            if current_day not in game_days:
                logger.info(f"Not a game day (weekday {current_day}), skipping update")
                return
                
            logger.info(f"Updating live scores for Week {current_week}")
            
            # Update live scores
            updated_count = update_live_scores(current_week, 2025)
            
            if updated_count > 0:
                logger.info(f"Successfully updated {updated_count} games")
            else:
                logger.debug("No games needed updating")
                
        except Exception as e:
            logger.error(f"Error updating games: {e}")
            
    def _get_current_nfl_week(self) -> Optional[int]:
        """Determine current NFL week based on date"""
        try:
            # NFL 2025 season starts in early September
            # Week 1 typically starts around September 5-8
            season_start = datetime(2025, 9, 5)  # Approximate start date
            current_date = datetime.now()
            
            if current_date < season_start:
                return None  # Season hasn't started
                
            # Calculate weeks since season start
            days_since_start = (current_date - season_start).days
            week = (days_since_start // 7) + 1
            
            # NFL regular season is 18 weeks
            if week > 18:
                return None  # Season is over
                
            return week
            
        except Exception as e:
            logger.error(f"Error determining current NFL week: {e}")
            return None
            
    def is_running(self) -> bool:
        """Check if the updater is currently running"""
        return self.running and self.thread and self.thread.is_alive()
        
    def get_status(self) -> dict:
        """Get current status of the background updater"""
        return {
            'running': self.is_running(),
            'update_interval_minutes': self.update_interval // 60,
            'current_week': self._get_current_nfl_week(),
            'next_update_in_seconds': self.update_interval if self.is_running() else None
        }

# Global instance
game_updater = BackgroundGameUpdater(update_interval=15)  # 15 minutes

def start_background_updater():
    """Start the global background game updater"""
    game_updater.start()
    
def stop_background_updater():
    """Stop the global background game updater"""
    game_updater.stop()
    
def get_updater_status():
    """Get status of the global background updater"""
    return game_updater.get_status()
