#!/usr/bin/env python3
"""
Weekly Auto-Monitor: Checks if automatic scoring system is working
Run this script once per week to verify everything is functioning properly
"""
import sqlite3
import requests
import json
from datetime import datetime, timedelta
import sys
import os

class WeeklyAutoMonitor:
    def __init__(self, db_path='nfl_fantasy.db'):
        self.db_path = db_path
        self.issues_found = []
        self.warnings = []
        self.successes = []
        
    def log_issue(self, message):
        self.issues_found.append(f"❌ {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  {message}")
        
    def log_success(self, message):
        self.successes.append(f"✅ {message}")
    
    def check_database_connectivity(self):
        """Check if we can connect to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM nfl_games")
            total_games = cursor.fetchone()[0]
            
            if total_games > 0:
                self.log_success(f"Database accessible with {total_games} total games")
                conn.close()
                return True
            else:
                self.log_issue("Database is empty - no games found")
                conn.close()
                return False
                
        except Exception as e:
            self.log_issue(f"Cannot connect to database: {e}")
            return False
    
    def check_current_week_status(self):
        """Check if current week games are being updated properly"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Calculate current NFL week
            from nfl_week_calculator import get_current_nfl_week
            current_week = get_current_nfl_week(2025)
            
            # Check games for current week
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
                       SUM(CASE WHEN home_score IS NOT NULL AND away_score IS NOT NULL THEN 1 ELSE 0 END) as games_with_scores,
                       MIN(game_date) as first_game,
                       MAX(game_date) as last_game
                FROM nfl_games 
                WHERE week = ? AND year = 2025
            ''', (current_week,))
            
            row = cursor.fetchone()
            total_games = row['total_games']
            final_games = row['final_games']
            games_with_scores = row['games_with_scores']
            first_game = row['first_game']
            last_game = row['last_game']
            
            if total_games == 0:
                self.log_issue(f"No games found for Week {current_week}")
                conn.close()
                return False
            
            # Check if we should have final games by now
            current_time = datetime.now()
            
            if first_game:
                first_game_dt = datetime.fromisoformat(first_game.replace('T', ' '))
                days_since_first = (current_time - first_game_dt).days
                
                if days_since_first > 0 and final_games == 0:
                    self.log_issue(f"Week {current_week}: {days_since_first} days since first game, but NO games marked final")
                    self.log_issue("This indicates background updater is NOT working")
                elif days_since_first > 0 and final_games > 0:
                    self.log_success(f"Week {current_week}: {final_games}/{total_games} games completed")
                else:
                    self.log_success(f"Week {current_week}: Games haven't started yet")
            
            # Check picks scoring status
            cursor.execute('''
                SELECT COUNT(*) as total_picks,
                       SUM(CASE WHEN is_correct IS NOT NULL THEN 1 ELSE 0 END) as scored_picks
                FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE g.week = ? AND g.year = 2025
            ''', (current_week,))
            
            pick_row = cursor.fetchone()
            total_picks = pick_row['total_picks']
            scored_picks = pick_row['scored_picks']
            
            if total_picks > 0:
                unscored_picks = total_picks - scored_picks
                if final_games > 0 and unscored_picks > 0:
                    self.log_warning(f"Week {current_week}: {unscored_picks} picks unscored despite {final_games} final games")
                elif scored_picks > 0:
                    self.log_success(f"Week {current_week}: {scored_picks}/{total_picks} picks properly scored")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log_issue(f"Error checking current week status: {e}")
            return False
    
    def check_recent_update_activity(self):
        """Check if there has been recent automatic update activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check when games were last marked final
            cursor.execute('''
                SELECT MAX(game_date) as latest_final_game,
                       COUNT(*) as total_final_games
                FROM nfl_games 
                WHERE is_final = 1 AND year = 2025
            ''')
            
            row = cursor.fetchone()
            latest_final = row['latest_final_game']
            total_final = row['total_final_games']
            
            if latest_final:
                latest_dt = datetime.fromisoformat(latest_final.replace('T', ' '))
                days_since_latest = (datetime.now() - latest_dt).days
                
                if days_since_latest > 7:
                    self.log_warning(f"Latest final game was {days_since_latest} days ago")
                    self.log_warning("Background updater may not be running regularly")
                else:
                    self.log_success(f"Recent final game detected ({days_since_latest} days ago)")
            
            self.log_success(f"Total final games in 2025: {total_final}")
            conn.close()
            return True
            
        except Exception as e:
            self.log_issue(f"Error checking update activity: {e}")
            return False
    
    def check_espn_api_connectivity(self):
        """Test if ESPN API is accessible (basic connectivity test)"""
        try:
            # Simple test to see if ESPN is reachable
            response = requests.get('https://espn.com', timeout=10)
            if response.status_code == 200:
                self.log_success("ESPN website is accessible")
                return True
            else:
                self.log_warning(f"ESPN website returned status {response.status_code}")
                return False
                
        except requests.exceptions.SSLError:
            self.log_issue("SSL certificate error when connecting to ESPN")
            self.log_issue("This may prevent background updater from working")
            return False
        except requests.exceptions.ConnectionError:
            self.log_issue("Cannot connect to ESPN - network issue")
            return False
        except Exception as e:
            self.log_warning(f"ESPN connectivity test failed: {e}")
            return False
    
    def check_background_processes(self):
        """Check if background updater process might be running"""
        try:
            import subprocess
            
            # Check for Python processes (Windows compatible)
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True, timeout=10)
            
            if 'python.exe' in result.stdout:
                self.log_success("Python processes detected on system")
                # Note: Can't easily determine if it's background_updater specifically
                self.log_warning("Cannot verify if background_updater.py is specifically running")
            else:
                self.log_warning("No Python processes detected")
                
        except subprocess.TimeoutExpired:
            self.log_warning("Process check timed out")
        except Exception as e:
            self.log_warning(f"Cannot check background processes: {e}")
    
    def generate_weekly_report(self):
        """Generate comprehensive weekly status report"""
        print("=" * 80)
        print("🏈 WEEKLY AUTO-MONITOR REPORT")
        print("=" * 80)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all checks
        db_ok = self.check_database_connectivity()
        if db_ok:
            self.check_current_week_status()
            self.check_recent_update_activity()
        
        self.check_espn_api_connectivity()
        self.check_background_processes()
        
        # Print results
        if self.successes:
            print("✅ SUCCESSES:")
            for success in self.successes:
                print(f"   {success}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
            print()
        
        if self.issues_found:
            print("❌ CRITICAL ISSUES:")
            for issue in self.issues_found:
                print(f"   {issue}")
            print()
        
        # Overall assessment
        print("📊 OVERALL ASSESSMENT:")
        if len(self.issues_found) == 0:
            if len(self.warnings) == 0:
                print("   🎉 EXCELLENT - System appears to be working perfectly!")
                assessment = "EXCELLENT"
            else:
                print("   👍 GOOD - System working with minor warnings")
                assessment = "GOOD"
        else:
            print("   🚨 ATTENTION REQUIRED - Critical issues detected")
            assessment = "NEEDS_ATTENTION"
        
        print()
        print("🔧 RECOMMENDED ACTIONS:")
        
        if assessment == "EXCELLENT":
            print("   • No action needed - system is working properly")
            print("   • Continue running this monitor weekly")
            
        elif assessment == "GOOD":
            print("   • Monitor warnings but no immediate action required")
            print("   • Check server logs if available")
            
        else:  # NEEDS_ATTENTION
            print("   • 🚨 URGENT: Background updater is likely not working")
            print("   • SSH to your server and check:")
            print("     - ps aux | grep background_updater")
            print("     - Check if background_updater.py is running")
            print("   • If not running, start it:")
            print("     - nohup python background_updater.py > updater.log 2>&1 &")
            print("   • Upload corrected database if needed")
            print("   • Run manual scoring as backup")
        
        print()
        print("=" * 80)
        
        return assessment
    
    def save_report_to_file(self, assessment):
        """Save report to file for tracking"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"weekly_monitor_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(f"Weekly Auto-Monitor Report\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Assessment: {assessment}\n\n")
                
                f.write("Successes:\n")
                for success in self.successes:
                    f.write(f"  {success}\n")
                f.write("\n")
                
                f.write("Warnings:\n")
                for warning in self.warnings:
                    f.write(f"  {warning}\n")
                f.write("\n")
                
                f.write("Issues:\n")
                for issue in self.issues_found:
                    f.write(f"  {issue}\n")
                
            print(f"📄 Report saved to: {filename}")
            
        except Exception as e:
            print(f"⚠️  Could not save report to file: {e}")

def main():
    """Run the weekly monitoring check"""
    print("🏈 Starting Weekly Auto-Monitor...")
    print()
    
    monitor = WeeklyAutoMonitor()
    assessment = monitor.generate_weekly_report()
    monitor.save_report_to_file(assessment)
    
    # Exit with appropriate code
    if assessment == "NEEDS_ATTENTION":
        sys.exit(1)  # Non-zero exit for automation/alerts
    else:
        sys.exit(0)  # Success

if __name__ == '__main__':
    main()
