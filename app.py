from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import datetime
import os
import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from nfl_schedule_2025 import get_2025_2026_schedule, get_current_nfl_week_2025, NFL_TEAMS
from nfl_2025_official_schedule import get_official_2025_games, populate_all_2025_weeks
import pytz

app = Flask(__name__)
app.secret_key = 'nfl-fantasy-secret-key-2024'

AST = pytz.timezone('America/Puerto_Rico')  # Atlantic Standard Time

def auto_populate_nfl_games():
    """Auto-populate NFL games for all weeks when starting the application"""
    print("🏈 Auto-populating NFL games for current season...")
    
    current_year = datetime.datetime.now().year
    total_games_created = 0
    
    # Force create games for at least the first 5 weeks
    priority_weeks = [1, 2, 3, 4, 5]
    
    for week in priority_weeks:
        try:
            print(f"   Processing Priority Week {week}...")
            games_created = ensure_games_exist(week, current_year)
            total_games_created += games_created
            print(f"   ✓ Week {week}: {games_created} games")
                
        except Exception as e:
            print(f"   ❌ Error processing Week {week}: {e}")
            continue
    
    # Then process remaining weeks
    for week in range(6, 19):
        try:
            print(f"   Checking Week {week}...")
            
            # Check if games already exist
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, current_year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, current_year)
                total_games_created += games_created
                print(f"   ✓ Created {games_created} games for Week {week}")
            else:
                print(f"   ✓ Week {week} already has {existing_games} games")
                
        except Exception as e:
            print(f"   ❌ Error processing Week {week}: {e}")
            continue
    
    print(f"🎯 Auto-population complete! Total new games created: {total_games_created}")
    return total_games_created

def validate_nfl_games():
    """Validate that we have sufficient games in the database"""
    print("🔍 Validating NFL games in database...")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get total games count
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE year = ?', (datetime.datetime.now().year,))
    total_games = cursor.fetchone()[0]
    
    # Get games by week
    cursor.execute('''
        SELECT week, COUNT(*) as game_count 
        FROM nfl_games 
        WHERE year = ? 
        GROUP BY week 
        ORDER BY week
    ''', (datetime.datetime.now().year,))
    
    weeks_data = cursor.fetchall()
    conn.close()
    
    print(f"   📊 Total games in database: {total_games}")
    print(f"   📅 Weeks with games: {len(weeks_data)}/18")
    
    # Show games per week
    for week, count in weeks_data:
        print(f"      Week {week}: {count} games")
    
    # Validate minimum requirements - NFL typically has 256 regular season games total
    if total_games < 100:  # Should have at least 100 games for partial season
        print("   ⚠️  Warning: Low game count detected")
        return False
    
    # Check that weeks have reasonable number of games (12-16 per week)
    cursor.execute('''
        SELECT week, COUNT(*) as game_count 
        FROM nfl_games 
        WHERE year = ? AND game_count < 10
        GROUP BY week 
    ''', (datetime.datetime.now().year,))
    
    low_weeks = cursor.fetchall()
    if low_weeks:
        print(f"   ⚠️  Warning: {len(low_weeks)} weeks have fewer than 10 games")
        for week, count in low_weeks:
            print(f"      Week {week}: only {count} games")
    
    conn.close()
    
    print("   ✅ NFL games validation completed")
    return len(low_weeks) == 0

def get_week_game_count(week, year):
    """Get the number of games in a specific week"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
    game_count = cursor.fetchone()[0]
    
    conn.close()
    return game_count

def init_db():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            game_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_date TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            home_score INTEGER,
            away_score INTEGER,
            is_final BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # User Picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            selected_team TEXT NOT NULL,
            predicted_home_score INTEGER,
            predicted_away_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (game_id) REFERENCES nfl_games(id)
        )
    ''')
    
    # Weekly Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week INTEGER,
            year INTEGER,
            correct_picks INTEGER DEFAULT 0,
            total_picks INTEGER DEFAULT 0,
            monday_score_diff INTEGER,
            is_winner BOOLEAN DEFAULT FALSE,
            points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # League Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Schedule table (store schedule data in database)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_time TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, week, home_team, away_team)
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin@localhost.com', 1))
        print("✓ Created default admin user")
    
    # Create sample family users
    sample_users = [
        ('dad', 'family123', 'dad@family.com'),
        ('mom', 'family123', 'mom@family.com'),
        ('son', 'family123', 'son@family.com'),
        ('daughter', 'family123', 'daughter@family.com')
    ]
    
    for username, password, email in sample_users:
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        if cursor.fetchone()[0] == 0:
            user_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (username, user_hash, email, 0))
            print(f"✓ Created sample user: {username}")
    
    # Initialize league settings with updated costs
    default_settings = [
        ('weekly_fee', '20.00', 'Weekly pool entry fee'),
        ('season_fee', '20.00', 'Season initial entry fee'), 
        ('current_season', str(datetime.datetime.now().year), 'Current NFL season'),
        ('league_name', 'La Casa de Todos NFL League', 'Name of the fantasy league'),
        ('max_participants', '20', 'Maximum number of league participants'),
        ('elimination_advance_days', '7', 'Days before Saturday to submit elimination picks')
    ]
    
    for setting_name, setting_value, description in default_settings:
        cursor.execute('SELECT COUNT(*) FROM league_settings WHERE setting_name = ?', (setting_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO league_settings (setting_name, setting_value, description)
                VALUES (?, ?, ?)
            ''', (setting_name, setting_value, description))
            print(f"✓ Created setting: {setting_name}")
    
    # Create default schedules for 2024, 2025, 2026
    for year in [2024, 2025, 2026]:
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        if cursor.fetchone()[0] == 0:
            print(f"Creating default schedule for {year}")
            conn.close()
            create_default_schedule_in_db(year)
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
    
    conn.commit()
    conn.close()
    print("✓ Database initialization completed")

# NFL API functions
def get_current_nfl_week():
    """Get current NFL week based on actual NFL calendar"""
    try:
        now = datetime.datetime.now()
        
        if now.year >= 2025:
            return get_current_nfl_week_2025()
        
        # For 2024 and earlier
        if now.year <= 2024:
            season_start = datetime.datetime(2024, 9, 5)
            season_end = datetime.datetime(2025, 1, 8)
        else:
            season_start = datetime.datetime(now.year, 9, 7)
            season_end = datetime.datetime(now.year + 1, 1, 7)
        
        if now < season_start:
            return 1
        elif now > season_end:
            return 18
        else:
            days_since_start = (now - season_start).days
            week = min(18, max(1, (days_since_start // 7) + 1))
            return week
            
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        return 1

def create_nfl_games_from_schedule(week, year):
    """Create NFL games from database-stored schedule"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have schedule data for this year
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        schedule_count = cursor.fetchone()[0]
        
        if schedule_count == 0:
            print(f"No schedule data for {year}, creating default schedule...")
            create_default_schedule_in_db(year)
        
        # Get games from schedule table
        cursor.execute('''
            SELECT home_team, away_team, game_time, is_monday_night, is_thursday_night 
            FROM nfl_schedule 
            WHERE year = ? AND week = ?
            ORDER BY game_time
        ''', (year, week))
        
        schedule_games = cursor.fetchall()
        conn.close()
        
        games = []
        for i, (home_team, away_team, game_time, is_monday, is_thursday) in enumerate(schedule_games):
            # Parse game_time
            if isinstance(game_time, str):
                game_date = datetime.datetime.fromisoformat(game_time)
            else:
                game_date = game_time
            
            games.append({
                'week': week,
                'year': year,
                'game_id': f'sched_{year}_w{week}_g{i+1}',
                'home_team': home_team,
                'away_team': away_team,
                'game_date': game_date,
                'is_monday_night': bool(is_monday),
                'is_thursday_night': bool(is_thursday)
            })
        
        return games
        
    except Exception as e:
        print(f"Error creating games from database schedule: {e}")
        return create_sample_games(week, year)

