#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime

def fix_database():
    """Fix the database with proper structure and Week 4 games including correct MNF detection"""
    
    # Remove existing database and start fresh
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("Removed existing database")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create nfl_games table with correct structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER UNIQUE,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            away_team TEXT NOT NULL,
            home_team TEXT NOT NULL,
            game_date TEXT NOT NULL,
            away_score INTEGER,
            home_score INTEGER,
            is_final BOOLEAN DEFAULT FALSE,
            is_monday_night BOOLEAN DEFAULT FALSE,
            is_thursday_night BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            selected_team TEXT NOT NULL,
            predicted_home_score INTEGER,
            predicted_away_score INTEGER,
            is_correct BOOLEAN DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (game_id) REFERENCES nfl_games (id),
            UNIQUE(user_id, game_id)
        )
    ''')
    
    # Create weekly_results table  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            correct_picks INTEGER DEFAULT 0,
            total_picks INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            rank INTEGER,
            is_winner BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(week, year, user_id)
        )
    ''')
    
    print("Database tables created successfully!")
    
    # Insert Week 4 games with correct Monday Night Football detection
    print("Adding Week 4 games...")
    
    week4_games = [
        # Thursday Night Football
        (101, 4, 2025, 'Dallas Cowboys', 'New York Giants', '2025-09-25 20:15:00', False, True),
        
        # Sunday games
        (102, 4, 2025, 'Chicago Bears', 'Los Angeles Rams', '2025-09-28 13:00:00', False, False),
        (103, 4, 2025, 'Carolina Panthers', 'Atlanta Falcons', '2025-09-28 13:00:00', False, False),
        (104, 4, 2025, 'Indianapolis Colts', 'Pittsburgh Steelers', '2025-09-28 13:00:00', False, False),
        (105, 4, 2025, 'Minnesota Vikings', 'Green Bay Packers', '2025-09-28 13:00:00', False, False),
        (106, 4, 2025, 'New Orleans Saints', 'Tampa Bay Buccaneers', '2025-09-28 13:00:00', False, False),
        (107, 4, 2025, 'Philadelphia Eagles', 'Washington Commanders', '2025-09-28 13:00:00', False, False),
        (108, 4, 2025, 'Houston Texans', 'Jacksonville Jaguars', '2025-09-28 13:00:00', False, False),
        (109, 4, 2025, 'Miami Dolphins', 'Tennessee Titans', '2025-09-28 13:00:00', False, False),
        (110, 4, 2025, 'Cleveland Browns', 'Las Vegas Raiders', '2025-09-28 16:05:00', False, False),
        (111, 4, 2025, 'New England Patriots', 'San Francisco 49ers', '2025-09-28 16:25:00', False, False),
        (112, 4, 2025, 'Arizona Cardinals', 'Los Angeles Chargers', '2025-09-28 16:25:00', False, False),
        (113, 4, 2025, 'Kansas City Chiefs', 'New York Jets', '2025-09-28 20:20:00', False, False),  # Sunday Night
        
        # Monday Night Football - The actual MNF game that should show for tiebreaker
        (114, 4, 2025, 'Cincinnati Bengals', 'Denver Broncos', '2025-09-29 20:15:00', True, False),  # THIS IS THE REAL MNF
    ]
    
    for game_data in week4_games:
        cursor.execute('''
            INSERT INTO nfl_games (game_id, week, year, away_team, home_team, game_date, is_monday_night, is_thursday_night)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', game_data)
    
    print(f"Added {len(week4_games)} games for Week 4")
    
    # Add sample admin user
    from werkzeug.security import generate_password_hash
    
    admin_password_hash = generate_password_hash('admin123')
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin@casadetodos.com', admin_password_hash, True))
    
    # Add sample regular users
    sample_users = [
        ('jean', 'jean@example.com', 'password123'),
        ('coyote', 'coyote@example.com', 'password123'),
        ('ramfis', 'ramfis@example.com', 'password123'),
        ('buffalo', 'buffalo@example.com', 'password123'),
    ]
    
    for username, email, password in sample_users:
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, False))
    
    print("Added sample users")
    
    # Verify Monday Night Football detection
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
    
    # Verify the MNF detection query works
    cursor.execute('''
        SELECT id, away_team, home_team FROM nfl_games 
        WHERE week = 4 AND year = 2025 
        AND strftime('%w', game_date) = '1'  -- Monday
        ORDER BY game_date DESC, id DESC
        LIMIT 1
    ''')
    
    mnf_game = cursor.fetchone()
    if mnf_game:
        print(f"\nMNF Tiebreaker Game: {mnf_game[1]} @ {mnf_game[2]} (ID: {mnf_game[0]})")
    else:
        print("\nERROR: No Monday Night game found for tiebreaker!")
    
    conn.commit()
    conn.close()
    
    print("\nDatabase fix completed successfully!")
    print("Cincinnati Bengals @ Denver Broncos should now appear as Monday Night tiebreaker.")

if __name__ == '__main__':
    fix_database()