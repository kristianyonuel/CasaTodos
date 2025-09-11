#!/usr/bin/env python3
"""
Monday Night Football Score Prediction Cleanup Tool

This script identifies and removes score predictions for games that are no longer
considered the actual Monday Night Football game due to the updated detection logic.

The new logic identifies the LATEST game on Monday as the actual MNF game,
not just any game with the is_monday_night flag set to 1.
"""

import sqlite3
from datetime import datetime
import sys
import os

# Add the app directory to the path so we can import the database config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_database_path():
    """Get the correct database path"""
    try:
        from config import DATABASE_PATH
        return DATABASE_PATH
    except ImportError:
        # Fallback to the known database file
        return 'nfl_fantasy.db'

def analyze_score_predictions():
    """Analyze existing score predictions and identify cleanup candidates"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔍 Analyzing Monday Night Football Score Predictions...")
    print("=" * 60)
    
    cleanup_candidates = []
    weeks_analyzed = []
    
    # Get all weeks that have games
    cursor.execute('''
        SELECT DISTINCT week, year 
        FROM nfl_games 
        WHERE year = 2025
        ORDER BY week
    ''')
    
    weeks = cursor.fetchall()
    
    for week_data in weeks:
        week = week_data['week']
        year = week_data['year']
        
        print(f"\n📅 Week {week}, {year}")
        print("-" * 30)
        
        # Find all Monday games for this week
        cursor.execute('''
            SELECT id, away_team, home_team, game_date, is_monday_night
            FROM nfl_games 
            WHERE week = ? AND year = ? 
            AND strftime('%w', game_date) = '1'  -- Monday games
            ORDER BY game_date ASC
        ''', (week, year))
        
        monday_games = cursor.fetchall()
        
        if not monday_games:
            print("  ℹ️  No Monday games found")
            continue
            
        if len(monday_games) == 1:
            print(f"  ✅ Only one Monday game: {monday_games[0]['away_team']} @ {monday_games[0]['home_team']}")
            continue
        
        print(f"  📊 Found {len(monday_games)} Monday games:")
        for i, game in enumerate(monday_games):
            print(f"    {i+1}. {game['away_team']} @ {game['home_team']} - {game['game_date']} (DB flag: {game['is_monday_night']})")
        
        # Find the actual Monday Night Football game using new logic
        cursor.execute('''
            SELECT id FROM nfl_games 
            WHERE week = ? AND year = ? 
            AND strftime('%w', game_date) = '1'  -- Monday
            ORDER BY game_date DESC, id DESC
            LIMIT 1
        ''', (week, year))
        
        actual_mnf_game = cursor.fetchone()
        actual_mnf_id = actual_mnf_game[0] if actual_mnf_game else None
        
        # Find the actual MNF game details
        actual_mnf_details = None
        for game in monday_games:
            if game['id'] == actual_mnf_id:
                actual_mnf_details = game
                break
        
        if actual_mnf_details:
            print(f"  🏈 Actual MNF (latest): {actual_mnf_details['away_team']} @ {actual_mnf_details['home_team']}")
        
        # Find games that have score predictions but are NOT the actual MNF game
        obsolete_games = [game for game in monday_games if game['id'] != actual_mnf_id]
        
        for obsolete_game in obsolete_games:
            # Check if users have score predictions for this obsolete game
            cursor.execute('''
                SELECT COUNT(*) as prediction_count
                FROM user_picks 
                WHERE game_id = ? 
                AND (predicted_home_score IS NOT NULL OR predicted_away_score IS NOT NULL)
            ''', (obsolete_game['id'],))
            
            prediction_count = cursor.fetchone()['prediction_count']
            
            if prediction_count > 0:
                print(f"  ⚠️  CLEANUP NEEDED: {obsolete_game['away_team']} @ {obsolete_game['home_team']} has {prediction_count} score predictions")
                
                # Get details of affected users
                cursor.execute('''
                    SELECT u.username, up.predicted_home_score, up.predicted_away_score
                    FROM user_picks up
                    JOIN users u ON up.user_id = u.id
                    WHERE up.game_id = ? 
                    AND (up.predicted_home_score IS NOT NULL OR up.predicted_away_score IS NOT NULL)
                    ORDER BY u.username
                ''', (obsolete_game['id'],))
                
                affected_users = cursor.fetchall()
                
                cleanup_candidates.append({
                    'week': week,
                    'year': year,
                    'game_id': obsolete_game['id'],
                    'game_label': f"{obsolete_game['away_team']} @ {obsolete_game['home_team']}",
                    'game_date': obsolete_game['game_date'],
                    'affected_users': affected_users,
                    'prediction_count': prediction_count
                })
                
                for user in affected_users:
                    print(f"      👤 {user['username']}: {user['predicted_away_score']}-{user['predicted_home_score']}")
            else:
                print(f"  ✅ {obsolete_game['away_team']} @ {obsolete_game['home_team']} has no score predictions")
        
        weeks_analyzed.append({'week': week, 'year': year, 'monday_games': len(monday_games)})
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 CLEANUP SUMMARY")
    print("=" * 60)
    
    if not cleanup_candidates:
        print("✅ No cleanup needed! All score predictions are for the correct MNF games.")
    else:
        print(f"⚠️  Found {len(cleanup_candidates)} games with obsolete score predictions:")
        total_affected_predictions = sum(candidate['prediction_count'] for candidate in cleanup_candidates)
        print(f"📊 Total obsolete predictions: {total_affected_predictions}")
        
        for candidate in cleanup_candidates:
            print(f"\n  Week {candidate['week']}: {candidate['game_label']}")
            print(f"    📅 {candidate['game_date']}")
            print(f"    👥 {candidate['prediction_count']} affected predictions")
    
    return cleanup_candidates

def cleanup_obsolete_predictions(cleanup_candidates, dry_run=True):
    """Clean up obsolete score predictions"""
    if not cleanup_candidates:
        print("✅ No cleanup needed!")
        return
    
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n🧹 {'DRY RUN: ' if dry_run else ''}CLEANING UP OBSOLETE SCORE PREDICTIONS")
    print("=" * 60)
    
    total_cleaned = 0
    
    for candidate in cleanup_candidates:
        game_label = candidate['game_label']
        game_id = candidate['game_id']
        week = candidate['week']
        
        print(f"\n📍 Week {week}: {game_label}")
        
        if dry_run:
            print(f"   🔍 Would remove {candidate['prediction_count']} score predictions")
            for user in candidate['affected_users']:
                print(f"      👤 {user['username']}: {user['predicted_away_score']}-{user['predicted_home_score']} → (removed)")
        else:
            # Actually remove the score predictions
            cursor.execute('''
                UPDATE user_picks 
                SET predicted_home_score = NULL, predicted_away_score = NULL
                WHERE game_id = ? 
                AND (predicted_home_score IS NOT NULL OR predicted_away_score IS NOT NULL)
            ''', (game_id,))
            
            cleaned_count = cursor.rowcount
            total_cleaned += cleaned_count
            
            print(f"   ✅ Removed {cleaned_count} score predictions")
            for user in candidate['affected_users']:
                print(f"      👤 {user['username']}: {user['predicted_away_score']}-{user['predicted_home_score']} → ✅ CLEANED")
    
    if not dry_run:
        conn.commit()
        print(f"\n🎉 Cleanup complete! Removed {total_cleaned} obsolete score predictions.")
    else:
        print(f"\n💡 This was a dry run. To actually clean up, run with --execute flag.")
    
    conn.close()

def main():
    """Main function"""
    print("🏈 Monday Night Football Score Prediction Cleanup Tool")
    print("=" * 60)
    print("This tool identifies and cleans up score predictions for games")
    print("that are no longer the actual Monday Night Football game.")
    print()
    
    # Analyze current state
    cleanup_candidates = analyze_score_predictions()
    
    if not cleanup_candidates:
        return
    
    # Check if user wants to execute cleanup
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("\n⚠️  EXECUTE MODE: Will actually modify the database!")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cleanup cancelled.")
            return
    
    # Perform cleanup
    cleanup_obsolete_predictions(cleanup_candidates, dry_run=dry_run)

if __name__ == '__main__':
    main()
