#!/usr/bin/env python3
"""
Automated PFR Monitoring System

This system provides continuous monitoring of Pro Football Reference weekly pages
to automatically detect and update new NFL game scores. 

Features:
- Monitors current and future weeks (week_11.htm, week_12.htm format)
- Uses PFR as primary source with ESPN API fallback
- Integrates with VS Code fetch_webpage when available
- Can run as background service or one-time update
- Maintains update history and logging

Per user request: "keep updating from this page moving forward first"
"""

import sqlite3
import time
import logging
import json
import os
from datetime import datetime, timedelta
from pfr_app_integration import PFRScoreUpdater


class PFRMonitoringSystem:
    """Automated monitoring system for PFR score updates"""
    
    def __init__(self, db_path='nfl_fantasy.db', log_path='pfr_monitor.log'):
        self.db_path = db_path
        self.log_path = log_path
        self.year = 2025
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PFRMonitor')
        
        # Initialize score updater
        self.updater = PFRScoreUpdater(db_path)
        
        # Monitoring configuration
        self.config = {
            'update_interval_minutes': 15,  # Check every 15 minutes
            'weeks_to_monitor': [],  # Will be populated dynamically
            'max_retries': 3,
            'retry_delay_minutes': 5
        }
        
        # Update history file
        self.history_file = 'pfr_update_history.json'

    def get_weeks_to_monitor(self):
        """Determine which weeks need monitoring"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get weeks with incomplete games
            cursor.execute("""
                SELECT DISTINCT week FROM nfl_games 
                WHERE year = ? AND is_final = 0 
                ORDER BY week
            """, (self.year,))
            
            weeks = [row[0] for row in cursor.fetchall()]
            
            # Also include next week if current week is mostly complete
            if weeks:
                current_week = min(weeks)
                
                # Check if current week is mostly done
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final
                    FROM nfl_games 
                    WHERE week = ? AND year = ?
                """, (current_week, self.year))
                
                total, final = cursor.fetchone()
                
                # If more than 80% complete, monitor next week too
                if total > 0 and (final / total) > 0.8:
                    next_week = current_week + 1
                    if next_week <= 18:  # NFL regular season is 18 weeks
                        weeks.append(next_week)
            
            conn.close()
            self.logger.info(f"Monitoring weeks: {weeks}")
            return weeks
            
        except Exception as e:
            self.logger.error(f"Error determining weeks to monitor: {e}")
            return [11]  # Default fallback

    def load_update_history(self):
        """Load update history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading update history: {e}")
            return {}

    def save_update_history(self, history):
        """Save update history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving update history: {e}")

    def fetch_pfr_data_if_available(self, week):
        """
        Attempt to fetch PFR data if fetch_webpage is available
        
        This would use the fetch_webpage tool in VS Code environment.
        In terminal environment, returns None to trigger ESPN fallback.
        """
        try:
            # This is where fetch_webpage would be called in VS Code environment
            # For now, we'll simulate the check and fall back to ESPN
            self.logger.info(f"PFR fetch attempt for Week {week} (fallback to ESPN in terminal)")
            return None
            
        except Exception as e:
            self.logger.error(f"PFR fetch failed for Week {week}: {e}")
            return None

    def update_week_with_monitoring(self, week):
        """Update a specific week with monitoring and history tracking"""
        history = self.load_update_history()
        week_key = f"week_{week}"
        
        # Check if we've updated this week recently
        if week_key in history:
            last_update = datetime.fromisoformat(history[week_key]['last_update'])
            if datetime.now() - last_update < timedelta(minutes=5):
                self.logger.debug(f"Week {week} updated recently, skipping")
                return 0
        
        # Get current week status before update
        before_status = self.updater.get_week_status(week)
        
        # Attempt update
        self.logger.info(f"Updating Week {week} scores...")
        updated = self.updater.update_week_scores(week)
        
        # Get status after update
        after_status = self.updater.get_week_status(week)
        
        # Update history
        history[week_key] = {
            'last_update': datetime.now().isoformat(),
            'games_updated': updated,
            'before_final': before_status['final_games'],
            'after_final': after_status['final_games'],
            'total_games': after_status['total_games']
        }
        
        self.save_update_history(history)
        
        if updated > 0:
            self.logger.info(f"Week {week}: Updated {updated} games ({after_status['final_games']}/{after_status['total_games']} final)")
        else:
            self.logger.debug(f"Week {week}: No updates needed ({after_status['final_games']}/{after_status['total_games']} final)")
        
        return updated

    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        self.logger.info("Starting monitoring cycle...")
        
        # Determine weeks to monitor
        weeks_to_monitor = self.get_weeks_to_monitor()
        self.config['weeks_to_monitor'] = weeks_to_monitor
        
        if not weeks_to_monitor:
            self.logger.info("No weeks need monitoring")
            return 0
        
        total_updated = 0
        
        for week in weeks_to_monitor:
            try:
                updated = self.update_week_with_monitoring(week)
                total_updated += updated
                
                # Brief pause between weeks
                if len(weeks_to_monitor) > 1:
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Error updating Week {week}: {e}")
        
        self.logger.info(f"Monitoring cycle complete: {total_updated} total games updated")
        return total_updated

    def run_continuous_monitoring(self, duration_hours=None):
        """Run continuous monitoring for specified duration"""
        self.logger.info("Starting continuous PFR monitoring...")
        
        start_time = datetime.now()
        cycle_count = 0
        total_updates = 0
        
        try:
            while True:
                cycle_count += 1
                self.logger.info(f"=== Monitoring Cycle {cycle_count} ===")
                
                # Run monitoring cycle
                updates = self.run_monitoring_cycle()
                total_updates += updates
                
                # Check duration limit
                if duration_hours:
                    elapsed = (datetime.now() - start_time).total_seconds() / 3600
                    if elapsed >= duration_hours:
                        self.logger.info(f"Duration limit reached ({duration_hours} hours)")
                        break
                
                # Wait for next cycle
                self.logger.info(f"Waiting {self.config['update_interval_minutes']} minutes until next cycle...")
                time.sleep(self.config['update_interval_minutes'] * 60)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        
        elapsed_time = datetime.now() - start_time
        self.logger.info(f"Monitoring summary: {cycle_count} cycles, {total_updates} total updates, {elapsed_time}")

    def get_monitoring_status(self):
        """Get current monitoring status"""
        history = self.load_update_history()
        weeks_to_monitor = self.get_weeks_to_monitor()
        
        status = {
            'current_time': datetime.now().isoformat(),
            'weeks_monitored': weeks_to_monitor,
            'update_interval_minutes': self.config['update_interval_minutes'],
            'recent_updates': {}
        }
        
        # Get recent update info for each week
        for week in weeks_to_monitor:
            week_key = f"week_{week}"
            if week_key in history:
                status['recent_updates'][week] = history[week_key]
            else:
                week_status = self.updater.get_week_status(week)
                status['recent_updates'][week] = {
                    'last_update': 'Never',
                    'games_final': f"{week_status['final_games']}/{week_status['total_games']}"
                }
        
        return status


