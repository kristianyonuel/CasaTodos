"""
Background Game Results Updater
Automatically updates game scores every 15 minutes during game days
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from database_sync import update_live_scores, update_live_scores_espn
from api_rate_limiter import check_api_rate_limit

logger = logging.getLogger(__name__)

class BackgroundGameUpdater:
    """Handles automatic game score updates with intelligent frequency"""
    
    def __init__(self, update_interval: int = 5):
        self.default_interval = update_interval * 60  # Convert minutes to seconds
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
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
            # Non-game days or off-peak hours
            else:
                return 30 * 60  # 30 minutes during quiet periods
                
        except Exception as e:
            logger.error(f"Error calculating dynamic interval: {e}")
            return self.default_interval
        
    def start(self):
        """Start the background updater"""
        if self.running:
            logger.warning("Background updater is already running")
            return
            
        self.running = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        logger.info("Background game updater started with dynamic intervals")
        
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
        """Main update loop with dynamic intervals"""
        while self.running and not self.stop_event.is_set():
            try:
                # Get current interval (5 min during games, 30 min otherwise)
                current_interval = self._get_dynamic_interval()
                
                # Log current interval for monitoring
                interval_min = current_interval // 60
                logger.info(f"Update cycle starting (next in {interval_min} min)")
                
                self._update_games()
            except Exception as e:
                logger.error(f"Error in background game update: {e}")
                
            # Wait for dynamic interval or stop event
            current_interval = self._get_dynamic_interval()
            self.stop_event.wait(current_interval)
            
    def _update_games(self):
        """Update game scores for current week using ESPN API and new score updater"""
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
                
            # First, check if there are any games that need updating
            games_needing_update = self._check_games_needing_update(current_week)
            
            # Get current day for game day logic
            current_day = datetime.now().weekday()  # 0=Mon, 6=Sun
            game_days = [3, 6, 0, 1]  # Thursday, Sunday, Monday, Tuesday
            
            # If it's not a game day but no games need updating, skip
            if current_day not in game_days and games_needing_update == 0:
                logger.info(f"Not a game day (weekday {current_day}) "
                            f"and no games need updating, skipping")
                return
            elif current_day not in game_days and games_needing_update > 0:
                logger.info(f"Not a game day (weekday {current_day}) but "
                            f"{games_needing_update} games need updating")
            else:
                logger.info(f"Game day (weekday {current_day}), "
                            f"updating live scores for Week {current_week}")
                
            # Use new comprehensive score updater
            try:
                from score_updater import NFLScoreUpdater
                score_updater = NFLScoreUpdater('nfl_fantasy.db')
                results = score_updater.run_update_cycle()
                
                updated_count = results.get('games_updated', 0)
                if updated_count > 0:
                    logger.info(f"Successfully updated {updated_count} games "
                                f"via new score updater")
                    
                    # IMPORTANT: Update weekly results after updating scores
                    self._update_weekly_results(current_week)
                else:
                    logger.debug("No games needed updating via new score "
                                 "updater")
                    
            except Exception as e:
                logger.error(f"Error with new score updater: {e}")
                
                # Fallback to original ESPN updater
                logger.info("Falling back to original ESPN API updater")
                updated_count = update_live_scores_espn(current_week, 2025)
                
                if updated_count > 0:
                    logger.info(f"Successfully updated {updated_count} games "
                                f"via fallback ESPN")
                    
                    # IMPORTANT: Update weekly results after updating scores
                    self._update_weekly_results(current_week)
                else:
                    logger.debug("No games needed updating via fallback ESPN")
                
        except Exception as e:
            logger.error(f"Error updating games: {e}")
            
    def _check_games_needing_update(self, week: int) -> int:
        """Check how many games in the current week need score updates"""
        try:
            # Import here to avoid circular imports
            import sqlite3
            
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            # Check for games that are not final but should be
            # (game time was more than 4 hours ago)
            cursor.execute('''
                SELECT COUNT(*) FROM nfl_games
                WHERE week = ? AND year = 2025
                AND is_final = 0
                AND datetime(game_date) < datetime('now', '-4 hours')
            ''', (week,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Error checking games needing update: {e}")
            return 0
            
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
            week = 10  # FORCED TO WEEK 10
            
            # NFL regular season is 18 weeks
            if week > 18:
                return None  # Season is over
                
            return week
            
        except Exception as e:
            logger.error(f"Error determining current NFL week: {e}")
            return None
    
    def _update_weekly_results(self, week: int):
        """Update weekly results after game scores are updated"""
        try:
            from scoring_updater import ScoringUpdater
            
            logger.info(f"Updating weekly results for Week {week}, 2025...")
            updater = ScoringUpdater('nfl_fantasy.db')
            success = updater.update_weekly_results(week, 2025)
            
            if success:
                logger.info(f"✅ Weekly results updated for Week {week}")
                
                # Also update previous week if it might have been affected
                if week > 1:
                    prev_success = updater.update_weekly_results(week - 1, 2025)
                    if prev_success:
                        logger.info(f"✅ Previous week ({week - 1}) results also updated")
            else:
                logger.warning(f"❌ Failed to update weekly results for Week {week}")
                
        except Exception as e:
            logger.error(f"Error updating weekly results for Week {week}: {e}")
            
    def is_running(self) -> bool:
        """Check if the updater is currently running"""
        return self.running and self.thread and self.thread.is_alive()
        
    def get_status(self) -> dict:
        """Get current status of the background updater"""
        if self.is_running():
            current_interval = self._get_dynamic_interval()
        else:
            current_interval = None
            
        return {
            'running': self.is_running(),
            'update_interval_minutes': (current_interval // 60
                                        if current_interval else None),
            'dynamic_intervals': True,
            'game_time_interval': '5 minutes',
            'off_peak_interval': '30 minutes',
            'current_week': self._get_current_nfl_week(),
            'next_update_in_seconds': (current_interval
                                       if self.is_running() else None)
        }


# Global instance - dynamic intervals: 5 min during games, 30 min off-peak
game_updater = BackgroundGameUpdater(update_interval=5)


def start_background_updater():
    """Start the global background game updater"""
    game_updater.start()
    

def stop_background_updater():
    """Stop the global background game updater"""
    game_updater.stop()
    

def get_updater_status():
    """Get status of the global background updater"""
    return game_updater.get_status()
