#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def fix_nfl_fantasy_database():
    """Fix nfl_fantasy.db with proper Week 4 games and Cincinnati Bengals MNF"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("Fixing nfl_fantasy.db for correct Monday Night Football...")
    
    # First, clear existing Week 4 games
    cursor.execute('DELETE FROM nfl_games WHERE week = 4 AND year = 2025')
    deleted_count = cursor.rowcount
    print(f"Deleted {deleted_count} existing Week 4 games")
    
    # Insert correct Week 4 games with Cincinnati Bengals vs Denver Broncos as MNF
    print("Adding correct Week 4 games...")
    
    week4_games = [
        # Thursday Night Football - September 25th
        (201, 4, 2025, 'Dallas Cowboys', 'New York Giants', '2025-09-25 20:15:00', False, True, False),
        
        # Sunday games - September 28th
        (202, 4, 2025, 'Chicago Bears', 'Los Angeles Rams', '2025-09-28 13:00:00', False, False, False),
        (203, 4, 2025, 'Carolina Panthers', 'Atlanta Falcons', '2025-09-28 13:00:00', False, False, False),
        (204, 4, 2025, 'Indianapolis Colts', 'Pittsburgh Steelers', '2025-09-28 13:00:00', False, False, False),
        (205, 4, 2025, 'Minnesota Vikings', 'Green Bay Packers', '2025-09-28 13:00:00', False, False, False),
        (206, 4, 2025, 'New Orleans Saints', 'Tampa Bay Buccaneers', '2025-09-28 13:00:00', False, False, False),
        (207, 4, 2025, 'Philadelphia Eagles', 'Washington Commanders', '2025-09-28 13:00:00', False, False, False),
        (208, 4, 2025, 'Houston Texans', 'Jacksonville Jaguars', '2025-09-28 13:00:00', False, False, False),
        (209, 4, 2025, 'Miami Dolphins', 'Tennessee Titans', '2025-09-28 13:00:00', False, False, False),
        (210, 4, 2025, 'Cleveland Browns', 'Las Vegas Raiders', '2025-09-28 16:05:00', False, False, False),
        (211, 4, 2025, 'New England Patriots', 'San Francisco 49ers', '2025-09-28 16:25:00', False, False, False),
        (212, 4, 2025, 'Arizona Cardinals', 'Los Angeles Chargers', '2025-09-28 16:25:00', False, False, False),
        (213, 4, 2025, 'Kansas City Chiefs', 'New York Jets', '2025-09-28 20:20:00', False, False, False),  # Sunday Night
        
        # Monday Night Football - September 29th - THE CORRECT MNF GAME!
        (214, 4, 2025, 'Cincinnati Bengals', 'Denver Broncos', '2025-09-29 20:15:00', True, False, False),
    ]
    
    # Insert the games
    for game_data in week4_games:
        cursor.execute('''
            INSERT INTO nfl_games (game_id, week, year, away_team, home_team, game_date, is_monday_night, is_thursday_night, is_final)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', game_data)
    
    print(f"Added {len(week4_games)} correct Week 4 games")
    
    # Verify the Monday Night Football detection
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, is_monday_night,
               strftime('%w', game_date) as day_of_week
        FROM nfl_games 
        WHERE week = 4 AND year = 2025
        ORDER BY game_date
    ''')
    
    games = cursor.fetchall()
    print(f"\nWeek 4 Games Summary:")
    print(f"Total games: {len(games)}")
    
    # Find actual Monday games
    monday_games = [g for g in games if g[5] == '1']  # day_of_week = 1 for Monday
    mnf_flagged_games = [g for g in games if g[4] == 1]  # is_monday_night = True
    
    print(f"Games on Monday (day_of_week = 1): {len(monday_games)}")
    for game in monday_games:
        print(f"  {game[1]} @ {game[2]} - {game[3]}")
    
    print(f"Games flagged as MNF (is_monday_night = True): {len(mnf_flagged_games)}")
    for game in mnf_flagged_games:
        print(f"  {game[1]} @ {game[2]} - {game[3]}")
    
    # Test the MNF detection query that the app uses
    cursor.execute('''
        SELECT id, away_team, home_team FROM nfl_games 
        WHERE week = 4 AND year = 2025 
        AND strftime('%w', game_date) = '1'  -- Monday
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''')
    
    mnf_game = cursor.fetchone()
    if mnf_game:
        print(f"\nMNF Tiebreaker Game (detected by app): {mnf_game[1]} @ {mnf_game[2]} (ID: {mnf_game[0]})")
        
        if mnf_game[1] == 'Cincinnati Bengals' and mnf_game[2] == 'Denver Broncos':
            print("SUCCESS: Cincinnati Bengals @ Denver Broncos is correctly detected as MNF!")
        else:
            print("ERROR: Wrong game detected as MNF!")
    else:
        print("\nERROR: No Monday Night game found for tiebreaker!")
    
    conn.commit()
    conn.close()
    
    print("\nnfl_fantasy.db fix completed!")
    print("The Monday Night Football issue should now be resolved.")

if __name__ == '__main__':
    fix_nfl_fantasy_database()