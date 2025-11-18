#!/usr/bin/env python3
"""
Check Cowboys vs Cardinals game and today's games
"""

import sqlite3
from datetime import datetime

def check_todays_games():
    """Check what games are scheduled for today"""
    print("=" * 70)
    print("CHECKING TODAY'S GAMES (November 3, 2025)")
    print("=" * 70)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check all games for today's date
    print("\n1. All games scheduled for November 3, 2025:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT 
            id,
            week,
            away_team,
            home_team,
            game_date,
            game_status,
            away_score,
            home_score,
            is_final
        FROM nfl_games 
        WHERE DATE(game_date) = '2025-11-03'
        ORDER BY game_date
    """)
    
    todays_games = cursor.fetchall()
    
    if todays_games:
        print(f"Found {len(todays_games)} games for today:")
        for game in todays_games:
            status = f"Final {game['away_score']}-{game['home_score']}" if game['is_final'] else game['game_status']
            print(f"  Game {game['id']} (Week {game['week']}): {game['away_team']} @ {game['home_team']}")
            print(f"    Time: {game['game_date']}")
            print(f"    Status: {status}")
            print()
    else:
        print("❌ No games found for today (2025-11-03)")
    
    # Specifically check for Cowboys vs Cardinals
    print("\n2. Looking for Cowboys vs Cardinals game:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT 
            id,
            week,
            away_team,
            home_team,
            game_date,
            game_status,
            away_score,
            home_score,
            is_final
        FROM nfl_games 
        WHERE (away_team LIKE '%Cowboys%' OR home_team LIKE '%Cowboys%' OR
               away_team LIKE '%Dallas%' OR home_team LIKE '%Dallas%') AND
              (away_team LIKE '%Cardinals%' OR home_team LIKE '%Cardinals%' OR
               away_team LIKE '%Arizona%' OR home_team LIKE '%Arizona%')
        ORDER BY game_date DESC
        LIMIT 5
    """)
    
    cowboys_cardinals = cursor.fetchall()
    
    if cowboys_cardinals:
        print(f"Found Cowboys vs Cardinals games:")
        for game in cowboys_cardinals:
            game_date = datetime.fromisoformat(game['game_date'].replace('Z', '+00:00'))
            is_today = game_date.date() == datetime(2025, 11, 3).date()
            today_marker = " ⭐ TODAY" if is_today else ""
            
            status = f"Final {game['away_score']}-{game['home_score']}" if game['is_final'] else game['game_status']
            print(f"  Game {game['id']} (Week {game['week']}): {game['away_team']} @ {game['home_team']}{today_marker}")
            print(f"    Date: {game['game_date']}")
            print(f"    Status: {status}")
            print()
    else:
        print("❌ No Cowboys vs Cardinals game found in database")
    
    # Check Week 9 games specifically
    print("\n3. All Week 9 games with dates:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT 
            id,
            away_team,
            home_team,
            game_date,
            game_status,
            is_final
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    
    week9_games = cursor.fetchall()
    
    for game in week9_games:
        game_date = datetime.fromisoformat(game['game_date'].replace('Z', '+00:00'))
        is_today = game_date.date() == datetime(2025, 11, 3).date()
        today_marker = " ⭐ TODAY" if is_today else ""
        
        # Highlight Cowboys vs Cardinals
        is_cowboys_cardinals = (('Cowboys' in game['away_team'] or 'Dallas' in game['away_team']) and 
                               ('Cardinals' in game['home_team'] or 'Arizona' in game['home_team'])) or \
                              (('Cardinals' in game['away_team'] or 'Arizona' in game['away_team']) and 
                               ('Cowboys' in game['home_team'] or 'Dallas' in game['home_team']))
        
        special_marker = " 🏈 COWBOYS vs CARDINALS" if is_cowboys_cardinals else ""
        
        print(f"  Game {game['id']}: {game['away_team']} @ {game['home_team']}{today_marker}{special_marker}")
        print(f"    Date: {game['game_date']}")
        print(f"    Status: {game['game_status']}")
        print()
    
    # Check current week setting
    print("\n4. Checking current week setting:")
    print("-" * 50)
    
    cursor.execute("SELECT current_week FROM league_settings LIMIT 1")
    current_week_result = cursor.fetchone()
    current_week = current_week_result['current_week'] if current_week_result else 'Not set'
    
    print(f"Current week setting: {current_week}")
    
    # Check if there are any games visible to users today
    print("\n5. Games that should be visible for picks today:")
    print("-" * 50)
    
    # Games that haven't started yet or are in progress
    cursor.execute("""
        SELECT 
            id,
            week,
            away_team,
            home_team,
            game_date,
            game_status
        FROM nfl_games 
        WHERE DATE(game_date) >= '2025-11-03' 
        AND game_status IN ('scheduled', 'in_progress')
        ORDER BY game_date
        LIMIT 10
    """)
    
    upcoming_games = cursor.fetchall()
    
    if upcoming_games:
        print(f"Found {len(upcoming_games)} upcoming games:")
        for game in upcoming_games:
            game_date = datetime.fromisoformat(game['game_date'].replace('Z', '+00:00'))
            is_today = game_date.date() == datetime(2025, 11, 3).date()
            today_marker = " ⭐ TODAY" if is_today else ""
            
            print(f"  Week {game['week']}: {game['away_team']} @ {game['home_team']}{today_marker}")
            print(f"    Time: {game['game_date']}")
            print(f"    Status: {game['game_status']}")
            print()
    else:
        print("❌ No upcoming games found")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS")
    print("=" * 50)
    print("Checking if Cowboys vs Cardinals game exists and is properly scheduled...")

if __name__ == "__main__":
    check_todays_games()