"""
Game management for NFL Fantasy League
"""

import sqlite3
import datetime
import requests
from nfl_schedule import generate_schedule_for_year, NFL_TEAMS

def create_emergency_games(week, year):
    """Create emergency minimal games when all other methods fail"""
    teams = list(NFL_TEAMS.values())[:16]  # Use first 16 teams
    
    if year >= 2025:
        season_start = datetime.datetime(2025, 9, 4)
    else:
        season_start = datetime.datetime(2024, 9, 5)
    
    week_start = season_start + datetime.timedelta(weeks=week-1)
    games = []
    
    # Thursday Night Football (except week 1)
    if week > 1:
        thursday_date = week_start + datetime.timedelta(days=3)
        games.append({
            'game_id': f'emergency_tnf_{week}_{year}',
            'week': week,
            'year': year,
            'home_team': teams[0],
            'away_team': teams[1],
            'game_date': thursday_date.replace(hour=20, minute=15),
            'is_monday_night': False,
            'is_thursday_night': True
        })
        used_teams = 2
    else:
        used_teams = 0
    
    # Sunday games
    sunday = week_start + datetime.timedelta(days=6)
    game_counter = 0
    
    for i in range(used_teams, min(used_teams + 12, len(teams)), 2):
        if i + 1 < len(teams):
            games.append({
                'game_id': f'emergency_sun_{week}_{year}_{game_counter}',
                'week': week,
                'year': year,
                'home_team': teams[i],
                'away_team': teams[i + 1],
                'game_date': sunday.replace(hour=13, minute=0),
                'is_monday_night': False,
                'is_thursday_night': False
            })
            game_counter += 1
    
    # Monday Night Football
    monday = week_start + datetime.timedelta(days=7)
    remaining_teams = [t for t in teams if t not in [g['home_team'] for g in games] + [g['away_team'] for g in games]]
    
    if len(remaining_teams) >= 2:
        games.append({
            'game_id': f'emergency_mnf_{week}_{year}',
            'week': week,
            'year': year,
            'home_team': remaining_teams[0],
            'away_team': remaining_teams[1],
            'game_date': monday.replace(hour=20, minute=15),
            'is_monday_night': True,
            'is_thursday_night': False
        })
    
    return games

def create_games_from_schedule(week, year):
    """Create NFL games from the schedule"""
    try:
        schedule = generate_schedule_for_year(year)
        if week not in schedule:
            return []
        
        games = []
        week_data = schedule[week]
        
        # Thursday games
        for game in week_data['thursday_games']:
            games.append({
                'week': week,
                'year': year,
                'game_id': f'tnf_{year}_week_{week}',
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'game_date': game['game_time'],
                'is_monday_night': False,
                'is_thursday_night': True
            })
        
        # Sunday games
        for i, game in enumerate(week_data['sunday_games']):
            games.append({
                'week': week,
                'year': year,
                'game_id': f'sun_{year}_week_{week}_game_{i+1}',
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'game_date': game['game_time'],
                'is_monday_night': False,
                'is_thursday_night': False
            })
        
        # Monday games
        for game in week_data['monday_games']:
            games.append({
                'week': week,
                'year': year,
                'game_id': f'mnf_{year}_week_{week}',
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'game_date': game['game_time'],
                'is_monday_night': True,
                'is_thursday_night': False
            })
        
        return games
        
    except Exception as e:
        print(f"Error creating games from schedule: {e}")
        return []

def ensure_games_exist(week, year):
    """Ensure games exist for the given week and year"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            conn.close()
            return existing_count
        
        # Create games using multiple methods
        games = create_games_from_schedule(week, year)
        
        if not games:
            games = create_emergency_games(week, year)
        
        # Insert games into database
        games_created = 0
        for game in games:
            try:
                game_date = game['game_date']
                if isinstance(game_date, datetime.datetime):
                    game_date_str = game_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    game_date_str = str(game_date)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO nfl_games 
                    (game_id, week, year, home_team, away_team, game_date, 
                     is_monday_night, is_thursday_night, home_score, away_score, is_final)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game.get('game_id', f'game_{week}_{year}_{games_created}'),
                    game['week'], 
                    game['year'], 
                    game['home_team'], 
                    game['away_team'], 
                    game_date_str,
                    game.get('is_monday_night', False), 
                    game.get('is_thursday_night', False),
                    game.get('home_score'),
                    game.get('away_score'),
                    game.get('is_final', False)
                ))
                games_created += 1
                
            except Exception as game_error:
                print(f"Error inserting game: {game_error}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"Successfully created {games_created} games for Week {week}")
        return games_created
        
    except Exception as e:
        print(f"Critical error in ensure_games_exist: {e}")
        return 0

def auto_populate_all_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        print(f"Processing {year} season...")
        
        for week in range(1, 19):
            try:
                conn = sqlite3.connect('nfl_fantasy.db')
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
                existing_games = cursor.fetchone()[0]
                conn.close()
                
                if existing_games == 0:
                    games_created = ensure_games_exist(week, year)
                    total_games_created += games_created
                    if games_created > 0:
                        print(f"   ✓ Created {games_created} games for {year} Week {week}")
                
            except Exception as e:
                print(f"   ❌ Error processing {year} Week {week}: {e}")
                continue
    
    print(f"🎯 Auto-population complete! Total new games created: {total_games_created}")
    return total_games_created
