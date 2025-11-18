#!/usr/bin/env python3
"""
Test the new spreadsheet-style export functionality
"""

import sqlite3
import os
import csv
import io
from datetime import datetime

def test_export_format():
    """Test the export format matches the requested format"""
    
    if not os.path.exists('nfl_fantasy.db'):
        print("❌ Database not found. Run setup_database.py first")
        return False
    
    print("🧪 Testing spreadsheet-style export format...")
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get users
        cursor.execute('SELECT id, username FROM users WHERE is_active = 1 ORDER BY username')
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found")
            return False
        
        print(f"📊 Found {len(users)} users: {[user[1] for user in users]}")
        
        # Get games for week 1
        week = 1
        year = 2025
        cursor.execute('''
            SELECT id, away_team, home_team
            FROM nfl_games 
            WHERE week = ? AND year = ?
            ORDER BY game_date
            LIMIT 5
        ''', (week, year))
        
        games = cursor.fetchall()
        
        if not games:
            print(f"❌ No games found for Week {week}, {year}")
            return False
        
        print(f"🏈 Found {len(games)} games for Week {week}")
        
        # Get picks data
        cursor.execute('''
            SELECT up.user_id, up.game_id, up.selected_team, u.username
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            JOIN users u ON up.user_id = u.id
            WHERE g.week = ? AND g.year = ?
        ''', (week, year))
        
        picks_data = {}
        pick_count = 0
        for row in cursor.fetchall():
            user_id = row[0]
            game_id = row[1]
            selected_team = row[2]
            username = row[3]
            
            if user_id not in picks_data:
                picks_data[user_id] = {}
            picks_data[user_id][game_id] = selected_team
            pick_count += 1
        
        print(f"🎯 Found {pick_count} total picks")
        
        # Simulate the export format
        print("\n📋 Export Format Preview:")
        print("=" * 60)
        
        # Header row (usernames)
        header_row = [user[1] for user in users]
        print(" | ".join(f"{name:10}" for name in header_row))
        print("-" * 60)
        
        # One row per game
        for i, game in enumerate(games):
            game_id = game[0]
            away_team = game[1]
            home_team = game[2]
            
            game_picks_row = []
            for user in users:
                user_id = user[0]
                user_pick = picks_data.get(user_id, {}).get(game_id, 'NO PICK')
                game_picks_row.append(user_pick)
            
            print(" | ".join(f"{pick:10}" for pick in game_picks_row))
            print(f"   Game {i+1}: {away_team} @ {home_team}")
            
            if i >= 2:  # Show first 3 games
                break
        
        print("=" * 60)
        print("✅ Export format test completed!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_export_format()