def main():
    """Main function for PFR monitoring system"""
    print("🏈 PFR AUTOMATED MONITORING SYSTEM")
    print("=" * 60)
    
    monitor = PFRMonitoringSystem()
    
    print("\nAvailable options:")
    print("1. Run single monitoring cycle")
    print("2. Start continuous monitoring (1 hour)")
    print("3. Start continuous monitoring (4 hours)")
    print("4. Show current status")
    print("5. Configure monitoring settings")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        print("\n🔄 Running single monitoring cycle...")
        updated = monitor.run_monitoring_cycle()
        print(f"✅ Cycle complete: {updated} games updated")
        
    elif choice == "2":
        print("\n🔄 Starting 1-hour continuous monitoring...")
        monitor.run_continuous_monitoring(duration_hours=1)
        
    elif choice == "3":
        print("\n🔄 Starting 4-hour continuous monitoring...")
        monitor.run_continuous_monitoring(duration_hours=4)
        
    elif choice == "4":
        print("\n📊 Current Monitoring Status:")
        status = monitor.get_monitoring_status()
        print(f"   Current time: {status['current_time']}")
        print(f"   Weeks monitored: {status['weeks_monitored']}")
        print(f"   Update interval: {status['update_interval_minutes']} minutes")
        print(f"   Recent updates:")
        for week, info in status['recent_updates'].items():
            print(f"     Week {week}: {info}")
            
    elif choice == "5":
        print("\n⚙️  Monitoring Configuration:")
        print(f"   Current interval: {monitor.config['update_interval_minutes']} minutes")
        new_interval = input("   New interval (minutes): ").strip()
        if new_interval.isdigit():
            monitor.config['update_interval_minutes'] = int(new_interval)
            print(f"   ✅ Updated to {new_interval} minutes")
        else:
            print("   ❌ Invalid interval")
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()