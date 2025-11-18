#!/usr/bin/env python3
"""
SIMPLE BACKGROUND SERVICE
=========================

This replaces ALL the complex background updater systems that were causing
server crashes with a simple, reliable solution that runs outside the 
Flask app process.

Instead of threading/multiprocessing inside Flask (which causes crashes):
- This runs as a separate script
- Called by Windows Task Scheduler every 15 minutes  
- No infinite loops or memory leaks
- Graceful error handling
- Automatic recovery

This replaces:
- background_updater.py
- enhanced_background_updater.py  
- pfr_monitoring_system.py
- All threading-based solutions
"""

import sqlite3
import requests
import sys
from datetime import datetime
from pathlib import Path
import urllib3

# Disable SSL warnings for enterprise networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SimpleBackgroundService:
    """Simple, crash-proof background service"""
    
    def __init__(self, db_path: str = 'nfl_fantasy.db'):
        self.db_path = Path(db_path)
        self.year = 2025
        self.log_file = Path('simple_service.log')
        
        # Team mappings
        self.teams = {
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

    def log(self, message: str):
        """Simple logging to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        print(log_message)  # Console
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\\n')
        except Exception as e:
            print(f"Logging error: {e}")
        
        # Keep log file small (max 100KB)
        try:
            if self.log_file.exists() and self.log_file.stat().st_size > 100000:
                # Keep only last 50 lines
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] Log rotated\\n")
                    f.writelines(lines[-50:])
        except:
            pass

    def get_current_week(self) -> int:
        """Get current NFL week"""
        try:
            if not self.db_path.exists():
                self.log(f"ERROR: Database not found: {self.db_path}")
                return 11
                
            conn = sqlite3.connect(str(self.db_path), timeout=10)
            cursor = conn.cursor()
            
            # Check league settings
            cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
            result = cursor.fetchone()
            
            if result:
                week = int(result[0])
                conn.close()
                return week
                
            # Fallback: incomplete games
            cursor.execute("""
                SELECT week FROM nfl_games 
                WHERE year = ? AND is_final = 0 
                ORDER BY week ASC LIMIT 1
            """, (self.year,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 11
            
        except Exception as e:
            self.log(f"ERROR getting current week: {e}")
            return 11

    def update_scores(self, week: int) -> int:
        """Update scores for a specific week"""
        try:
            # Get ESPN data with SSL verification disabled for enterprise networks
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            params = {'seasontype': 2, 'week': week, 'year': self.year}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers,
                timeout=30,
                verify=False  # Disable SSL verification for enterprise networks
            )
            response.raise_for_status()
            
            data = response.json()
            games = data.get('events', [])
            
            if not games:
                self.log(f"No games found for Week {week}")
                return 0
            
            return self._update_database(games, week)
            
        except requests.RequestException as e:
            self.log(f"ESPN API error for Week {week}: {str(e)[:100]}...")
            return 0
        except Exception as e:
            self.log(f"Unexpected error updating Week {week}: {e}")
            return 0

    def _update_database(self, games: list, week: int) -> int:
        """Update database with game data"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=30)
            cursor = conn.cursor()
            updated = 0
            
            for game in games:
                try:
                    status = game.get('status', {}).get('type', {}).get('name', '')
                    
                    if status not in ['STATUS_FINAL', 'STATUS_IN_PROGRESS']:
                        continue
                    
                    competitors = game.get('competitions', [{}])[0].get('competitors', [])
                    if len(competitors) != 2:
                        continue
                    
                    away_team, home_team = None, None
                    away_score, home_score = 0, 0
                    
                    for comp in competitors:
                        abbr = comp.get('team', {}).get('abbreviation', '')
                        score = int(comp.get('score', 0))
                        is_home = comp.get('homeAway') == 'home'
                        
                        team_name = self.teams.get(abbr, abbr)
                        
                        if is_home:
                            home_team, home_score = team_name, score
                        else:
                            away_team, away_score = team_name, score
                    
                    if not away_team or not home_team:
                        continue
                    
                    # Update game
                    is_final = 1 if status == 'STATUS_FINAL' else 0
                    
                    cursor.execute("""
                        UPDATE nfl_games 
                        SET away_score = ?, home_score = ?, is_final = ?
                        WHERE away_team = ? AND home_team = ? AND week = ? AND year = ?
                    """, (away_score, home_score, is_final, away_team, home_team, week, self.year))
                    
                    if cursor.rowcount > 0:
                        updated += 1
                        self.log(f"UPDATED: {away_team} {away_score} - {home_team} {home_score}")
                        
                        # Update picks if final
                        if is_final:
                            self._update_picks(cursor, away_team, home_team, away_score, home_score, week)
                
                except Exception as e:
                    self.log(f"Error processing game: {e}")
            
            conn.commit()
            conn.close()
            return updated
            
        except Exception as e:
            self.log(f"Database error: {e}")
            return 0

    def _update_picks(self, cursor, away_team: str, home_team: str, 
                     away_score: int, home_score: int, week: int):
        """Update pick scoring"""
        try:
            winner = home_team if home_score > away_score else away_team
            
            cursor.execute("""
                SELECT id FROM nfl_games 
                WHERE away_team = ? AND home_team = ? AND week = ? AND year = ?
            """, (away_team, home_team, week, self.year))
            
            game = cursor.fetchone()
            if not game:
                return
            
            cursor.execute("""
                UPDATE user_picks 
                SET is_correct = CASE WHEN selected_team = ? THEN 1 ELSE 0 END,
                    points_earned = CASE WHEN selected_team = ? THEN 1 ELSE 0 END
                WHERE game_id = ?
            """, (winner, winner, game[0]))
            
            self.log(f"PICKS: Updated {cursor.rowcount} picks for {away_team} vs {home_team}")
            
        except Exception as e:
            self.log(f"Error updating picks: {e}")

    def run_update_cycle(self):
        """Run one complete update cycle"""
        try:
            self.log("=== STARTING UPDATE CYCLE ===")
            
            # Get current week
            current_week = self.get_current_week()
            self.log(f"Current week: {current_week}")
            
            # Update current week
            updated = self.update_scores(current_week)
            self.log(f"Week {current_week}: {updated} games updated")
            
            # Also check next week
            next_week = current_week + 1
            if next_week <= 18:
                next_updated = self.update_scores(next_week)
                self.log(f"Week {next_week}: {next_updated} games updated")
                updated += next_updated
            
            self.log(f"=== CYCLE COMPLETE: {updated} total updates ===")
            return updated
            
        except Exception as e:
            self.log(f"CYCLE ERROR: {e}")
            return 0

    def create_task_scheduler_script(self):
        """Create Windows Task Scheduler setup script"""
        script_path = Path('setup_task_scheduler.bat')
        
        service_path = Path(__file__).absolute()
        
        bat_content = f'''@echo off
echo Setting up NFL Fantasy Background Service...
echo.

REM Delete existing task if it exists
schtasks /delete /tn "NFL_Fantasy_Background" /f >nul 2>&1

REM Create new task to run every 15 minutes
schtasks /create /tn "NFL_Fantasy_Background" /tr "python \\"{service_path}\\" --run" /sc minute /mo 15 /f

if %errorlevel% == 0 (
    echo ✅ Task scheduled successfully!
    echo   Task Name: NFL_Fantasy_Background
    echo   Frequency: Every 15 minutes
    echo   Command: python "{service_path}" --run
    echo.
    echo To check status: schtasks /query /tn "NFL_Fantasy_Background"
    echo To delete task: schtasks /delete /tn "NFL_Fantasy_Background" /f
) else (
    echo ❌ Failed to create scheduled task
    echo   Make sure you're running as Administrator
)

echo.
pause
'''

        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.log(f"Created task scheduler setup: {script_path}")
            print(f"\\n✅ Created {script_path}")
            print("   Run as Administrator to set up automatic updates")
            
        except Exception as e:
            self.log(f"Error creating task script: {e}")


def main():
    """Main function"""
    service = SimpleBackgroundService()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        # Called by Task Scheduler
        service.run_update_cycle()
        sys.exit(0)
    
    # Interactive mode
    print("SIMPLE BACKGROUND SERVICE")
    print("=" * 40)
    print("This replaces all complex background systems")
    print("with a simple, crash-proof solution.")
    print()
    print("Options:")
    print("1. Run update cycle once")
    print("2. Set up Windows Task Scheduler (auto-run every 15 min)")
    print("3. Show current status")
    print("4. Exit")
    
    try:
        choice = input("\\nSelect (1-4): ").strip()
        
        if choice == '1':
            print("\\nRunning update cycle...")
            updated = service.run_update_cycle()
            print(f"Complete: {updated} games updated")
            
        elif choice == '2':
            print("\\nSetting up automatic background service...")
            service.create_task_scheduler_script()
            print("\\nNext steps:")
            print("1. Run 'setup_task_scheduler.bat' as Administrator")
            print("2. The service will run automatically every 15 minutes")
            print("3. Check 'simple_service.log' for activity")
            
        elif choice == '3':
            print("\\nService Status:")
            current_week = service.get_current_week()
            print(f"Current week: {current_week}")
            
            log_file = Path('simple_service.log')
            if log_file.exists():
                print(f"Log file: {log_file} ({log_file.stat().st_size} bytes)")
                # Show last few log entries
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print("Recent activity:")
                        for line in lines[-5:]:
                            print(f"  {line.rstrip()}")
                except:
                    pass
            else:
                print("No log file found")
                
        elif choice == '4':
            print("Goodbye!")
            
        else:
            print("Invalid option")
            
    except KeyboardInterrupt:
        print("\\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()