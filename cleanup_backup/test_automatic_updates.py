#!/usr/bin/env python3
"""Test script to validate automatic updates system"""

import sqlite3
from datetime import datetime
from background_updater import get_updater_status, start_background_updater
from espn_api_service import ESPNAPIService
from database_sync import update_live_scores_espn

def check_database_status():
    """Check current database status"""
    print("=== DATABASE STATUS ===")
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check Buffalo game
    cursor.execute('''
        SELECT game_id, home_team, away_team, home_score, away_score, is_final 
        FROM nfl_games 
        WHERE (home_team = "BUF" OR away_team = "BUF") AND week = 3 AND year = 2025
    ''')
    
    buffalo_game = cursor.fetchone()
    if buffalo_game:
        print(f"Buffalo Game: {buffalo_game[2]} @ {buffalo_game[1]}")
        print(f"Score: {buffalo_game[4]} - {buffalo_game[3]}")
        print(f"Final: {buffalo_game[5]}")
        print(f"Game ID: {buffalo_game[0]}")
        
        # Check picks for this game
        cursor.execute('''
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                   SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong,
                   SUM(CASE WHEN is_correct IS NULL THEN 1 ELSE 0 END) as unscored
            FROM user_picks 
            WHERE game_id = ?
        ''', (buffalo_game[0],))
        
        pick_stats = cursor.fetchone()
        print(f"Pick Stats: {pick_stats[1]} correct, {pick_stats[2]} wrong, {pick_stats[3]} unscored out of {pick_stats[0]} total")
    else:
        print("Buffalo game not found!")
    
    conn.close()

def test_espn_api():
    """Test ESPN API for Buffalo game"""
    print("\n=== ESPN API TEST ===")
    try:
        api = ESPNAPIService()
        games = api.get_week_games(week=3, year=2025)
        print(f"ESPN API returned {len(games)} games for Week 3")
        
        # Find Buffalo game
        buffalo_games = [g for g in games if 'BUF' in [g.get('home_team'), g.get('away_team')]]
        if buffalo_games:
            game = buffalo_games[0]
            print("Buffalo Game from ESPN:")
            print(f"  Away: {game.get('away_team')} ({game.get('away_score')})")
            print(f"  Home: {game.get('home_team')} ({game.get('home_score')})")
            print(f"  Final: {game.get('is_final')}")
            print(f"  Status: {game.get('status', 'Unknown')}")
            return game
        else:
            print("Buffalo game not found in ESPN data")
            return None
    except Exception as e:
        print(f"ESPN API Error: {e}")
        return None

def test_background_updater():
    """Test background updater status and startup"""
    print("\n=== BACKGROUND UPDATER TEST ===")
    
    # Check current status
    status = get_updater_status()
    print("Current Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if not status.get('running'):
        print("\nStarting background updater...")
        start_background_updater()
        
        # Check status again
        new_status = get_updater_status()
        print("New Status:")
        for key, value in new_status.items():
            print(f"  {key}: {value}")

def test_manual_update():
    """Test manual database update"""
    print("\n=== MANUAL UPDATE TEST ===")
    try:
        print("Running manual ESPN score update...")
        result = update_live_scores_espn()
        print(f"Update result: {result}")
        
        # Check database again
        print("\nChecking database after manual update:")
        check_database_status()
        
    except Exception as e:
        print(f"Manual update error: {e}")

if __name__ == "__main__":
    print(f"Test started at: {datetime.now()}")
    
    # Step 1: Check current database status
    check_database_status()
    
    # Step 2: Test ESPN API
    espn_result = test_espn_api()
    
    # Step 3: Test background updater
    test_background_updater()
    
    # Step 4: If ESPN API works but database is stale, try manual update
    if espn_result and espn_result.get('is_final'):
        test_manual_update()
    
    print(f"\nTest completed at: {datetime.now()}")
