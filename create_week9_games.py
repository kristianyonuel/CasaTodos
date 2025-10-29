#!/usr/bin/env python3
"""
Create Week 9 NFL Games
=======================

Since the automated API game creation isn't working, this script manually creates
Week 9 games based on the 2025 NFL schedule.

Week 9 is typically the first week of November (around November 3-10, 2025).

Created: October 29, 2025
"""

import sqlite3
from datetime import datetime, timedelta

def create_week9_games():
    print("🏈 Creating Week 9 NFL Games")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check if Week 9 games already exist
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 9 AND year = 2025")
    existing_games = cursor.fetchone()[0]
    
    if existing_games > 0:
        print(f"⚠️ Week 9 already has {existing_games} games. Delete them first? (y/n)")
        response = input().lower().strip()
        if response == 'y':
            cursor.execute("DELETE FROM nfl_games WHERE week = 9 AND year = 2025")
            print(f"✅ Deleted {existing_games} existing Week 9 games")
        else:
            print("❌ Cancelled - Week 9 games already exist")
            conn.close()
            return
    
    # Week 9 games (November 3-10, 2025 - estimated schedule)
    # Note: This is a placeholder schedule - you should replace with actual 2025 Week 9 games
    week9_games = [
        # Thursday Night Football - Nov 6, 2025
        {
            'away_team': 'CIN', 'home_team': 'BAL',
            'game_date': '2025-11-06 20:15:00',
            'is_thursday_night': True, 'tv_network': 'Prime Video'
        },
        
        # Sunday Games - Nov 9, 2025
        {
            'away_team': 'NE', 'home_team': 'MIA',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'NYJ', 'home_team': 'BUF',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'LV', 'home_team': 'PIT',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'JAX', 'home_team': 'CLE',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'CAR', 'home_team': 'ATL',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'TB', 'home_team': 'NO',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'WAS', 'home_team': 'NYG',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'TEN', 'home_team': 'IND',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'MIN', 'home_team': 'CHI',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'DET', 'home_team': 'GB',
            'game_date': '2025-11-09 13:00:00'
        },
        {
            'away_team': 'DEN', 'home_team': 'LAC',
            'game_date': '2025-11-09 16:05:00'
        },
        {
            'away_team': 'SF', 'home_team': 'SEA',
            'game_date': '2025-11-09 16:25:00'
        },
        {
            'away_team': 'DAL', 'home_team': 'PHI',
            'game_date': '2025-11-09 16:25:00'
        },
        
        # Sunday Night Football - Nov 9, 2025
        {
            'away_team': 'KC', 'home_team': 'LAR',
            'game_date': '2025-11-09 20:20:00',
            'is_sunday_night': True, 'tv_network': 'NBC'
        },
        
        # Monday Night Football - Nov 10, 2025
        {
            'away_team': 'ARI', 'home_team': 'HOU',
            'game_date': '2025-11-10 20:15:00',
            'is_monday_night': True, 'tv_network': 'ESPN'
        }
    ]
    
    print(f"📅 Creating {len(week9_games)} Week 9 games...")
    
    games_created = 0
    for game in week9_games:
        game_id = f"nfl_2025_w9_{game['away_team']}_{game['home_team']}"
        
        cursor.execute('''
            INSERT INTO nfl_games
            (week, year, game_id, away_team, home_team, game_date,
             is_thursday_night, is_monday_night, is_sunday_night,
             game_status, tv_network, is_final)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            9, 2025, game_id, 
            game['away_team'], game['home_team'], game['game_date'],
            game.get('is_thursday_night', False),
            game.get('is_monday_night', False),
            game.get('is_sunday_night', False),
            'scheduled', game.get('tv_network', 'TBD'), False
        ))
        
        games_created += 1
        
        # Show game info
        away = game['away_team']
        home = game['home_team']
        date = game['game_date']
        special = ""
        if game.get('is_thursday_night'):
            special = " (TNF)"
        elif game.get('is_sunday_night'):
            special = " (SNF)"
        elif game.get('is_monday_night'):
            special = " (MNF)"
            
        print(f"  {away} @ {home} - {date}{special}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Created {games_created} Week 9 games!")
    print()
    print("🎯 NEXT STEPS:")
    print("1. Verify the games in your admin panel")
    print("2. Update game times if needed (these are estimates)")
    print("3. Players can now make Week 9 picks!")
    print()
    print("⚠️ NOTE: This is a placeholder schedule.")
    print("Please verify actual Week 9 matchups and times from official NFL sources.")

if __name__ == "__main__":
    create_week9_games()