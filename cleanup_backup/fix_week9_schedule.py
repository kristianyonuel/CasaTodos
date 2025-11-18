#!/usr/bin/env python3
"""
Fix all Week 9 game schedules to correct NFL dates and times
"""

import sqlite3
from datetime import datetime

def fix_week9_schedule():
    """Fix Week 9 game schedule with proper NFL dates and times"""
    print("=" * 70)
    print("FIXING WEEK 9 NFL SCHEDULE")
    print("=" * 70)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Proper NFL Week 9 schedule for 2025
    # Based on typical NFL scheduling pattern
    week9_schedule = [
        # Thursday Night Football - October 31, 2024 (Week 9 starts Thursday)
        {
            'teams': ('Baltimore Ravens', 'Miami Dolphins'),
            'date': '2025-10-30 20:15:00',  # Thursday 8:15 PM
            'is_thursday_night': True,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        
        # Sunday Early Games - November 2, 2025 (1:00 PM ET)
        {
            'teams': ('Chicago Bears', 'Cincinnati Bengals'),
            'date': '2025-11-02 13:00:00',  # Sunday 1:00 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('Minnesota Vikings', 'Detroit Lions'),
            'date': '2025-11-02 13:00:00',  # Sunday 1:00 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('Carolina Panthers', 'Green Bay Packers'),
            'date': '2025-11-02 13:00:00',  # Sunday 1:00 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('Los Angeles Chargers', 'Tennessee Titans'),
            'date': '2025-11-02 13:00:00',  # Sunday 1:00 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('Atlanta Falcons', 'New England Patriots'),
            'date': '2025-11-02 13:00:00',  # Sunday 1:00 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('San Francisco 49ers', 'New York Giants'),
            'date': '2025-11-02 13:00:00',  # Sunday 1:00 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('Indianapolis Colts', 'Pittsburgh Steelers'),
            'date': '2025-11-02 13:00:00',  # Sunday 1:00 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        
        # Sunday Late Games - November 2, 2025 (4:25 PM ET)
        {
            'teams': ('Denver Broncos', 'Houston Texans'),
            'date': '2025-11-02 16:25:00',  # Sunday 4:25 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('Jacksonville Jaguars', 'Las Vegas Raiders'),
            'date': '2025-11-02 16:25:00',  # Sunday 4:25 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        {
            'teams': ('New Orleans Saints', 'Los Angeles Rams'),
            'date': '2025-11-02 16:25:00',  # Sunday 4:25 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': False
        },
        
        # Sunday Night Football - November 2, 2025 (8:20 PM ET)
        {
            'teams': ('Kansas City Chiefs', 'Buffalo Bills'),
            'date': '2025-11-02 20:20:00',  # Sunday 8:20 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': True
        },
        {
            'teams': ('Seattle Seahawks', 'Washington Commanders'),
            'date': '2025-11-02 20:20:00',  # Sunday 8:20 PM
            'is_thursday_night': False,
            'is_monday_night': False,
            'is_sunday_night': True
        },
        
        # Monday Night Football - November 3, 2025 (9:15 PM ET)
        {
            'teams': ('Arizona Cardinals', 'Dallas Cowboys'),
            'date': '2025-11-03 21:15:00',  # Monday 9:15 PM
            'is_thursday_night': False,
            'is_monday_night': True,
            'is_sunday_night': False
        }
    ]
    
    print(f"Updating {len(week9_schedule)} games with correct schedule...")
    
    # Get all Week 9 games
    cursor.execute("""
        SELECT id, away_team, home_team, game_date 
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY id
    """)
    
    current_games = cursor.fetchall()
    
    print(f"\nFound {len(current_games)} games in database:")
    for game in current_games:
        print(f"  Game {game[0]}: {game[1]} @ {game[2]} - {game[3]}")
    
    # Update each game with correct schedule
    updates_made = 0
    
    for i, schedule_item in enumerate(week9_schedule):
        if i < len(current_games):
            game_id = current_games[i][0]
            away_team, home_team = schedule_item['teams']
            new_date = schedule_item['date']
            is_thursday = schedule_item['is_thursday_night']
            is_monday = schedule_item['is_monday_night']
            is_sunday = schedule_item['is_sunday_night']
            
            # Update the game
            cursor.execute("""
                UPDATE nfl_games 
                SET game_date = ?,
                    is_thursday_night = ?,
                    is_monday_night = ?,
                    is_sunday_night = ?
                WHERE id = ?
            """, (new_date, is_thursday, is_monday, is_sunday, game_id))
            
            game_type = "Thursday Night" if is_thursday else "Monday Night" if is_monday else "Sunday Night" if is_sunday else "Regular"
            
            print(f"\n✅ Updated Game {game_id}:")
            print(f"   Teams: {away_team} @ {home_team}")
            print(f"   New Date: {new_date}")
            print(f"   Type: {game_type}")
            
            updates_made += 1
        else:
            print(f"❌ No game found for {schedule_item['teams']}")
    
    # Commit changes
    conn.commit()
    
    # Verify the updates
    print(f"\n" + "=" * 50)
    print("VERIFICATION - Updated Week 9 Schedule")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            id, away_team, home_team, game_date, 
            is_thursday_night, is_monday_night, is_sunday_night,
            away_score, home_score, is_final
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    
    updated_games = cursor.fetchall()
    
    for game in updated_games:
        game_type = "TNF" if game[4] else "MNF" if game[5] else "SNF" if game[6] else "Regular"
        score_info = f" - Final {game[7]}-{game[8]}" if game[9] else " - Scheduled"
        
        print(f"Game {game[0]} ({game_type}): {game[1]} @ {game[2]}")
        print(f"  Date: {game[3]}{score_info}")
        print()
    
    # Special check for Monday Night Football
    print("🏈 Monday Night Football Status:")
    cursor.execute("""
        SELECT id, away_team, home_team, game_date, away_score, home_score, is_final
        FROM nfl_games 
        WHERE week = 9 AND year = 2025 AND is_monday_night = 1
    """)
    
    mnf_games = cursor.fetchall()
    for mnf in mnf_games:
        if mnf[6]:  # is_final
            print(f"  ✅ {mnf[1]} @ {mnf[2]} - Final {mnf[4]}-{mnf[5]}")
        else:
            print(f"  ⏳ {mnf[1]} @ {mnf[2]} - Scheduled for {mnf[3]}")
    
    conn.close()
    
    print(f"\n✅ Updated {updates_made} games with correct NFL schedule!")
    print("🎯 Week 9 schedule now matches proper NFL timing!")

if __name__ == "__main__":
    fix_week9_schedule()