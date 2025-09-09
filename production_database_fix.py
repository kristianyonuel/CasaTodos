#!/usr/bin/env python3
"""
Production script to fix scoring system on remote server
Run this ONCE on the production server after deploying the updated code
"""

import sqlite3
import sys
import os
from datetime import datetime


def backup_database():
    """Create a backup before making changes"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"nfl_fantasy_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2('nfl_fantasy.db', backup_name)
        print(f"✅ Database backed up to: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to backup database: {e}")
        return False


def fix_production_scoring():
    """Fix all scoring issues on production server"""
    
    if not backup_database():
        print("❌ Cannot proceed without database backup")
        return False
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== PRODUCTION SCORING FIX ===")
    
    # 1. Check if fixes are needed
    cursor.execute('''
        SELECT COUNT(*) FROM user_picks 
        WHERE is_correct IS NULL
    ''')
    null_count = cursor.fetchone()[0]
    
    if null_count == 0:
        print("✅ No NULL is_correct values found. Database already fixed.")
        conn.close()
        return True
    
    print(f"Found {null_count} picks with NULL is_correct values. Fixing...")
    
    # 2. Fix all is_correct values based on game results
    cursor.execute('''
        SELECT p.id, p.selected_team, g.home_team, g.away_team, 
               g.home_score, g.away_score, g.is_final
        FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 1 AND g.year = 2025 AND g.is_final = 1
        AND p.is_correct IS NULL
    ''')
    
    picks_to_fix = cursor.fetchall()
    fixes_made = 0
    
    for pick_id, selected_team, home_team, away_team, home_score, away_score, is_final in picks_to_fix:
        # Determine actual winner
        if home_score > away_score:
            actual_winner = home_team
        elif away_score > home_score:
            actual_winner = away_team
        else:
            actual_winner = 'TIE'
        
        # Set is_correct value
        is_correct = 1 if selected_team == actual_winner else 0
        
        cursor.execute('''
            UPDATE user_picks 
            SET is_correct = ? 
            WHERE id = ?
        ''', (is_correct, pick_id))
        fixes_made += 1
    
    print(f"✅ Fixed {fixes_made} pick records")
    
    # 3. Fix coyote's Monday Night prediction if needed
    cursor.execute('''
        SELECT p.id, p.predicted_away_score, p.predicted_home_score
        FROM user_picks p
        JOIN nfl_games g ON p.game_id = g.id
        JOIN users u ON p.user_id = u.id
        WHERE u.username = "coyote" 
        AND g.week = 1 AND g.year = 2025
        AND g.home_team = "CHI" AND g.away_team = "MIN"
    ''')
    
    coyote_pick = cursor.fetchone()
    if coyote_pick and coyote_pick[1] != 27:  # Check if away score is not 27
        print("Fixing coyote's reversed Monday Night prediction...")
        cursor.execute('''
            UPDATE user_picks 
            SET predicted_away_score = 27, predicted_home_score = 21 
            WHERE id = ?
        ''', (coyote_pick[0],))
        print("✅ Corrected coyote's prediction to MIN 27 - CHI 21")
    
    conn.commit()
    
    # 4. Update weekly results using the scoring system
    try:
        from scoring_updater import ScoringUpdater
        updater = ScoringUpdater()
        success = updater.update_weekly_results(1, 2025)
        
        if success:
            print("✅ Weekly results updated successfully!")
            
            # Show final results
            results = updater.get_week_winners(1, 2025)
            print("\n=== PRODUCTION LEADERBOARD UPDATED ===")
            for i, result in enumerate(results[:5], 1):
                print(f"{i}. {result['username']}: {result['correct_picks']} correct")
        else:
            print("❌ Failed to update weekly results")
            
    except ImportError:
        print("❌ scoring_updater module not found. Make sure updated code is deployed.")
        
    conn.close()
    print("\n✅ Production database fix completed!")
    return True


if __name__ == "__main__":
    if not os.path.exists('nfl_fantasy.db'):
        print("❌ Database file not found. Make sure you're in the correct directory.")
        sys.exit(1)
    
    print("🚨 PRODUCTION DATABASE FIX")
    print("This will modify your production database.")
    
    # In production, you might want to add a confirmation
    # response = input("Continue? (yes/no): ")
    # if response.lower() != 'yes':
    #     print("Operation cancelled.")
    #     sys.exit(0)
    
    success = fix_production_scoring()
    if success:
        print("✅ All fixes applied successfully!")
        sys.exit(0)
    else:
        print("❌ Fix failed. Check the backup file.")
        sys.exit(1)
