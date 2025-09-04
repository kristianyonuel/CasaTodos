import sqlite3
from werkzeug.security import generate_password_hash
import datetime
import os

def create_full_database():
    """Create complete database with all tables and sample data"""
    print("Creating NFL Fantasy League Database...")
    
    # Remove existing database if it exists
    if os.path.exists('nfl_fantasy.db'):
        os.remove('nfl_fantasy.db')
        print("✓ Removed existing database")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Created users table")
    
    # NFL Games table
    cursor.execute('''
        CREATE TABLE nfl_games (
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
    print("✓ Created nfl_games table")
    
    # User Picks table
    cursor.execute('''
        CREATE TABLE user_picks (
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
    print("✓ Created user_picks table")
    
    # Weekly Results table
    cursor.execute('''
        CREATE TABLE weekly_results (
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
    print("✓ Created weekly_results table")
    
    # League Settings table
    cursor.execute('''
        CREATE TABLE league_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Created league_settings table")
    
    # Insert admin user
    admin_hash = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, password_hash, email, is_admin)
        VALUES (?, ?, ?, ?)
    ''', ('admin', admin_hash, 'admin@localhost.com', 1))
    print("✓ Created admin user")
    
    # Insert family users
    family_users = [
        ('dad', 'family123', 'dad@family.com'),
        ('mom', 'family123', 'mom@family.com'),
        ('son', 'family123', 'son@family.com'),
        ('daughter', 'family123', 'daughter@family.com'),
        ('uncle', 'family123', 'uncle@family.com'),
        ('aunt', 'family123', 'aunt@family.com')
    ]
    
    for username, password, email in family_users:
        user_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', (username, user_hash, email, 0))
    print(f"✓ Created {len(family_users)} family users")
    
    # Insert league settings
    settings = [
        ('weekly_fee', '5.00', 'Weekly pool entry fee'),
        ('season_fee', '10.00', 'Full season pool entry fee'),
        ('current_season', str(datetime.datetime.now().year), 'Current NFL season'),
        ('league_name', 'La Casa de Todos NFL League', 'Name of the fantasy league'),
        ('max_participants', '20', 'Maximum number of league participants'),
        ('elimination_advance_days', '7', 'Days before Saturday to submit elimination picks'),
        ('thursday_deadline_hours', '2', 'Hours before TNF to submit picks'),
        ('sunday_deadline_hours', '1', 'Hours before first Sunday game to submit picks')
    ]
    
    for setting_name, setting_value, description in settings:
        cursor.execute('''
            INSERT INTO league_settings (setting_name, setting_value, description)
            VALUES (?, ?, ?)
        ''', (setting_name, setting_value, description))
    print(f"✓ Created {len(settings)} league settings")
    
    # Insert sample NFL games for current week
    current_year = datetime.datetime.now().year
    current_week = 1  # Start with week 1
    
    sample_games = [
        (current_week, current_year, f'game_tnf_{current_week}', 'KC', 'BUF', 
         datetime.datetime(current_year, 9, 7, 20, 15), False, True),
        (current_week, current_year, f'game_sun1_{current_week}', 'DAL', 'NYG', 
         datetime.datetime(current_year, 9, 10, 13, 0), False, False),
        (current_week, current_year, f'game_sun2_{current_week}', 'SF', 'LAR', 
         datetime.datetime(current_year, 9, 10, 13, 0), False, False),
        (current_week, current_year, f'game_sun3_{current_week}', 'NE', 'MIA', 
         datetime.datetime(current_year, 9, 10, 16, 25), False, False),
        (current_week, current_year, f'game_mnf_{current_week}', 'GB', 'CHI', 
         datetime.datetime(current_year, 9, 11, 20, 15), True, False)
    ]
    
    for week, year, game_id, home, away, game_date, is_monday, is_thursday in sample_games:
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_monday_night, is_thursday_night)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (week, year, game_id, home, away, game_date, is_monday, is_thursday))
    print(f"✓ Created {len(sample_games)} sample games")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("DATABASE CREATION COMPLETED!")
    print("="*50)
    print(f"Database file: nfl_fantasy.db")
    print(f"Admin user: admin / admin123")
    print(f"Family users: dad, mom, son, daughter, uncle, aunt / family123")
    print(f"Sample games created for week {current_week}")
    print("="*50)

if __name__ == "__main__":
    create_full_database()
