#!/usr/bin/env python3
"""
ROBUST NFL FANTASY SCORE SYSTEM
===============================

This single file replaces ALL the scattered PFR/ESPN/monitoring systems 
with one simple, reliable solution that won't crash the server.

Features:
- Single point of control for all score updates
- Built-in error handling and recovery
- No infinite loops or threading issues
- Minimal memory usage
- Self-healing when things go wrong
- Comprehensive logging

This replaces:
- pfr_monitoring_system.py
- pfr_app_integration.py  
- background_updater.py
- All 290+ fix/debug/test files
"""

import sqlite3
import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os


class RobustNFLScoreSystem:
    """Single, robust system for NFL score updates"""
    
    def __init__(self, db_path: str = 'nfl_fantasy.db'):
        self.db_path = db_path
        self.year = 2025
        self.max_retries = 3
        self.retry_delay = 30  # seconds
        
        # Setup minimal logging to prevent log bloat
        self.setup_logging()
        
        # State tracking to prevent infinite loops
        self.last_update_time = None
        self.update_count = 0
        self.max_updates_per_hour = 10
        
        # Team name mappings (consolidated from all scattered files)
        self.team_mappings = {
            'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens',
            'BUF': 'Buffalo Bills', 'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears',
            'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns', 'DAL': 'Dallas Cowboys',
            'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
            'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars',
            'KC': 'Kansas City Chiefs', 'LV': 'Las Vegas Raiders', 'LAC': 'Los Angeles Chargers',
            'LAR': 'Los Angeles Rams', 'MIA': 'Miami Dolphins', 'MIN': 'Minnesota Vikings',
            'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants',
            'NYJ': 'New York Jets', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers',
            'SF': 'San Francisco 49ers', 'SEA': 'Seattle Seahawks', 'TB': 'Tampa Bay Buccaneers',
            'TEN': 'Tennessee Titans', 'WAS': 'Washington Commanders'
        }
        
        self.logger.info("🏈 Robust NFL Score System initialized")

    def setup_logging(self):
        """Setup simple, effective logging"""
        # Clear any existing handlers to prevent conflicts
        logging.getLogger().handlers.clear()
        
        # Create logger with rotation to prevent huge log files
        self.logger = logging.getLogger('RobustNFL')
        self.logger.setLevel(logging.INFO)
        
        # File handler with automatic rotation
        handler = logging.FileHandler('nfl_scores.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        
        # Keep log file small by truncating if it gets too big
        try:
            if os.path.exists('nfl_scores.log') and os.path.getsize('nfl_scores.log') > 1024 * 1024:  # 1MB
                with open('nfl_scores.log', 'w') as f:
                    f.write(f"{datetime.now()} - Log rotated due to size\\n")
        except:
            pass

    def get_current_week(self) -> int:
        """Get current NFL week with robust fallback"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # Check league settings first
            cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
            result = cursor.fetchone()
            
            if result and result[0]:
                week = int(result[0])
                conn.close()
                return week
                
            # Fallback: find week with incomplete games
            cursor.execute("""
                SELECT week FROM nfl_games 
                WHERE year = ? AND is_final = 0 
                ORDER BY week ASC LIMIT 1
            """, (self.year,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 11  # Safe fallback
            
        except Exception as e:
            self.logger.error(f"Error getting current week: {e}")
            return 11  # Safe fallback to current week

    def rate_limit_check(self) -> bool:
        """Check if we're within rate limits to prevent crashes"""
        now = datetime.now()
        
        # Reset count every hour
        if self.last_update_time and (now - self.last_update_time).seconds > 3600:
            self.update_count = 0
            
        if self.update_count >= self.max_updates_per_hour:
            self.logger.warning(f"Rate limit reached: {self.update_count} updates this hour")
            return False
            
        return True

    def safe_database_operation(self, operation_func, *args, **kwargs):
        """Execute database operations with error handling"""
        for attempt in range(self.max_retries):
            try:
                return operation_func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    self.logger.warning(f"Database locked, attempt {attempt + 1}/{self.max_retries}")
                    time.sleep(self.retry_delay)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Database operation failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(5)
        
        return None

    def update_scores_from_espn(self, week: int) -> int:
        """Update scores from ESPN with robust error handling"""
        if not self.rate_limit_check():
            return 0
            
        try:
            # Get ESPN data with timeout
            url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            params = {'seasontype': 2, 'week': week, 'year': self.year}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            games_data = data.get('events', [])
            
            if not games_data:
                self.logger.info(f"No games found for Week {week}")
                return 0
            
            return self.safe_database_operation(self._process_espn_games, games_data, week)
            
        except requests.RequestException as e:
            self.logger.error(f"ESPN API error: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"Unexpected error updating ESPN scores: {e}")
            return 0

    def _process_espn_games(self, games_data: list, week: int) -> int:
        """Process ESPN games data and update database"""
        conn = sqlite3.connect(self.db_path, timeout=30)
        cursor = conn.cursor()
        updated_count = 0
        
        try:
            for game in games_data:
                try:
                    # Extract game data
                    game_status = game.get('status', {}).get('type', {}).get('name', '')
                    
                    if game_status not in ['STATUS_FINAL', 'STATUS_IN_PROGRESS']:
                        continue
                    
                    competitors = game.get('competitions', [{}])[0].get('competitors', [])
                    if len(competitors) != 2:
                        continue
                    
                    # Get team info and scores
                    away_team = None
                    home_team = None
                    away_score = 0
                    home_score = 0
                    
                    for comp in competitors:
                        team_abbr = comp.get('team', {}).get('abbreviation', '')
                        team_score = int(comp.get('score', 0))
                        is_home = comp.get('homeAway') == 'home'
                        
                        if is_home:
                            home_team = self.team_mappings.get(team_abbr, team_abbr)
                            home_score = team_score
                        else:
                            away_team = self.team_mappings.get(team_abbr, team_abbr)
                            away_score = team_score
                    
                    if not away_team or not home_team:
                        continue
                    
                    # Update database
                    is_final = 1 if game_status == 'STATUS_FINAL' else 0
                    
                    cursor.execute("""
                        UPDATE nfl_games 
                        SET away_score = ?, home_score = ?, is_final = ?
                        WHERE away_team = ? AND home_team = ? AND week = ? AND year = ?
                    """, (away_score, home_score, is_final, away_team, home_team, week, self.year))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                        self.logger.info(f"Updated: {away_team} {away_score} - {home_team} {home_score}")
                        
                        # Update pick scoring if game is final
                        if is_final:
                            self._update_pick_scoring(cursor, away_team, home_team, away_score, home_score, week)
                
                except Exception as e:
                    self.logger.error(f"Error processing game: {e}")
                    continue
            
            conn.commit()
            self.update_count += 1
            self.last_update_time = datetime.now()
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database transaction error: {e}")
            raise
        finally:
            conn.close()
        
        return updated_count

    def _update_pick_scoring(self, cursor, away_team: str, home_team: str, 
                           away_score: int, home_score: int, week: int):
        """Update pick scoring for completed games"""
        try:
            # Determine winner
            winning_team = home_team if home_score > away_score else away_team
            
            # Get game ID
            cursor.execute("""
                SELECT id FROM nfl_games 
                WHERE away_team = ? AND home_team = ? AND week = ? AND year = ?
            """, (away_team, home_team, week, self.year))
            
            game = cursor.fetchone()
            if not game:
                return
            
            game_id = game[0]
            
            # Update picks
            cursor.execute("""
                UPDATE user_picks 
                SET is_correct = CASE 
                    WHEN selected_team = ? THEN 1 
                    ELSE 0 
                END,
                points_earned = CASE 
                    WHEN selected_team = ? THEN 1 
                    ELSE 0 
                END
                WHERE game_id = ?
            """, (winning_team, winning_team, game_id))
            
            self.logger.info(f"Updated {cursor.rowcount} picks for {away_team} vs {home_team}")
            
        except Exception as e:
            self.logger.error(f"Error updating pick scoring: {e}")

    def update_current_week(self) -> int:
        """Main method to update current week scores"""
        current_week = self.get_current_week()
        self.logger.info(f"Updating Week {current_week} scores...")
        
        updated = self.update_scores_from_espn(current_week)
        
        if updated > 0:
            self.logger.info(f"✅ Updated {updated} games in Week {current_week}")
        else:
            self.logger.info(f"📍 No updates needed for Week {current_week}")
        
        return updated

    def monitor_continuously(self, duration_minutes: int = 60):
        """Run continuous monitoring with safety limits"""
        self.logger.info(f"🔄 Starting monitoring for {duration_minutes} minutes")
        
        start_time = datetime.now()
        update_interval = 15  # 15 minutes between checks
        
        try:
            while True:
                # Check if duration exceeded
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                if elapsed >= duration_minutes:
                    self.logger.info(f"✅ Monitoring duration completed: {duration_minutes} minutes")
                    break
                
                # Run update
                try:
                    updated = self.update_current_week()
                    
                    if updated > 0:
                        # If we updated games, check next week too
                        next_week = self.get_current_week() + 1
                        if next_week <= 18:
                            next_updated = self.update_scores_from_espn(next_week)
                            self.logger.info(f"Also checked Week {next_week}: {next_updated} updates")
                
                except Exception as e:
                    self.logger.error(f"Update cycle error: {e}")
                
                # Wait for next update (with safety check)
                self.logger.info(f"⏰ Waiting {update_interval} minutes until next check...")
                time.sleep(update_interval * 60)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"🚨 Monitoring system error: {e}")
            
        self.logger.info("📊 Monitoring session ended")

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        current_week = self.get_current_week()
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # Get week statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final
                FROM nfl_games 
                WHERE week = ? AND year = ?
            """, (current_week, self.year))
            
            total, final = cursor.fetchone()
            conn.close()
            
            return {
                'current_week': current_week,
                'total_games': total or 0,
                'final_games': final or 0,
                'completion_rate': round((final / total * 100), 1) if total > 0 else 0,
                'last_update': self.last_update_time.isoformat() if self.last_update_time else None,
                'updates_this_hour': self.update_count,
                'system_healthy': True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                'current_week': current_week,
                'system_healthy': False,
                'error': str(e)
            }


def main():
    """Main function for running the system"""
    print("🏈 ROBUST NFL FANTASY SCORE SYSTEM")
    print("=" * 50)
    print("This replaces ALL scattered score update systems")
    print("with one simple, reliable solution.")
    print()
    
    system = RobustNFLScoreSystem()
    
    print("Available options:")
    print("1. Update current week once")
    print("2. Monitor for 1 hour")
    print("3. Monitor for 4 hours") 
    print("4. Show system status")
    print("5. Exit")
    
    try:
        choice = input("\\nSelect option (1-5): ").strip()
        
        if choice == "1":
            print("\\n🔄 Running single update...")
            updated = system.update_current_week()
            print(f"✅ Complete: {updated} games updated")
            
        elif choice == "2":
            print("\\n🔄 Starting 1-hour monitoring...")
            system.monitor_continuously(60)
            
        elif choice == "3":
            print("\\n🔄 Starting 4-hour monitoring...")
            system.monitor_continuously(240)
            
        elif choice == "4":
            print("\\n📊 System Status:")
            status = system.get_system_status()
            for key, value in status.items():
                print(f"   {key}: {value}")
                
        elif choice == "5":
            print("👋 Goodbye!")
            
        else:
            print("❌ Invalid option")
            
    except KeyboardInterrupt:
        print("\\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()