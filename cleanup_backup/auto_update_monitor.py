#!/usr/bin/env python3
"""
Auto-Update Monitor
Ensures the background game updater is running and provides monitoring capabilities
"""

import time
import sqlite3
from datetime import datetime, timedelta
from background_updater import start_background_updater, get_updater_status
from score_updater import NFLScoreUpdater
from api_rate_limiter import check_api_rate_limit, get_api_calls_remaining
import logging

logger = logging.getLogger(__name__)

class AutoUpdateMonitor:
    """Monitors and ensures automatic game updates are working"""
    
    def __init__(self):
        self.last_check = None
        self.consecutive_failures = 0
        
    def ensure_updater_running(self) -> bool:
        """Ensure the background updater is running"""
        try:
            status = get_updater_status()
            if not status['running']:
                logger.info("🚀 Background updater not running, starting it...")
                start_background_updater()
                
                # Verify it started
                time.sleep(2)
                status = get_updater_status()
                if status['running']:
                    logger.info("✅ Background updater successfully started")
                    return True
                else:
                    logger.error("❌ Failed to start background updater")
                    return False
            else:
                logger.info("✅ Background updater is already running")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error ensuring updater is running: {e}")
            return False
    
    def check_recent_updates(self) -> dict:
        """Check if games have been updated recently"""
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            # Get current week
            current_date = datetime.now()
            season_start = datetime(2025, 9, 5)
            days_since_start = (current_date - season_start).days
            current_week = max(1, min(18, (days_since_start // 7) + 1))
            
            # Check games that should have been updated
            cursor.execute('''
                SELECT game_id, away_team, home_team, away_score, home_score, 
                       is_final, game_status, game_date
                FROM nfl_games 
                WHERE week = ? AND year = 2025
                AND datetime(game_date) < datetime('now', '-2 hours')
                ORDER BY game_date DESC
            ''', (current_week,))
            
            past_games = cursor.fetchall()
            
            # Check for games that should be updated but aren't
            needs_update = []
            for game in past_games:
                game_id, away, home, away_score, home_score, is_final, status, game_date = game
                
                # If game was more than 4 hours ago and still not final, it likely needs updating
                game_time = datetime.fromisoformat(game_date.replace('Z', '+00:00')).replace(tzinfo=None)
                hours_ago = (current_date - game_time).total_seconds() / 3600
                
                if hours_ago > 4 and not is_final and (away_score == 0 and home_score == 0):
                    needs_update.append({
                        'game': f"{away} @ {home}",
                        'hours_ago': round(hours_ago, 1),
                        'status': status or 'Scheduled'
                    })
            
            conn.close()
            
            return {
                'current_week': current_week,
                'past_games_count': len(past_games),
                'needs_update_count': len(needs_update),
                'needs_update': needs_update
            }
            
        except Exception as e:
            logger.error(f"Error checking recent updates: {e}")
            return {'error': str(e)}
    
    def force_update_now(self) -> dict:
        """Force an immediate update using ESPN API"""
        try:
            logger.info("🔄 Forcing immediate score update...")
            
            updater = NFLScoreUpdater('nfl_fantasy.db')
            results = updater.run_update_cycle()
            
            logger.info(f"✅ Force update completed: {results.get('games_updated', 0)} games updated")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in force update: {e}")
            return {'error': str(e)}
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        try:
            # Background updater status
            updater_status = get_updater_status()
            
            # API status
            api_ok = check_api_rate_limit()
            api_remaining = get_api_calls_remaining()
            
            # Recent updates check
            update_check = self.check_recent_updates()
            
            # Current time and day
            now = datetime.now()
            current_day = now.weekday()
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            game_days = [3, 6, 0, 1]  # Thursday, Sunday, Monday, Tuesday
            is_game_day = current_day in game_days
            
            return {
                'timestamp': now.isoformat(),
                'current_day': day_names[current_day],
                'is_game_day': is_game_day,
                'updater': updater_status,
                'api': {
                    'rate_limit_ok': api_ok,
                    'calls_remaining': api_remaining
                },
                'recent_updates': update_check
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}

def main():
    """Main function for command line usage"""
    print("🔍 AUTO-UPDATE MONITOR")
    print("=" * 50)
    
    monitor = AutoUpdateMonitor()
    
    # Ensure updater is running
    monitor.ensure_updater_running()
    
    # Get system status
    status = monitor.get_system_status()
    
    print(f"Current Time: {status.get('timestamp', 'Unknown')}")
    print(f"Current Day: {status.get('current_day', 'Unknown')} {'(Game Day)' if status.get('is_game_day') else '(Off Day)'}")
    print()
    
    # Updater status
    updater = status.get('updater', {})
    print("Background Updater:")
    print(f"  Running: {updater.get('running', False)}")
    print(f"  Update Interval: {updater.get('update_interval_minutes', 'Unknown')} minutes")
    print(f"  Current Week: {updater.get('current_week', 'Unknown')}")
    print()
    
    # API status
    api = status.get('api', {})
    print("API Status:")
    print(f"  Rate Limit OK: {api.get('rate_limit_ok', 'Unknown')}")
    print(f"  Calls Remaining: {api.get('calls_remaining', 'Unknown')}")
    print()
    
    # Recent updates
    updates = status.get('recent_updates', {})
    if 'error' not in updates:
        print("Recent Updates:")
        print(f"  Current Week: {updates.get('current_week', 'Unknown')}")
        print(f"  Past Games: {updates.get('past_games_count', 0)}")
        print(f"  Need Updates: {updates.get('needs_update_count', 0)}")
        
        if updates.get('needs_update'):
            print("\n  Games needing updates:")
            for game in updates['needs_update']:
                print(f"    - {game['game']} ({game['hours_ago']} hours ago) - {game['status']}")
    
    # If there are games needing updates, offer to force update
    if updates.get('needs_update_count', 0) > 0:
        print("\n🚨 Games may need updating!")
        response = input("Force update now? (y/n): ").strip().lower()
        if response == 'y':
            print("\n🔄 Running force update...")
            results = monitor.force_update_now()
            if 'error' not in results:
                print(f"✅ Updated {results.get('games_updated', 0)} games")
            else:
                print(f"❌ Error: {results['error']}")

if __name__ == "__main__":
    main()
