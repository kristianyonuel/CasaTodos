"""
Database operations for NFL Fantasy League
"""

import sqlite3
import datetime
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the NFL Fantasy League database with enhanced features"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
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
    
    # Enhanced NFL Games table with additional fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            game_id TEXT UNIQUE,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_team_full_name TEXT,
            away_team_full_name TEXT,
            game_date TIMESTAMP NOT NULL,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            is_sunday_night BOOLEAN DEFAULT FALSE,
            home_score INTEGER,
            away_score INTEGER,
            is_final BOOLEAN DEFAULT FALSE,
            game_status TEXT DEFAULT 'scheduled',
            weather_conditions TEXT,
            tv_network TEXT,
            spread REAL,
            over_under REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Enhanced User Picks table with confidence levels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id INTEGER,
            selected_team TEXT NOT NULL,
            predicted_home_score INTEGER,
            predicted_away_score INTEGER,
            confidence_level INTEGER DEFAULT 1,
            pick_reason TEXT,
            is_locked BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (game_id) REFERENCES nfl_games(id) ON DELETE CASCADE,
            UNIQUE(user_id, game_id)
        )
    ''')
    
    # Enhanced Weekly Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week INTEGER,
            year INTEGER,
            correct_picks INTEGER DEFAULT 0,
            total_picks INTEGER DEFAULT 0,
            confidence_points INTEGER DEFAULT 0,
            monday_score_diff INTEGER,
            is_winner BOOLEAN DEFAULT FALSE,
            points INTEGER DEFAULT 0,
            rank INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, week, year)
        )
    ''')
    
    # League Settings table with more options
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_name TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            setting_type TEXT DEFAULT 'string',
            description TEXT,
            is_public BOOLEAN DEFAULT TRUE,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    ''')
    
    # User Statistics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            total_weeks_played INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0,
            best_week_score INTEGER DEFAULT 0,
            worst_week_score INTEGER DEFAULT 0,
            average_score REAL DEFAULT 0.0,
            monday_night_accuracy REAL DEFAULT 0.0,
            confidence_accuracy REAL DEFAULT 0.0,
            favorite_team TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT DEFAULT 'info',
            is_read BOOLEAN DEFAULT FALSE,
            action_url TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # League Seasons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER UNIQUE NOT NULL,
            name TEXT,
            start_date DATE,
            end_date DATE,
            is_active BOOLEAN DEFAULT FALSE,
            weekly_fee REAL DEFAULT 5.0,
            season_fee REAL DEFAULT 10.0,
            max_participants INTEGER DEFAULT 20,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Game Comments table for social features
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            comment TEXT NOT NULL,
            is_prediction BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES nfl_games(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
    
    # Initialize enhanced league settings
    enhanced_settings = [
        ('weekly_fee', '5.00', 'decimal', 'Weekly pool entry fee'),
        ('season_fee', '10.00', 'decimal', 'Full season pool entry fee'),
        ('current_season', str(datetime.datetime.now().year), 'integer', 'Current NFL season'),
        ('league_name', 'La Casa de Todos NFL League', 'string', 'Name of the fantasy league'),
        ('max_participants', '20', 'integer', 'Maximum number of league participants'),
        ('elimination_advance_days', '7', 'integer', 'Days before Saturday to submit elimination picks'),
        ('confidence_scoring', 'true', 'boolean', 'Enable confidence point scoring'),
        ('allow_tie_games', 'false', 'boolean', 'Allow tie game predictions'),
        ('notification_enabled', 'true', 'boolean', 'Enable push notifications'),
        ('auto_lock_picks', 'true', 'boolean', 'Auto-lock picks at game time'),
        ('show_live_scores', 'true', 'boolean', 'Show live game scores'),
        ('allow_comments', 'true', 'boolean', 'Allow user comments on games')
    ]
    
    for setting_name, setting_value, setting_type, description in enhanced_settings:
        cursor.execute('SELECT COUNT(*) FROM league_settings WHERE setting_name = ?', (setting_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO league_settings (setting_name, setting_value, setting_type, description)
                VALUES (?, ?, ?, ?)
            ''', (setting_name, setting_value, setting_type, description))
    
    # Initialize current season
    current_year = datetime.datetime.now().year
    cursor.execute('SELECT COUNT(*) FROM league_seasons WHERE year = ?', (current_year,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO league_seasons (year, name, start_date, end_date, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_year, f'{current_year} NFL Season', 
              f'{current_year}-09-01', f'{current_year+1}-02-01', True))
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_week_year ON nfl_games(week, year)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_picks_user_week ON user_picks(user_id, game_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_results_week_year ON weekly_results(week, year)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read)')
    
    conn.commit()
    conn.close()
    print("✓ Enhanced database initialization completed")

def get_week_game_count(week, year):
    """Get the number of games in a specific week"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
    game_count = cursor.fetchone()[0]
    
    conn.close()
    return game_count

def get_available_weeks(year):
    """Get list of weeks that have games in the database"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT week FROM nfl_games 
        WHERE year = ? 
        ORDER BY week
    ''', (year,))
    
    weeks = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return weeks