def create_default_schedule_in_db(year):
    """Create default schedule in database for given year"""
    print(f"Creating default schedule in database for {year}")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # NFL Teams
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 
             'MIA', 'NYJ', 'CIN', 'CLE', 'HOU', 'IND', 'JAX', 'TEN', 'NO', 'ATL', 
             'CAR', 'TB', 'MIN', 'DET', 'PHI', 'WAS', 'ARI', 'SEA', 'CHI', 'NYG', 'LAR', 'LV']
    
    # Season start dates
    if year == 2025:
        season_start = datetime.datetime(2025, 9, 4)
    elif year == 2026:
        season_start = datetime.datetime(2026, 9, 10)
    else:
        season_start = datetime.datetime(year, 9, 5)
    
    for week in range(1, 19):
        week_start = season_start + datetime.timedelta(weeks=week-1)
        used_teams = set()
        
        # Thursday Night Football (weeks 2-17)
        if 2 <= week <= 17:
            thursday = week_start + datetime.timedelta(days=3)
            home_team = teams[(week * 2) % len(teams)]
            away_team = teams[(week * 2 + 1) % len(teams)]
            
            cursor.execute('''
                INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                VALUES (?, ?, ?, ?, ?, 1, 0)
            ''', (year, week, home_team, away_team, thursday.replace(hour=20, minute=15).isoformat()))
            
            used_teams.update([home_team, away_team])
        
        # Sunday games
        sunday = week_start + datetime.timedelta(days=6)
        available_teams = [t for t in teams if t not in used_teams]
        
        # Early Sunday games (1:00 PM)
        for i in range(0, min(16, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=13, minute=0).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Late Sunday games (4:25 PM)
        available_teams = [t for t in teams if t not in used_teams]
        for i in range(0, min(6, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=16, minute=25).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Monday Night Football (weeks 1-17)
        if week <= 17:
            remaining_teams = [t for t in teams if t not in used_teams]
            if len(remaining_teams) >= 2:
                monday = week_start + datetime.timedelta(days=7)
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 1)
                ''', (year, week, remaining_teams[0], remaining_teams[1], 
                      monday.replace(hour=20, minute=15).isoformat()))
    
    conn.commit()
    conn.close()
    print(f"Created schedule for {year} in database")

def init_db():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            game_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_date TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            home_score INTEGER,
            away_score INTEGER,
            is_final BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # User Picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            selected_team TEXT NOT NULL,
            predicted_home_score INTEGER,
            predicted_away_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (game_id) REFERENCES nfl_games(id)
        )
    ''')
    
    # Weekly Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week INTEGER,
            year INTEGER,
            correct_picks INTEGER DEFAULT 0,
            total_picks INTEGER DEFAULT 0,
            monday_score_diff INTEGER,
            is_winner BOOLEAN DEFAULT FALSE,
            points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # League Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Schedule table (store schedule data in database)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_time TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, week, home_team, away_team)
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin@localhost.com', 1))
        print("✓ Created default admin user")
    
    # Create sample family users
    sample_users = [
        ('dad', 'family123', 'dad@family.com'),
        ('mom', 'family123', 'mom@family.com'),
        ('son', 'family123', 'son@family.com'),
        ('daughter', 'family123', 'daughter@family.com')
    ]
    
    for username, password, email in sample_users:
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        if cursor.fetchone()[0] == 0:
            user_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (username, user_hash, email, 0))
            print(f"✓ Created sample user: {username}")
    
    # Initialize league settings with updated costs
    default_settings = [
        ('weekly_fee', '20.00', 'Weekly pool entry fee'),
        ('season_fee', '20.00', 'Season initial entry fee'), 
        ('current_season', str(datetime.datetime.now().year), 'Current NFL season'),
        ('league_name', 'La Casa de Todos NFL League', 'Name of the fantasy league'),
        ('max_participants', '20', 'Maximum number of league participants'),
        ('elimination_advance_days', '7', 'Days before Saturday to submit elimination picks')
    ]
    
    for setting_name, setting_value, description in default_settings:
        cursor.execute('SELECT COUNT(*) FROM league_settings WHERE setting_name = ?', (setting_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO league_settings (setting_name, setting_value, description)
                VALUES (?, ?, ?)
            ''', (setting_name, setting_value, description))
            print(f"✓ Created setting: {setting_name}")
    
    # Create default schedules for 2024, 2025, 2026
    for year in [2024, 2025, 2026]:
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        if cursor.fetchone()[0] == 0:
            print(f"Creating default schedule for {year}")
            conn.close()
            create_default_schedule_in_db(year)
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
    
    conn.commit()
    conn.close()
    print("✓ Database initialization completed")

# NFL API functions
def get_current_nfl_week():
    """Get current NFL week based on actual NFL calendar"""
    try:
        now = datetime.datetime.now()
        
        if now.year >= 2025:
            return get_current_nfl_week_2025()
        
        # For 2024 and earlier
        if now.year <= 2024:
            season_start = datetime.datetime(2024, 9, 5)
            season_end = datetime.datetime(2025, 1, 8)
        else:
            season_start = datetime.datetime(now.year, 9, 7)
            season_end = datetime.datetime(now.year + 1, 1, 7)
        
        if now < season_start:
            return 1
        elif now > season_end:
            return 18
        else:
            days_since_start = (now - season_start).days
            week = min(18, max(1, (days_since_start // 7) + 1))
            return week
            
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        return 1

def create_nfl_games_from_schedule(week, year):
    """Create NFL games from database-stored schedule"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have schedule data for this year
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        schedule_count = cursor.fetchone()[0]
        
        if schedule_count == 0:
            print(f"No schedule data for {year}, creating default schedule...")
            create_default_schedule_in_db(year)
        
        # Get games from schedule table
        cursor.execute('''
            SELECT home_team, away_team, game_time, is_monday_night, is_thursday_night 
            FROM nfl_schedule 
            WHERE year = ? AND week = ?
            ORDER BY game_time
        ''', (year, week))
        
        schedule_games = cursor.fetchall()
        conn.close()
        
        games = []
        for i, (home_team, away_team, game_time, is_monday, is_thursday) in enumerate(schedule_games):
            # Parse game_time
            if isinstance(game_time, str):
                game_date = datetime.datetime.fromisoformat(game_time)
            else:
                game_date = game_time
            
            games.append({
                'week': week,
                'year': year,
                'game_id': f'sched_{year}_w{week}_g{i+1}',
                'home_team': home_team,
                'away_team': away_team,
                'game_date': game_date,
                'is_monday_night': bool(is_monday),
                'is_thursday_night': bool(is_thursday)
            })
        
        return games
        
    except Exception as e:
        print(f"Error creating games from database schedule: {e}")
        return create_sample_games(week, year)

def create_default_schedule_in_db(year):
    """Create default schedule in database for given year"""
    print(f"Creating default schedule in database for {year}")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # NFL Teams
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 
             'MIA', 'NYJ', 'CIN', 'CLE', 'HOU', 'IND', 'JAX', 'TEN', 'NO', 'ATL', 
             'CAR', 'TB', 'MIN', 'DET', 'PHI', 'WAS', 'ARI', 'SEA', 'CHI', 'NYG', 'LAR', 'LV']
    
    # Season start dates
    if year == 2025:
        season_start = datetime.datetime(2025, 9, 4)
    elif year == 2026:
        season_start = datetime.datetime(2026, 9, 10)
    else:
        season_start = datetime.datetime(year, 9, 5)
    
    for week in range(1, 19):
        week_start = season_start + datetime.timedelta(weeks=week-1)
        used_teams = set()
        
        # Thursday Night Football (weeks 2-17)
        if 2 <= week <= 17:
            thursday = week_start + datetime.timedelta(days=3)
            home_team = teams[(week * 2) % len(teams)]
            away_team = teams[(week * 2 + 1) % len(teams)]
            
            cursor.execute('''
                INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                VALUES (?, ?, ?, ?, ?, 1, 0)
            ''', (year, week, home_team, away_team, thursday.replace(hour=20, minute=15).isoformat()))
            
            used_teams.update([home_team, away_team])
        
        # Sunday games
        sunday = week_start + datetime.timedelta(days=6)
        available_teams = [t for t in teams if t not in used_teams]
        
        # Early Sunday games (1:00 PM)
        for i in range(0, min(16, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=13, minute=0).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Late Sunday games (4:25 PM)
        available_teams = [t for t in teams if t not in used_teams]
        for i in range(0, min(6, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=16, minute=25).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Monday Night Football (weeks 1-17)
        if week <= 17:
            remaining_teams = [t for t in teams if t not in used_teams]
            if len(remaining_teams) >= 2:
                monday = week_start + datetime.timedelta(days=7)
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 1)
                ''', (year, week, remaining_teams[0], remaining_teams[1], 
                      monday.replace(hour=20, minute=15).isoformat()))
    
    conn.commit()
    conn.close()
    print(f"Created schedule for {year} in database")

def init_db():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            game_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_date TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            home_score INTEGER,
            away_score INTEGER,
            is_final BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # User Picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            selected_team TEXT NOT NULL,
            predicted_home_score INTEGER,
            predicted_away_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (game_id) REFERENCES nfl_games(id)
        )
    ''')
    
    # Weekly Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week INTEGER,
            year INTEGER,
            correct_picks INTEGER DEFAULT 0,
            total_picks INTEGER DEFAULT 0,
            monday_score_diff INTEGER,
            is_winner BOOLEAN DEFAULT FALSE,
            points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # League Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Schedule table (store schedule data in database)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_time TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, week, home_team, away_team)
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin@localhost.com', 1))
        print("✓ Created default admin user")
    
    # Create sample family users
    sample_users = [
        ('dad', 'family123', 'dad@family.com'),
        ('mom', 'family123', 'mom@family.com'),
        ('son', 'family123', 'son@family.com'),
        ('daughter', 'family123', 'daughter@family.com')
    ]
    
    for username, password, email in sample_users:
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        if cursor.fetchone()[0] == 0:
            user_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (username, user_hash, email, 0))
            print(f"✓ Created sample user: {username}")
    
    # Initialize league settings with updated costs
    default_settings = [
        ('weekly_fee', '20.00', 'Weekly pool entry fee'),
        ('season_fee', '20.00', 'Season initial entry fee'), 
        ('current_season', str(datetime.datetime.now().year), 'Current NFL season'),
        ('league_name', 'La Casa de Todos NFL League', 'Name of the fantasy league'),
        ('max_participants', '20', 'Maximum number of league participants'),
        ('elimination_advance_days', '7', 'Days before Saturday to submit elimination picks')
    ]
    
    for setting_name, setting_value, description in default_settings:
        cursor.execute('SELECT COUNT(*) FROM league_settings WHERE setting_name = ?', (setting_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO league_settings (setting_name, setting_value, description)
                VALUES (?, ?, ?)
            ''', (setting_name, setting_value, description))
            print(f"✓ Created setting: {setting_name}")
    
    # Create default schedules for 2024, 2025, 2026
    for year in [2024, 2025, 2026]:
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        if cursor.fetchone()[0] == 0:
            print(f"Creating default schedule for {year}")
            conn.close()
            create_default_schedule_in_db(year)
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
    
    conn.commit()
    conn.close()
    print("✓ Database initialization completed")

