#!/usr/bin/env python3
"""
Enhanced Background Updater with Weekly Game Sync
Combines live score updates with automatic weekly game fetching
"""

import threading
import time
import logging
from datetime import datetime
from typing import Optional
from database_sync import update_live_scores, update_live_scores_espn
from api_rate_limiter import check_api_rate_limit
from auto_weekly_sync import auto_sync_next_week, check_and_sync_missing_weeks

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_background_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedBackgroundUpdater:
    """Enhanced background updater with weekly sync and live score updates"""
    
    def __init__(self, update_interval: int = 5):
        self.default_interval = update_interval * 60  # Convert to seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.last_weekly_check = None
        
    def _get_dynamic_interval(self) -> int:
        """Get dynamic update interval based on current time and game status"""
        try:
            current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
            current_hour = datetime.now().hour
            
            # Game days: Thursday (3), Saturday (5), Sunday (6), Monday (0), Tuesday (1)
            game_days = [0, 1, 3, 5, 6]
            
            # During game days and peak game hours (11 AM - 11 PM)
            if current_day in game_days and 11 <= current_hour <= 23:
                return 5 * 60  # 5 minutes during game times
            else:
                return 30 * 60  # 30 minutes during quiet periods
                
        except Exception as e:
            logger.error(f"Error calculating dynamic interval: {e}")
            return self.default_interval
    
    def _should_check_weekly_sync(self) -> bool:
        """Check if it's time to run weekly sync (once per day)"""
        now = datetime.now()
        
        # If never checked before, or it's a new day
        if (self.last_weekly_check is None or 
            now.date() != self.last_weekly_check.date()):
            return True
            
        return False
    
    def _run_weekly_sync_check(self):
        """Run the weekly sync check"""
        try:
            logger.info("🏈 Running weekly sync check...")
            
            # Check for missing weeks first
            check_and_sync_missing_weeks()
            
            # Then check for next week sync
            auto_sync_next_week()
            
            self.last_weekly_check = datetime.now()
            logger.info("✅ Weekly sync check completed")
            
        except Exception as e:
            logger.error(f"Error in weekly sync check: {e}")
    
    def _update_loop(self):
        """Main update loop with both live scores and weekly sync"""
        logger.info("Enhanced background updater started")
        
        while not self.stop_event.is_set():
            try:
                # Get current interval
                interval = self._get_dynamic_interval()
                current_day = datetime.now().weekday()
                
                # Check for weekly sync once per day
                if self._should_check_weekly_sync():
                    self._run_weekly_sync_check()
                
                # Skip live score updates on non-game days
                if current_day not in [0, 1, 3, 5, 6]:  # Non-game days
                    logger.info(f"Not a game day (weekday {current_day}), skipping live score update")
                else:
                    # Update live scores
                    if check_api_rate_limit():
                        logger.info("Updating live scores...")
                        try:
                            # Try ESPN API first, fallback to BallDontLie
                            espn_result = update_live_scores_espn()
                            if espn_result:
                                logger.info("✅ ESPN score update successful")
                            else:
                                logger.info("⚠️ ESPN failed, trying BallDontLie...")
                                update_live_scores()
                        except Exception as e:
                            logger.error(f"Error updating scores: {e}")
                    else:
                        logger.warning("API rate limit exceeded, skipping score update")
                
                # Log current status
                logger.info(f"Update cycle completed (next in {interval//60} min)")
                
                # Wait for next update or stop signal
                if self.stop_event.wait(interval):
                    break
                    
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                # Wait a bit before retrying
                if self.stop_event.wait(60):
                    break
        
        logger.info("Enhanced background updater stopped")
    
    def start(self):
        """Start the enhanced background updater"""
        if self.running:
            logger.warning("Enhanced updater is already running")
            return
            
        self.running = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        logger.info("Enhanced background updater thread started")
    
    def stop(self):
        """Stop the enhanced background updater"""
        if not self.running:
            logger.warning("Enhanced updater is not running")
            return
            
        logger.info("Stopping enhanced background updater...")
        self.running = False
        self.stop_event.set()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
            
        logger.info("Enhanced background updater stopped")
    
    def is_running(self) -> bool:
        """Check if the updater is currently running"""
        return self.running and self.thread and self.thread.is_alive()


# Global updater instance
enhanced_updater = EnhancedBackgroundUpdater()


def start_enhanced_updater():
    """Start the enhanced background updater"""
    enhanced_updater.start()


def stop_enhanced_updater():
    """Stop the enhanced background updater"""
    enhanced_updater.stop()


if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        enhanced_updater.stop()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 Starting Enhanced Background Updater...")
    logger.info("Features: Live score updates + Weekly game sync")
    
    # Start the enhanced updater
    enhanced_updater.start()
    
    try:
        # Keep the main thread alive
        while enhanced_updater.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        enhanced_updater.stop()
        logger.info("Enhanced background updater shutdown complete")