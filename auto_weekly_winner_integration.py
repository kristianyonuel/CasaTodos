#!/usr/bin/env python3

"""
Integration module to automatically process weekly winners when games complete.
This should be called by the main app after score updates.
"""

import logging
from weekly_winner_manager import WeeklyWinnerManager

class AutoWeeklyWinnerProcessor:
    """Integrates weekly winner processing into the main application"""
    
    def __init__(self, db_path='nfl_fantasy.db'):
        self.manager = WeeklyWinnerManager(db_path)
        self.logger = logging.getLogger(__name__)
    
    def process_on_score_update(self, updated_week=None, year=2025):
        """
        Process weekly winners after score updates.
        This should be called from the score updater.
        
        Args:
            updated_week: Specific week that was updated (optional)
            year: Season year
        """
        try:
            if updated_week:
                # Check if this specific week is complete and needs processing
                if (self.manager.check_week_completion(updated_week, year) and
                    not self.manager.is_weekly_results_saved(updated_week, year)):
                    
                    self.logger.info(f"🏆 Week {updated_week} completed! Processing winner...")
                    success = self.manager.save_weekly_results(updated_week, year)
                    
                    if success:
                        # Get winner info for announcement
                        standings = self.manager.get_week_standings(updated_week, year)
                        if standings:
                            winner = standings[0]
                            user_id, username, total_picks, correct_picks = winner
                            
                            self.logger.info(f"🎉 WEEK {updated_week} WINNER: {username.upper()} with {correct_picks}/{total_picks} picks!")
                            
                            # Get Monday Night info
                            mnf_info = self.manager.get_monday_night_info(user_id, updated_week, year)
                            if mnf_info:
                                self.logger.info(f"Monday Night Pick: {mnf_info['pick']} - {'✅ CORRECT' if mnf_info['pick_correct'] else '❌ WRONG'}")
                            
                            return {
                                'week': updated_week,
                                'winner': username,
                                'score': f"{correct_picks}/{total_picks}",
                                'monday_night': mnf_info
                            }
                    else:
                        self.logger.error(f"Failed to save Week {updated_week} results")
            else:
                # Process all completed weeks
                processed = self.manager.process_completed_weeks(year=year)
                if processed:
                    self.logger.info(f"🏆 Processed completed weeks: {processed}")
                    return {'processed_weeks': processed}
            
        except Exception as e:
            self.logger.error(f"Error processing weekly winners: {e}")
            return None
    
    def get_season_summary(self, year=2025):
        """Get a summary of all weekly winners for the season"""
        import sqlite3
        
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT wr.week, u.username, wr.correct_picks, wr.total_picks
            FROM weekly_results wr
            JOIN users u ON wr.user_id = u.id
            WHERE wr.is_winner = 1 AND wr.year = ?
            ORDER BY wr.week
        ''', (year,))
        
        winners = cursor.fetchall()
        conn.close()
        
        # Count wins per user
        user_wins = {}
        weekly_details = []
        
        for week, username, correct, total in winners:
            if username not in user_wins:
                user_wins[username] = 0
            user_wins[username] += 1
            
            weekly_details.append({
                'week': week,
                'winner': username,
                'score': f"{correct}/{total}"
            })
        
        # Sort by wins
        sorted_users = sorted(user_wins.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'weekly_winners': weekly_details,
            'season_leaders': sorted_users
        }

# Example integration function for the main app
def integrate_with_score_updater():
    """
    Example of how to integrate this with the existing score updater.
    Add this call to your score_updater.py after scores are updated.
    """
    processor = AutoWeeklyWinnerProcessor()
    
    # Call this after score updates
    # processor.process_on_score_update(updated_week=current_week)
    
    return processor

def display_season_standings():
    """Display current season standings with weekly winners"""
    processor = AutoWeeklyWinnerProcessor()
    summary = processor.get_season_summary()
    
    print("🏆 2025 NFL FANTASY SEASON STANDINGS")
    print("=" * 80)
    
    print("\n📅 WEEKLY WINNERS:")
    print("-" * 50)
    for details in summary['weekly_winners']:
        print(f"Week {details['week']:2d}: {details['winner']:12s} ({details['score']})")
    
    print("\n🎯 SEASON LEADERS:")
    print("-" * 50)
    for username, wins in summary['season_leaders']:
        weeks = [str(w['week']) for w in summary['weekly_winners'] if w['winner'] == username]
        weeks_str = ", ".join([f"Week {w}" for w in weeks])
        print(f"{username:12s}: {wins} wins - {weeks_str}")

if __name__ == "__main__":
    # Test the integration
    display_season_standings()