# NFL API functions
def get_current_nfl_week():
    """Get current NFL week based on actual NFL calendar"""
    try:
        now = datetime.datetime.now()
        
        if now.year >= 2025:
            return get_current_nfl_week_2025()
        
        # For 2024 and earlier
        if now.year <= 2024:
            season_start = datetime.datetime(2024, 9, 5)
            season_end = datetime.datetime(2025, 1, 8)
        else:
            season_start = datetime.datetime(now.year, 9, 7)
            season_end = datetime.datetime(now.year + 1, 1, 7)
        
        if now < season_start:
            return 1
        elif now > season_end:
            return 18
        else:
            days_since_start = (now - season_start).days
            week = min(18, max(1, (days_since_start // 7) + 1))
            return week
            
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        return 1

def create_nfl_games_from_schedule(week, year):
    """Create NFL games from database-stored schedule"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have schedule data for this year
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        schedule_count = cursor.fetchone()[0]
        
        if schedule_count == 0:
            print(f"No schedule data for {year}, creating default schedule...")
            create_default_schedule_in_db(year)
        
        # Get games from schedule table
        cursor.execute('''
            SELECT home_team, away_team, game_time, is_monday_night, is_thursday_night 
            FROM nfl_schedule 
            WHERE year = ? AND week = ?
            ORDER BY game_time
        ''', (year, week))
        
        schedule_games = cursor.fetchall()
        conn.close()
        
        games = []
        for i, (home_team, away_team, game_time, is_monday, is_thursday) in enumerate(schedule_games):
            # Parse game_time
            if isinstance(game_time, str):
                game_date = datetime.datetime.fromisoformat(game_time)
            else:
                game_date = game_time
            
            games.append({
                'week': week,
                'year': year,
                'game_id': f'sched_{year}_w{week}_g{i+1}',
                'home_team': home_team,
                'away_team': away_team,
                'game_date': game_date,
                'is_monday_night': bool(is_monday),
                'is_thursday_night': bool(is_thursday)
            })
        
        return games
        
    except Exception as e:
        print(f"Error creating games from database schedule: {e}")
        return create_sample_games(week, year)

def create_default_schedule_in_db(year):
    """Create default schedule in database for given year"""
    print(f"Creating default schedule in database for {year}")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # NFL Teams
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 
             'MIA', 'NYJ', 'CIN', 'CLE', 'HOU', 'IND', 'JAX', 'TEN', 'NO', 'ATL', 
             'CAR', 'TB', 'MIN', 'DET', 'PHI', 'WAS', 'ARI', 'SEA', 'CHI', 'NYG', 'LAR', 'LV']
    
    # Season start dates
    if year == 2025:
        season_start = datetime.datetime(2025, 9, 4)
    elif year == 2026:
        season_start = datetime.datetime(2026, 9, 10)
    else:
        season_start = datetime.datetime(year, 9, 5)
    
    for week in range(1, 19):
        week_start = season_start + datetime.timedelta(weeks=week-1)
        used_teams = set()
        
        # Thursday Night Football (weeks 2-17)
        if 2 <= week <= 17:
            thursday = week_start + datetime.timedelta(days=3)
            home_team = teams[(week * 2) % len(teams)]
            away_team = teams[(week * 2 + 1) % len(teams)]
            
            cursor.execute('''
                INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                VALUES (?, ?, ?, ?, ?, 1, 0)
            ''', (year, week, home_team, away_team, thursday.replace(hour=20, minute=15).isoformat()))
            
            used_teams.update([home_team, away_team])
        
        # Sunday games
        sunday = week_start + datetime.timedelta(days=6)
        available_teams = [t for t in teams if t not in used_teams]
        
        # Early Sunday games (1:00 PM)
        for i in range(0, min(16, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=13, minute=0).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Late Sunday games (4:25 PM)
        available_teams = [t for t in teams if t not in used_teams]
        for i in range(0, min(6, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=16, minute=25).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Monday Night Football (weeks 1-17)
        if week <= 17:
            remaining_teams = [t for t in teams if t not in used_teams]
            if len(remaining_teams) >= 2:
                monday = week_start + datetime.timedelta(days=7)
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 1)
                ''', (year, week, remaining_teams[0], remaining_teams[1], 
                      monday.replace(hour=20, minute=15).isoformat()))
    
    conn.commit()
    conn.close()
    print(f"Created schedule for {year} in database")

def init_db():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            game_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_date TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            home_score INTEGER,
            away_score INTEGER,
            is_final BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # User Picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            selected_team TEXT NOT NULL,
            predicted_home_score INTEGER,
            predicted_away_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (game_id) REFERENCES nfl_games(id)
        )
    ''')
    
    # Weekly Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week INTEGER,
            year INTEGER,
            correct_picks INTEGER DEFAULT 0,
            total_picks INTEGER DEFAULT 0,
            monday_score_diff INTEGER,
            is_winner BOOLEAN DEFAULT FALSE,
            points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # League Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Schedule table (store schedule data in database)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_time TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, week, home_team, away_team)
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin@localhost.com', 1))
        print("✓ Created default admin user")
    
    # Create sample family users
    sample_users = [
        ('dad', 'family123', 'dad@family.com'),
        ('mom', 'family123', 'mom@family.com'),
        ('son', 'family123', 'son@family.com'),
        ('daughter', 'family123', 'daughter@family.com')
    ]
    
    for username, password, email in sample_users:
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        if cursor.fetchone()[0] == 0:
            user_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (username, user_hash, email, 0))
            print(f"✓ Created sample user: {username}")
    
    # Initialize league settings with updated costs
    default_settings = [
        ('weekly_fee', '20.00', 'Weekly pool entry fee'),
        ('season_fee', '20.00', 'Season initial entry fee'), 
        ('current_season', str(datetime.datetime.now().year), 'Current NFL season'),
        ('league_name', 'La Casa de Todos NFL League', 'Name of the fantasy league'),
        ('max_participants', '20', 'Maximum number of league participants'),
        ('elimination_advance_days', '7', 'Days before Saturday to submit elimination picks')
    ]
    
    for setting_name, setting_value, description in default_settings:
        cursor.execute('SELECT COUNT(*) FROM league_settings WHERE setting_name = ?', (setting_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO league_settings (setting_name, setting_value, description)
                VALUES (?, ?, ?)
            ''', (setting_name, setting_value, description))
            print(f"✓ Created setting: {setting_name}")
    
    # Create default schedules for 2024, 2025, 2026
    for year in [2024, 2025, 2026]:
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        if cursor.fetchone()[0] == 0:
            print(f"Creating default schedule for {year}")
            conn.close()
            create_default_schedule_in_db(year)
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
    
    conn.commit()
    conn.close()
    print("✓ Database initialization completed")

# NFL API functions
def get_current_nfl_week():
    """Get current NFL week based on actual NFL calendar"""
    try:
        now = datetime.datetime.now()
        
        if now.year >= 2025:
            return get_current_nfl_week_2025()
        
        # For 2024 and earlier
        if now.year <= 2024:
            season_start = datetime.datetime(2024, 9, 5)
            season_end = datetime.datetime(2025, 1, 8)
        else:
            season_start = datetime.datetime(now.year, 9, 7)
            season_end = datetime.datetime(now.year + 1, 1, 7)
        
        if now < season_start:
            return 1
        elif now > season_end:
            return 18
        else:
            days_since_start = (now - season_start).days
            week = min(18, max(1, (days_since_start // 7) + 1))
            return week
            
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        return 1

def create_nfl_games_from_schedule(week, year):
    """Create NFL games from database-stored schedule"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have schedule data for this year
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        schedule_count = cursor.fetchone()[0]
        
        if schedule_count == 0:
            print(f"No schedule data for {year}, creating default schedule...")
            create_default_schedule_in_db(year)
        
        # Get games from schedule table
        cursor.execute('''
            SELECT home_team, away_team, game_time, is_monday_night, is_thursday_night 
            FROM nfl_schedule 
            WHERE year = ? AND week = ?
            ORDER BY game_time
        ''', (year, week))
        
        schedule_games = cursor.fetchall()
        conn.close()
        
        games = []
        for i, (home_team, away_team, game_time, is_monday, is_thursday) in enumerate(schedule_games):
            # Parse game_time
            if isinstance(game_time, str):
                game_date = datetime.datetime.fromisoformat(game_time)
            else:
                game_date = game_time
            
            games.append({
                'week': week,
                'year': year,
                'game_id': f'sched_{year}_w{week}_g{i+1}',
                'home_team': home_team,
                'away_team': away_team,
                'game_date': game_date,
                'is_monday_night': bool(is_monday),
                'is_thursday_night': bool(is_thursday)
            })
        
        return games
        
    except Exception as e:
        print(f"Error creating games from database schedule: {e}")
        return create_sample_games(week, year)

def create_default_schedule_in_db(year):
    """Create default schedule in database for given year"""
    print(f"Creating default schedule in database for {year}")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # NFL Teams
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 
             'MIA', 'NYJ', 'CIN', 'CLE', 'HOU', 'IND', 'JAX', 'TEN', 'NO', 'ATL', 
             'CAR', 'TB', 'MIN', 'DET', 'PHI', 'WAS', 'ARI', 'SEA', 'CHI', 'NYG', 'LAR', 'LV']
    
    # Season start dates
    if year == 2025:
        season_start = datetime.datetime(2025, 9, 4)
    elif year == 2026:
        season_start = datetime.datetime(2026, 9, 10)
    else:
        season_start = datetime.datetime(year, 9, 5)
    
    for week in range(1, 19):
        week_start = season_start + datetime.timedelta(weeks=week-1)
        used_teams = set()
        
        # Thursday Night Football (weeks 2-17)
        if 2 <= week <= 17:
            thursday = week_start + datetime.timedelta(days=3)
            home_team = teams[(week * 2) % len(teams)]
            away_team = teams[(week * 2 + 1) % len(teams)]
            
            cursor.execute('''
                INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                VALUES (?, ?, ?, ?, ?, 1, 0)
            ''', (year, week, home_team, away_team, thursday.replace(hour=20, minute=15).isoformat()))
            
            used_teams.update([home_team, away_team])
        
        # Sunday games
        sunday = week_start + datetime.timedelta(days=6)
        available_teams = [t for t in teams if t not in used_teams]
        
        # Early Sunday games (1:00 PM)
        for i in range(0, min(16, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=13, minute=0).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Late Sunday games (4:25 PM)
        available_teams = [t for t in teams if t not in used_teams]
        for i in range(0, min(6, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=16, minute=25).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Monday Night Football (weeks 1-17)
        if week <= 17:
            remaining_teams = [t for t in teams if t not in used_teams]
            if len(remaining_teams) >= 2:
                monday = week_start + datetime.timedelta(days=7)
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 1)
                ''', (year, week, remaining_teams[0], remaining_teams[1], 
                      monday.replace(hour=20, minute=15).isoformat()))
    
    conn.commit()
    conn.close()
    print(f"Created schedule for {year} in database")

def init_db():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            game_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_date TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            home_score INTEGER,
            away_score INTEGER,
            is_final BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # User Picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            selected_team TEXT NOT NULL,
            predicted_home_score INTEGER,
            predicted_away_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (game_id) REFERENCES nfl_games(id)
        )
    ''')
    
    # Weekly Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week INTEGER,
            year INTEGER,
            correct_picks INTEGER DEFAULT 0,
            total_picks INTEGER DEFAULT 0,
            monday_score_diff INTEGER,
            is_winner BOOLEAN DEFAULT FALSE,
            points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # League Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NFL Schedule table (store schedule data in database)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            game_time TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, week, home_team, away_team)
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin@localhost.com', 1))
        print("✓ Created default admin user")
    
    # Create sample family users
    sample_users = [
        ('dad', 'family123', 'dad@family.com'),
        ('mom', 'family123', 'mom@family.com'),
        ('son', 'family123', 'son@family.com'),
        ('daughter', 'family123', 'daughter@family.com')
    ]
    
    for username, password, email in sample_users:
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
        if cursor.fetchone()[0] == 0:
            user_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (username, user_hash, email, 0))
            print(f"✓ Created sample user: {username}")
    
    # Initialize league settings with updated costs
    default_settings = [
        ('weekly_fee', '20.00', 'Weekly pool entry fee'),
        ('season_fee', '20.00', 'Season initial entry fee'), 
        ('current_season', str(datetime.datetime.now().year), 'Current NFL season'),
        ('league_name', 'La Casa de Todos NFL League', 'Name of the fantasy league'),
        ('max_participants', '20', 'Maximum number of league participants'),
        ('elimination_advance_days', '7', 'Days before Saturday to submit elimination picks')
    ]
    
    for setting_name, setting_value, description in default_settings:
        cursor.execute('SELECT COUNT(*) FROM league_settings WHERE setting_name = ?', (setting_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO league_settings (setting_name, setting_value, description)
                VALUES (?, ?, ?)
            ''', (setting_name, setting_value, description))
            print(f"✓ Created setting: {setting_name}")
    
    # Create default schedules for 2024, 2025, 2026
    for year in [2024, 2025, 2026]:
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        if cursor.fetchone()[0] == 0:
            print(f"Creating default schedule for {year}")
            conn.close()
            create_default_schedule_in_db(year)
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
    
    conn.commit()
    conn.close()
    print("✓ Database initialization completed")

# NFL API functions
def get_current_nfl_week():
    """Get current NFL week based on actual NFL calendar"""
    try:
        now = datetime.datetime.now()
        
        if now.year >= 2025:
            return get_current_nfl_week_2025()
        
        # For 2024 and earlier
        if now.year <= 2024:
            season_start = datetime.datetime(2024, 9, 5)
            season_end = datetime.datetime(2025, 1, 8)
        else:
            season_start = datetime.datetime(now.year, 9, 7)
            season_end = datetime.datetime(now.year + 1, 1, 7)
        
        if now < season_start:
            return 1
        elif now > season_end:
            return 18
        else:
            days_since_start = (now - season_start).days
            week = min(18, max(1, (days_since_start // 7) + 1))
            return week
            
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        return 1

def create_nfl_games_from_schedule(week, year):
    """Create NFL games from database-stored schedule"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have schedule data for this year
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        schedule_count = cursor.fetchone()[0]
        
        if schedule_count == 0:
            print(f"No schedule data for {year}, creating default schedule...")
            create_default_schedule_in_db(year)
        
        # Get games from schedule table
        cursor.execute('''
            SELECT home_team, away_team, game_time, is_monday_night, is_thursday_night 
            FROM nfl_schedule 
            WHERE year = ? AND week = ?
            ORDER BY game_time
        ''', (year, week))
        
        schedule_games = cursor.fetchall()
        conn.close()
        
        games = []
        for i, (home_team, away_team, game_time, is_monday, is_thursday) in enumerate(schedule_games):
            # Parse game_time
            if isinstance(game_time, str):
                game_date = datetime.datetime.fromisoformat(game_time)
            else:
                game_date = game_time
            
            games.append({
                'week': week,
                'year': year,
                'game_id': f'sched_{year}_w{week}_g{i+1}',
                'home_team': home_team,
                'away_team': away_team,
                'game_date': game_date,
                'is_monday_night': bool(is_monday),
                'is_thursday_night': bool(is_thursday)
            })
        
        return games
        
    except Exception as e:
        print(f"Error creating games from database schedule: {e}")
        return create_sample_games(week, year)

def create_default_schedule_in_db(year):
    """Create default schedule in database for given year"""
    print(f"Creating default schedule in database for {year}")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # NFL Teams
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 
             'MIA', 'NYJ', 'CIN', 'CLE', 'HOU', 'IND', 'JAX', 'TEN', 'NO', 'ATL', 
             'CAR', 'TB', 'MIN', 'DET', 'PHI', 'WAS', 'ARI', 'SEA', 'CHI', 'NYG', 'LAR', 'LV']
    
    # Season start dates
    if year == 2025:
        season_start = datetime.datetime(2025, 9, 4)
    elif year == 2026:
        season_start = datetime.datetime(2026, 9, 10)
    else:
        season_start = datetime.datetime(year, 9, 5)
    
    for week in range(1, 19):
        week_start = season_start + datetime.timedelta(weeks=week-1)
        used_teams = set()
        
        # Thursday Night Football (weeks 2-17)
        if 2 <= week <= 17:
            thursday = week_start + datetime.timedelta(days=3)
            home_team = teams[(week * 2) % len(teams)]
            away_team = teams[(week * 2 + 1) % len(teams)]
            
            cursor.execute('''
                INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                VALUES (?, ?, ?, ?, ?, 1, 0)
            ''', (year, week, home_team, away_team, thursday.replace(hour=20, minute=15).isoformat()))
            
            used_teams.update([home_team, away_team])
        
        # Sunday games
        sunday = week_start + datetime.timedelta(days=6)
        available_teams = [t for t in teams if t not in used_teams]
        
        # Early Sunday games (1:00 PM)
        for i in range(0, min(16, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=13, minute=0).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Late Sunday games (4:25 PM)
        available_teams = [t for t in teams if t not in used_teams]
        for i in range(0, min(6, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                ''', (year, week, available_teams[i], available_teams[i + 1], 
                      sunday.replace(hour=16, minute=25).isoformat()))
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Monday Night Football (weeks 1-17)
        if week <= 17:
            remaining_teams = [t for t in teams if t not in used_teams]
            if len(remaining_teams) >= 2:
                monday = week_start + datetime.timedelta(days=7)
                cursor.execute('''
                    INSERT INTO nfl_schedule (year, week, home_team, away_team, game_time, is_thursday_night, is_monday_night)
                    VALUES (?, ?, ?, ?, ?, 0, 1)
                ''', (year, week, remaining_teams[0], remaining_teams[1], 
                      monday.replace(hour=20, minute=15).isoformat()))
    
    conn.commit()
    conn.close()
    print(f"Created schedule for {year} in database")

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/create_schedule', methods=['POST'])
def admin_create_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        year = data.get('year')
        
        # Check if schedule already exists
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        if existing_count > 0:
            return jsonify({'error': f'Schedule for {year} already exists'}), 400
        
        # Create schedule
        create_default_schedule_in_db(year)
        
        return jsonify({'success': True, 'message': f'Schedule created for {year}'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['is_admin'] = user[2] == 1
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'is_admin': user[3]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/weekly_results')
def api_weekly_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT correct_picks, total_picks, monday_score_diff, is_winner, points 
        FROM weekly_results 
        WHERE user_id = ? AND year = ? AND week = ?
    ''', (user_id, year, week))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'correct_picks': result[0],
            'total_picks': result[1],
            'monday_score_diff': result[2],
            'is_winner': result[3],
            'points': result[4]
        })
    else:
        return jsonify({'error': 'Results not found'}), 404




















































































































































































































































































































































































































































































































        return jsonify({'error': str(e)}), 500    except Exception as e:            return jsonify({'success': True, 'message': f'Schedule created for {year}'})                create_default_schedule_in_db(year)        # Create schedule                    return jsonify({'error': f'Schedule for {year} already exists'}), 400        if existing_count > 0:                conn.close()        existing_count = cursor.fetchone()[0]        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))        cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')        # Check if schedule already exists                year = data.get('year')        data = request.get_json()    try:            return jsonify({'error': 'Admin access required'}), 403    if 'user_id' not in session or not session.get('is_admin'):def api_admin_create_schedule():@app.route('/api/admin/create_schedule', methods=['POST'])            return jsonify({'error': str(e)}), 500        except Exception as e:            )            return jsonify({'success': True, 'message': f'Schedule created for {year}'}                        create_default_schedule_in_db(year)            # Create schedule                            return jsonify({'error': f'Schedule for {year} already exists'}), 400            if existing_count > 0:                        conn.close()            existing_count = cursor.fetchone()[0]            cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))            cursor = conn.cursor()            conn = sqlite3.connect('nfl_fantasy.db')            # Check if schedule already exists                        year = data.get('year')            data = request.get_json()        try:    elif request.method == 'POST':            return jsonify({'error': str(e)}), 500        except Exception as e:                        return jsonify(schedule)            conn.close()                            })                    'is_thursday_night': bool(row[7])                    'is_monday_night': bool(row[6]),                    'game_time': row[5],                    'away_team': row[4],                    'home_team': row[3],                    'week': row[2],                    'year': row[1],                    'id': row[0],                schedule.append({            for row in cursor.fetchall():            schedule = []                        ''', (year,))                ORDER BY week, game_time                WHERE year = ?                FROM nfl_schedule                 SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night            cursor.execute('''                        cursor = conn.cursor()            conn = sqlite3.connect('nfl_fantasy.db')        try:                year = request.args.get('year', datetime.datetime.now().year, type=int)    if request.method == 'GET':            return jsonify({'error': 'Admin access required'}), 403    if 'user_id' not in session or not session.get('is_admin'):def api_admin_schedule():@app.route('/api/admin/schedule', methods=['GET', 'POST'])            return jsonify({'error': str(e)}), 500        except Exception as e:                    return jsonify({'success': True, 'message': 'User deleted successfully'})                        conn.close()            conn.commit()                        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))                        cursor = conn.cursor()            conn = sqlite3.connect('nfl_fantasy.db')        try:    elif request.method == 'DELETE':                return jsonify({'error': str(e)}), 500        except Exception as e:                    return jsonify({'success': True, 'message': 'User updated successfully'})                        conn.close()            conn.commit()                        ''', (username, email, is_admin, user_id))                WHERE id = ?                SET username = ?, email = ?, is_admin = ?                UPDATE users             cursor.execute('''                        cursor = conn.cursor()            conn = sqlite3.connect('nfl_fantasy.db')                        is_admin = data.get('is_admin')            email = data.get('email')            username = data.get('username')            data = request.get_json()        try:    elif request.method == 'POST':                return jsonify({'error': 'User not found'}), 404        else:            })                'is_admin': user[3]                'email': user[2],                'username': user[1],                'id': user[0],            return jsonify({        if user:                conn.close()        user = cursor.fetchone()        cursor.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,))                cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')    if request.method == 'GET':            return jsonify({'error': 'Admin access required'}), 403    if 'user_id' not in session or not session.get('is_admin'):def api_admin_user(user_id):@app.route('/api/admin/user/<int:user_id>', methods=['GET', 'POST', 'DELETE'])    return jsonify(result)            })            'is_admin': row[3]            'email': row[2],            'username': row[1],            'id': row[0],        result.append({    for row in users:    result = []        conn.close()    users = cursor.fetchall()    cursor.execute('SELECT id, username, email, is_admin FROM users')        cursor = conn.cursor()    conn = sqlite3.connect('nfl_fantasy.db')            return jsonify({'error': 'Admin access required'}), 403    if 'user_id' not in session or not session.get('is_admin'):def api_admin_users():@app.route('/api/admin/users')    return jsonify(summary)            })            'is_winner': row[4]            'points': row[3],            'total_picks': row[2],            'correct_picks': row[1],            'week': row[0],        summary.append({    for row in results:    summary = []        conn.close()    results = cursor.fetchall()        ''', (user_id, year))        ORDER BY week        WHERE user_id = ? AND year = ?        FROM weekly_results        SELECT week, correct_picks, total_picks, points, is_winner    cursor.execute('''        cursor = conn.cursor()    conn = sqlite3.connect('nfl_fantasy.db')        year = request.args.get('year', datetime.datetime.now().year, type=int)    user_id = session['user_id']            return jsonify({'error': 'Unauthorized'}), 401    if 'user_id' not in session:def api_season_summary():@app.route('/api/season_summary')    return jsonify(result)            })            'points': row[4]            'total_picks': row[3],            'correct_picks': row[2],            'username': row[1],            'user_id': row[0],        result.append({    for row in leaderboard:    result = []        conn.close()    leaderboard = cursor.fetchall()        ''', (year, week))        ORDER BY wr.points DESC, wr.correct_picks DESC        WHERE wr.year = ? AND wr.week = ?        JOIN weekly_results wr ON u.id = wr.user_id        FROM users u        SELECT u.id, u.username, wr.correct_picks, wr.total_picks, wr.points    cursor.execute('''        cursor = conn.cursor()    conn = sqlite3.connect('nfl_fantasy.db')        week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)    year = request.args.get('year', datetime.datetime.now().year, type=int)def api_weekly_leaderboard():@app.route('/api/weekly_leaderboard')        return jsonify({'error': str(e)}), 500    except Exception as e:            return jsonify({'success': True, 'message': 'Elimination pick saved'})                conn.close()        conn.commit()                ''', (user_id, elimination_pick.get('game_id'), elimination_pick.get('selected_team')))                created_at = CURRENT_TIMESTAMP                selected_team = excluded.selected_team,            ON CONFLICT(game_id) DO UPDATE SET            VALUES (?, ?, ?, CURRENT_TIMESTAMP)            INSERT INTO user_picks (user_id, game_id, selected_team, created_at)        cursor.execute('''        # Insert or update elimination pick                cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')                elimination_pick = data.get('pick')  # {game_id, selected_team}        year = data.get('year')        week = data.get('week')        data = request.get_json()    try:        user_id = session['user_id']            return jsonify({'error': 'Unauthorized'}), 401    if 'user_id' not in session:def api_elimination_picks():@app.route('/api/elimination_picks', methods=['POST'])        return jsonify({'error': str(e)}), 500    except Exception as e:            return jsonify({'success': True, 'message': 'Results updated successfully'})                conn.close()        conn.commit()                    ''', (home_score, away_score, game_id))                WHERE game_id = ?                SET home_score = ?, away_score = ?, is_final = 1                UPDATE nfl_games             cursor.execute('''                        away_score = result.get('away_score')            home_score = result.get('home_score')            game_id = result.get('game_id')        for result in results:        # Update game results                cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')                results = data.get('results')  # List of {game_id, home_score, away_score}        year = data.get('year')        week = data.get('week')        data = request.get_json()    try:            return jsonify({'error': 'Admin access required'}), 403    if 'user_id' not in session or not session.get('is_admin'):def api_update_results():@app.route('/api/update_results', methods=['POST'])    return jsonify(NFL_TEAMS)def api_nfl_teams():@app.route('/api/nfl_teams')    return jsonify(result)            })            'total_points': row[4]            'total_picks': row[3],            'total_wins': row[2],            'username': row[1],            'user_id': row[0],        result.append({    for row in standings:    result = []        conn.close()    standings = cursor.fetchall()        ''', (year,))        ORDER BY total_points DESC, total_wins DESC        GROUP BY u.id        WHERE u.is_admin = 0        LEFT JOIN weekly_results wr ON u.id = wr.user_id AND wr.year = ?        FROM users u               COALESCE(SUM(wr.points), 0) as total_points               COALESCE(SUM(wr.total_picks), 0) as total_picks,               COALESCE(SUM(CASE WHEN wr.is_winner = 1 THEN 1 ELSE 0 END), 0) as total_wins,        SELECT u.id, u.username,     cursor.execute('''        cursor = conn.cursor()    conn = sqlite3.connect('nfl_fantasy.db')        year = request.args.get('year', datetime.datetime.now().year, type=int)def api_standings():@app.route('/api/standings')        return jsonify({'error': str(e)}), 500    except Exception as e:            return jsonify({'success': True, 'message': 'Picks saved successfully'})                conn.close()        conn.commit()                    ''', (user_id, game_id, selected_team, predicted_home_score, predicted_away_score))                    created_at = CURRENT_TIMESTAMP                    predicted_away_score = excluded.predicted_away_score,                    predicted_home_score = excluded.predicted_home_score,                    selected_team = excluded.selected_team,                ON CONFLICT(game_id) DO UPDATE SET                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)                INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, created_at)            cursor.execute('''                        predicted_away_score = pick.get('predicted_away_score')            predicted_home_score = pick.get('predicted_home_score')            selected_team = pick.get('selected_team')            game_id = pick.get('game_id')        for pick in picks:        # Update or insert user picks                cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')                picks = data.get('picks')  # List of {game_id, selected_team, predicted_home_score, predicted_away_score}        year = data.get('year')        week = data.get('week')        data = request.get_json()    try:        user_id = session['user_id']            return jsonify({'error': 'Unauthorized'}), 401    if 'user_id' not in session:def api_user_picks():@app.route('/api/user_picks', methods=['POST'])        return jsonify({'error': str(e)}), 500    except Exception as e:            return jsonify({'success': True, 'message': 'User deleted successfully'})                conn.close()        conn.commit()        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))        cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')        # Delete user                user_id = data.get('user_id')        data = request.get_json()    try:            return jsonify({'error': 'Admin access required'}), 403    if 'user_id' not in session or not session.get('is_admin'):def api_delete_user():@app.route('/api/delete_user', methods=['POST'])        return jsonify({'error': str(e)}), 500    except Exception as e:            return jsonify({'success': True, 'message': 'User updated successfully'})                conn.close()        conn.commit()                    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))            password_hash = generate_password_hash(password)        if password:                    cursor.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))        if email:                cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')        # Update user details                password = data.get('password')        email = data.get('email')        data = request.get_json()    try:        user_id = session['user_id']            return jsonify({'error': 'Unauthorized'}), 401    if 'user_id' not in session:def api_update_user():@app.route('/api/update_user', methods=['POST'])        return jsonify({'error': str(e)}), 500    except Exception as e:            return jsonify({'success': True, 'message': 'User created successfully'})                conn.close()        conn.commit()        ''', (username, password_hash, email, 0))            VALUES (?, ?, ?, ?)            INSERT INTO users (username, password_hash, email, is_admin)        cursor.execute('''        password_hash = generate_password_hash(password)        # Create new user                    return jsonify({'error': 'Username already exists'}), 400            conn.close()        if cursor.fetchone()[0] > 0:        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))        cursor = conn.cursor()        conn = sqlite3.connect('nfl_fantasy.db')        # Check if user already exists                    return jsonify({'error': 'Username, password, and email are required'}), 400        if not username or not password or not email:        # Validate input                email = data.get('email')        password = data.get('password')        username = data.get('username')        data = request.get_json()    try:def api_create_user():@app.route('/api/create_user', methods=['POST'])    return jsonify(schedule)            })            'is_thursday_night': bool(game[4])            'is_monday_night': bool(game[3]),            'game_time': game[2],            'away_team': game[1],            'home_team': game[0],        schedule.append({    for game in games:    schedule = []        conn.close()    games = cursor.fetchall()        ''', (year, week))        ORDER BY game_time        WHERE year = ? AND week = ?        FROM nfl_schedule         SELECT home_team, away_team, game_time, is_monday_night, is_thursday_night     cursor.execute('''        cursor = conn.cursor()    conn = sqlite3.connect('nfl_fantasy.db')        week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)    year = request.args.get('year', datetime.datetime.now().year, type=int)def api_nfl_schedule():@app.route('/api/nfl_schedule')            season_end = datetime.datetime(2025, 1, 8)
        else:
           