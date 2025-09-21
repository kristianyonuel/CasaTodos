#!/usr/bin/env python3
"""
Standalone Background Updater Starter
This script starts the background game updater and keeps it running
"""

import sys
import time
import signal
import logging
from background_updater import (
    start_background_updater, stop_background_updater, get_updater_status
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_updater.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False
    stop_background_updater()
    sys.exit(0)


def main():
    """Main function to start and monitor the background updater"""
    global running
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Starting NFL Fantasy Background Updater...")
    
    try:
        # Start the background updater
        start_background_updater()
        logger.info("Background updater started successfully")
        
        # Monitor and keep the script running
        while running:
            try:
                # Check status every 5 minutes
                status = get_updater_status()
                if status['running']:
                    interval = status['update_interval_minutes']
                    week = status['current_week']
                    
                    # Also check games needing update for detailed status
                    try:
                        import sqlite3
                        conn = sqlite3.connect('nfl_fantasy.db')
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT COUNT(*) FROM nfl_games
                            WHERE week = ? AND year = 2025
                            AND is_final = 0
                            AND datetime(game_date) < datetime('now', '-4 hours')
                        ''', (week,))
                        games_needing_update = cursor.fetchone()[0]
                        conn.close()
                        
                        logger.info(f"Background updater running - "
                                    f"Interval: {interval} min, Week: {week}, "
                                    f"Games needing update: "
                                    f"{games_needing_update}")
                    except Exception:
                        logger.info(f"Background updater running - "
                                    f"Interval: {interval} min, Week: {week}")
                else:
                    logger.warning("Background updater stopped unexpectedly, "
                                   "restarting...")
                    start_background_updater()
                
                # Sleep for 5 minutes before next status check
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
                
    except Exception as e:
        logger.error(f"Failed to start background updater: {e}")
        sys.exit(1)
    finally:
        logger.info("Stopping background updater...")
        stop_background_updater()
        logger.info("Background updater stopped")


if __name__ == '__main__':
    main()
