from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import datetime
import os
import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from nfl_schedule_2025 import get_2025_schedule, get_current_nfl_week_2025, NFL_TEAMS
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
    
    # Validate minimum requirements
    if total_games < 50:  # Minimum expected games
        print("   ⚠️  Warning: Low game count detected")
        return False
    
    if len(weeks_data) < 5:  # At least 5 weeks should have games
        print("   ⚠️  Warning: Few weeks have games")
        return False
    
    print("   ✅ NFL games validation passed")
    return True

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
    
    # Sample NFL games for current week (if none exist)
    cursor.execute('SELECT COUNT(*) FROM nfl_games')
    if cursor.fetchone()[0] == 0:
        current_week = get_current_nfl_week()
        current_year = datetime.datetime.now().year
        
        sample_games = [
            (current_week, current_year, f'sample_game_1_{current_week}', 'KC', 'BUF', datetime.datetime.now() + datetime.timedelta(days=3), 0, 1),
            (current_week, current_year, f'sample_game_2_{current_week}', 'DAL', 'NYG', datetime.datetime.now() + datetime.timedelta(days=5), 0, 0),
            (current_week, current_year, f'sample_game_3_{current_week}', 'SF', 'LAR', datetime.datetime.now() + datetime.timedelta(days=6), 1, 0)
        ]
        
        for week, year, game_id, home, away, game_date, is_monday, is_thursday in sample_games:
            cursor.execute('''
                INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_monday_night, is_thursday_night)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (week, year, game_id, home, away, game_date, is_monday, is_thursday))
        print(f"✓ Created sample games for week {current_week}")
    
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
    """Create NFL games from the official schedule"""
    try:
        if year >= 2025:
            games = get_official_2025_games(week)
            if games:
                return games
        
        # Fall back to sample games for older years
        return create_sample_games(week, year)
            
    except Exception as e:
        print(f"Error creating games from schedule: {e}")
        return create_sample_games(week, year)

def fetch_all_nfl_weeks(year=None):
    """Fetch all 18 weeks of NFL games for the season"""
    if not year:
        year = datetime.datetime.now().year
    
    print(f"Creating all NFL weeks for {year} season...")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    total_games_added = 0
    
    if year >= 2025:
        # Use official 2025 schedule
        all_weeks_data = populate_all_2025_weeks()
        
        for week in range(1, 19):
            print(f"Processing week {week}...")
            
            # Check if we already have games for this week
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            
            if existing_games > 0:
                print(f"Week {week} already has {existing_games} games, skipping...")
                continue
            
            try:
                games = all_weeks_data.get(week, [])
                
                week_games = 0
                for game in games:
                    cursor.execute('''
                        INSERT OR REPLACE INTO nfl_games 
                        (game_id, week, year, home_team, away_team, game_date, 
                         is_monday_night, is_thursday_night, home_score, away_score, is_final)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (game['game_id'], game['week'], game['year'], 
                          game['home_team'], game['away_team'], game['game_date'],
                          game['is_monday_night'], game['is_thursday_night'], 
                          game.get('home_score'), game.get('away_score'), game.get('is_final', False)))
                
                week_games += 1
                total_games_added += 1
                
                print(f"Added {week_games} games for week {week}")
                
            except Exception as e:
                print(f"Error processing week {week}: {e}")
                continue
    else:
        for week in range(1, 19):
            print(f"Processing week {week}...")
            
            # Check if we already have games for this week
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            
            if existing_games > 0:
                print(f"Week {week} already has {existing_games} games, skipping...")
                continue
            
            try:
                # First try official schedule
                games = create_nfl_games_from_schedule(week, year)
                
                # If no games from schedule, try ESPN API
                if not games:
                    games = fetch_nfl_games(week, year)
                
                # If still no games, create sample games
                if not games:
                    games = create_sample_games(week, year)
                
                week_games = 0
                for game in games:
                    cursor.execute('''
                        INSERT OR REPLACE INTO nfl_games 
                        (game_id, week, year, home_team, away_team, game_date, 
                         is_monday_night, is_thursday_night, home_score, away_score, is_final)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (game['game_id'], game['week'], game['year'], 
                          game['home_team'], game['away_team'], game['game_date'],
                          game['is_monday_night'], game['is_thursday_night'], 
                          game.get('home_score'), game.get('away_score'), game.get('is_final', False)))
                
                week_games += 1
                total_games_added += 1
                
                print(f"Added {week_games} games for week {week}")
                
            except Exception as e:
                print(f"Error processing week {week}: {e}")
                continue
    
    conn.commit()
    conn.close()
    
    print(f"Season creation complete! Added {total_games_added} total games.")
    return total_games_added

@app.route('/')
def index():
    print(f"Index route accessed - Session: {dict(session)}")
    
    if 'user_id' not in session:
        print("No user_id in session, redirecting to login")
        return redirect(url_for('login'))
    
    try:
        current_week = get_current_nfl_week()
        current_year = datetime.datetime.now().year
        
        # Initialize default values
        user_picks_count = 0
        total_games = 0
        user_wins = 0
        total_players = 0
        available_weeks = []
        
        # Get week-specific game count
        total_games = get_week_game_count(current_week, current_year)
        
        # Try to get database stats safely
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            # Get user's total picks this week
            cursor.execute('''
                SELECT COUNT(*) FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE up.user_id = ? AND g.week = ? AND g.year = ?
            ''', (session['user_id'], current_week, current_year))
            result = cursor.fetchone()
            user_picks_count = result[0] if result else 0
            
            # Get total games this week (safe query)
            cursor.execute('''
                SELECT COUNT(*) FROM nfl_games
                WHERE week = ? AND year = ?
            ''', (current_week, current_year))
            result = cursor.fetchone()
            total_games = result[0] if result else 0
            
            # Get user's total wins (safe query)
            cursor.execute('''
                SELECT COUNT(*) FROM weekly_results
                WHERE user_id = ? AND is_winner = 1
            ''', (session['user_id'],))
            result = cursor.fetchone()
            user_wins = result[0] if result else 0
            
            # Get league stats (safe query)
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
            result = cursor.fetchone()
            total_players = result[0] if result else 0
            
            # Get available weeks (safe query)
            cursor.execute('''
                SELECT DISTINCT week FROM nfl_games 
                WHERE year = ? 
                ORDER BY week
            ''', (current_year,))
            available_weeks = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            print(f"Dashboard stats: Picks {user_picks_count}/{total_games}, Wins: {user_wins}")
            
        except Exception as db_error:
            print(f"Database error (using defaults): {db_error}")
            if 'conn' in locals():
                conn.close()
        
        # Auto-sync NFL games if we have no weeks available
        if len(available_weeks) == 0:
            print("No weeks available, creating sample data...")
            try:
                # Create sample games for current week only
                sample_games = create_sample_games(current_week, current_year)
                conn = sqlite3.connect('nfl_fantasy.db')
                cursor = conn.cursor()
                
                for game in sample_games:
                    cursor.execute('''
                        INSERT OR IGNORE INTO nfl_games 
                        (game_id, week, year, home_team, away_team, game_date, is_monday_night, is_thursday_night)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (game['game_id'], game['week'], game['year'], game['home_team'], 
                          game['away_team'], game['game_date'], game['is_monday_night'], game['is_thursday_night']))
                
                conn.commit()
                conn.close()
                
                available_weeks = [current_week]
                total_games = len(sample_games)
                print(f"Created {len(sample_games)} sample games for week {current_week}")
                
            except Exception as create_error:
                print(f"Error creating sample games: {create_error}")
                available_weeks = [current_week]
        
        template_data = {
            'current_week': current_week, 
            'current_year': current_year,
            'username': session.get('username', 'User'),
            'user_picks_count': user_picks_count,
            'total_games': total_games,
            'user_wins': user_wins,
            'total_players': total_players,
            'available_weeks': available_weeks
        }
        
        print(f"Dashboard data prepared: {template_data}")
        return render_template('index.html', **template_data)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return minimal dashboard if all else fails
        return render_template('index.html', 
                             current_week=1, 
                             current_year=2024,
                             username=session.get('username', 'User'),
                             user_picks_count=0,
                             total_games=0,
                             user_wins=0,
                             total_players=0,
                             available_weeks=[1])

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"Login route accessed - Method: {request.method}")
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"Login attempt - Username: {username}")
            
            if not username or not password:
                print("Missing username or password")
                flash('Please enter both username and password', 'error')
                return render_template('login.html')
            
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            
            print(f"User lookup result: {user is not None}")
            
            if user:
                print(f"User found - ID: {user[0]}, Admin: {user[2]}")
                password_check = check_password_hash(user[1], password)
                print(f"Password check result: {password_check}")
                
                if password_check:
                    session['user_id'] = user[0]
                    session['username'] = username
                    session['is_admin'] = bool(user[2])
                    print(f"Login successful - Session set for user: {username}")
                    flash('Successfully logged in!', 'success')
                    return redirect(url_for('index'))
                else:
                    print("Password check failed")
            else:
                print("User not found")
                
            flash('Invalid username or password', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            flash('Login error occurred. Please try again.', 'error')
    
    print("Rendering login template")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            email = request.form.get('email', '').strip()
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('register.html')
            
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                flash('Username already exists', 'error')
                conn.close()
                return render_template('register.html')
            
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

def create_emergency_games(week, year):
    """Create emergency minimal games when all other methods fail"""
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 'MIA', 'NYJ', 'CIN', 'CLE', 'HOU', 'IND']
    
    # Calculate proper game dates for AST timezone
    if year >= 2025:
        season_start = datetime.datetime(2025, 9, 4)  # 2025 season starts Sept 4
    else:
        season_start = datetime.datetime(2024, 9, 5)  # 2024 season started Sept 5
    
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
            'game_date': thursday_date.replace(hour=20, minute=15),  # Thursday 8:15 PM AST
            'is_monday_night': False,
            'is_thursday_night': True
        })
        used_teams = 2
    else:
        used_teams = 0
    
    # Sunday games
    sunday = week_start + datetime.timedelta(days=(6 if week == 1 else 6))  # First Sunday
    
    # Early Sunday games (1:00 PM AST)
    game_counter = 0
    for i in range(used_teams, min(used_teams + 12, len(teams)), 2):
        if i + 1 < len(teams):
            games.append({
                'game_id': f'emergency_sun_early_{week}_{year}_{game_counter}',
                'week': week,
                'year': year,
                'home_team': teams[i],
                'away_team': teams[i + 1],
                'game_date': sunday.replace(hour=13, minute=0),  # 1:00 PM AST
                'is_monday_night': False,
                'is_thursday_night': False
            })
            game_counter += 1
    
    # Late Sunday games (4:25 PM AST)
    start_idx = used_teams + 12
    for i in range(start_idx, min(start_idx + 4, len(teams)), 2):
        if i + 1 < len(teams):
            games.append({
                'game_id': f'emergency_sun_late_{week}_{year}_{game_counter}',
                'week': week,
                'year': year,
                'home_team': teams[i],
                'away_team': teams[i + 1],
                'game_date': sunday.replace(hour=16, minute=25),  # 4:25 PM AST
                'is_monday_night': False,
                'is_thursday_night': False
            })
            game_counter += 1
    
    # Monday Night Football
    monday = week_start + datetime.timedelta(days=7)  # Next Monday
    remaining_teams = [t for t in teams if t not in [g['home_team'] for g in games] + [g['away_team'] for g in games]]
    
    if len(remaining_teams) >= 2:
        games.append({
            'game_id': f'emergency_mnf_{week}_{year}',
            'week': week,
            'year': year,
            'home_team': remaining_teams[0],
            'away_team': remaining_teams[1],
            'game_date': monday.replace(hour=20, minute=15),  # Monday 8:15 PM AST
            'is_monday_night': True,
            'is_thursday_night': False
        })
    
    print(f"Created {len(games)} emergency games for Week {week}")
    return games

def ensure_games_exist(week, year):
    """Ensure games exist for the given week and year, create if missing"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if games exist
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"Week {week} already has {existing_count} games")
            conn.close()
            return existing_count
        
        print(f"Creating games for Week {week}, {year}")
        
        # Create games using multiple methods
        games_created = 0
        games = []
        
        # Method 1: Use official schedule if available
        try:
            if year >= 2025:
                games = create_nfl_games_from_schedule(week, year)
                print(f"Created {len(games)} games from official schedule")
        except Exception as e:
            print(f"Official schedule failed: {e}")
        
        # Method 2: Try ESPN API if no schedule games
        if not games:
            try:
                games = fetch_nfl_games(week, year)
                print(f"Created {len(games)} games from ESPN API")
            except Exception as e:
                print(f"ESPN API failed: {e}")
        
        # Method 3: Create emergency games as fallback
        if not games:
            print("Creating emergency games as fallback...")
            games = create_emergency_games(week, year)
        
        # Insert games into database
        for game in games:
            try:
                # Handle game_date properly
                game_date = game['game_date']
                if isinstance(game_date, str):
                    try:
                        game_date = datetime.datetime.fromisoformat(game_date)
                    except:
                        game_date = datetime.datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S')
                
                # Store in database with proper timezone handling
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
                    game_date.strftime('%Y-%m-%d %H:%M:%S'),
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
        import traceback
        traceback.print_exc()
        return 0

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

def fetch_nfl_games(week=None, year=None):
    """Fetch NFL games from ESPN API"""
    if not year:
        year = datetime.datetime.now().year
    if not week:
        week = get_current_nfl_week()
    
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        params = {'seasontype': 2, 'week': week, 'year': year}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        games = []
        for event in data.get('events', []):
            try:
                game_date_str = event['date']
                # Handle different date formats from ESPN
                if game_date_str.endswith('Z'):
                    game_date = datetime.datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                else:
                    game_date = datetime.datetime.fromisoformat(game_date_str)
                
                # Determine game type based on day and time
                weekday = game_date.weekday()  # 0=Monday, 6=Sunday
                hour = game_date.hour
                
                # Fix the Monday night condition (line 918 issue)
                is_monday_night = (weekday == 0 and hour >= 18)  # Monday after 6 PM
                is_thursday_night = (weekday == 3 and hour >= 18)  # Thursday after 6 PM
                
                game = {
                    'id': event['id'],
                    'week': week,
                    'year': year,
                    'home_team': event['competitions'][0]['competitors'][0]['team']['abbreviation'],
                    'away_team': event['competitions'][0]['competitors'][1]['team']['abbreviation'],
                    'home_team_name': event['competitions'][0]['competitors'][0]['team']['displayName'],
                    'away_team_name': event['competitions'][0]['competitors'][1]['team']['displayName'],
                    'game_date': game_date,
                    'is_monday_night': is_monday_night,
                    'is_thursday_night': is_thursday_night,
                    'is_final': event['status']['type']['completed']
                }
                
                if game['is_final']:
                    competitors = event['competitions'][0]['competitors']
                    game['home_score'] = int(competitors[0].get('score', 0))
                    game['away_score'] = int(competitors[1].get('score', 0))
                
                games.append(game)
                
            except Exception as game_error:
                print(f"Error processing individual game: {game_error}")
                continue
        
        return games
    except Exception as e:
        print(f"Error fetching NFL games: {e}")
        return []

@app.route('/games')
def games():
    print(f"Games route accessed - Session: {dict(session)}")
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        # Ensure games exist for this week
        games_count = ensure_games_exist(week, year)
        print(f"Week {week} has {games_count} games available")
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get games for the week with proper ordering
        cursor.execute('''
            SELECT id, week, year, game_id, home_team, away_team, game_date, 
                   is_monday_night, is_thursday_night, home_score, away_score, is_final
            FROM nfl_games WHERE week = ? AND year = ? 
            ORDER BY 
                CASE 
                    WHEN is_thursday_night = 1 THEN 1
                    WHEN is_monday_night = 1 THEN 3
                    ELSE 2
                END, 
                datetime(game_date)
        ''', (week, year))
        
        db_games = cursor.fetchall()
        
        if not db_games:
            print(f"No games found in database for Week {week}, creating now...")
            # Force create games
            ensure_games_exist(week, year)
            
            # Try again
            cursor.execute('''
                SELECT id, week, year, game_id, home_team, away_team, game_date, 
                       is_monday_night, is_thursday_night, home_score, away_score, is_final
                FROM nfl_games WHERE week = ? AND year = ? 
                ORDER BY 
                    CASE 
                        WHEN is_thursday_night = 1 THEN 1
                        WHEN is_monday_night = 1 THEN 3
                        ELSE 2
                    END, 
                    datetime(game_date)
            ''', (week, year))
            db_games = cursor.fetchall()
        
        # Get user's existing picks
        cursor.execute('''
            SELECT g.id, up.selected_team, up.predicted_home_score, up.predicted_away_score
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = ? AND g.year = ?
        ''', (session['user_id'], week, year))
        
        user_picks = {row[0]: {
            'selected_team': row[1],
            'predicted_home_score': row[2],
            'predicted_away_score': row[3]
        } for row in cursor.fetchall()}
        
        conn.close()
        
        # Format games for template with proper AST timezone
        games_list = []
        for game in db_games:
            game_date = None
            if game[6]:  # game_date
                try:
                    if isinstance(game[6], str):
                        # Parse date string
                        try:
                            game_date = datetime.datetime.fromisoformat(game[6])
                        except ValueError:
                            game_date = datetime.datetime.strptime(game[6], '%Y-%m-%d %H:%M:%S')
                        
                        # Convert to AST if needed
                        if game_date.tzinfo is None:
                            game_date = AST.localize(game_date)
                        else:
                            game_date = game_date.astimezone(AST)
                    else:
                        game_date = game[6]
                        if hasattr(game_date, 'tzinfo') and game_date.tzinfo is None:
                            game_date = AST.localize(game_date)
                except Exception as date_error:
                    print(f"Date parsing error: {date_error}")
                    # Default to current time in AST
                    game_date = datetime.datetime.now(AST)
            
            games_list.append({
                'id': game[0],
                'week': game[1],
                'year': game[2],
                'game_id': game[3],
                'home_team': game[4],
                'away_team': game[5],
                'game_date': game_date,
                'is_monday_night': bool(game[7]),
                'is_thursday_night': bool(game[8]),
                'home_score': game[9],
                'away_score': game[10],
                'is_final': bool(game[11])
            })
        
        # Get available weeks for navigation
        available_weeks = get_available_weeks(year)
        if not available_weeks:
            available_weeks = list(range(1, 19))  # Default to all 18 weeks
        
        current_nfl_week = get_current_nfl_week()
        
        print(f"Games page loaded successfully: {len(games_list)} games for Week {week}")
        
        return render_template('games.html', 
                             games=games_list, 
                             user_picks=user_picks,
                             current_week=week,
                             current_year=year,
                             available_weeks=available_weeks,
                             current_nfl_week=current_nfl_week,
                             total_games=len(games_list))
                             
    except Exception as e:
        print(f"Games page error for Week {week}: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading games for Week {week}. Creating games now...', 'warning')
        
        # Emergency fallback - force create games and redirect
        try:
            ensure_games_exist(week, year)
            return redirect(url_for('games', week=week, year=year))
        except Exception as fallback_error:
            print(f"Emergency fallback failed: {fallback_error}")
            flash('Unable to load games. Please try a different week.', 'error')
            return redirect(url_for('index'))

@app.route('/force_create_games/<int:week>/<int:year>')
def force_create_games(week, year):
    """Force create games for a specific week (admin only)"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('games'))
    
    try:
        games_created = ensure_games_exist(week, year)
        flash(f'Successfully created {games_created} games for Week {week}', 'success')
    except Exception as e:
        flash(f'Error creating games: {str(e)}', 'error')
    
    return redirect(url_for('games', week=week, year=year))

@app.route('/submit_picks', methods=['POST'])
def submit_picks():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        picks = data.get('picks', [])
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        for pick in picks:
            game_id = pick.get('game_id')
            selected_team = pick.get('selected_team')
            home_score = pick.get('home_score')
            away_score = pick.get('away_score')
            
            if not game_id or not selected_team:
                continue
                
            # Check if pick already exists
            cursor.execute('''
                SELECT id FROM user_picks WHERE user_id = ? AND game_id = ?
            ''', (session['user_id'], game_id))
            
            existing_pick = cursor.fetchone()
            
            if existing_pick:
                cursor.execute('''
                    UPDATE user_picks 
                    SET selected_team = ?, predicted_home_score = ?, predicted_away_score = ?
                    WHERE id = ?
                ''', (selected_team, home_score, away_score, existing_pick[0]))
            else:
                cursor.execute('''
                    INSERT INTO user_picks 
                    (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session['user_id'], game_id, selected_team, home_score, away_score))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Picks submitted successfully!'})
    
    except Exception as e:
        print(f"Submit picks error: {e}")
        return jsonify({'error': 'Failed to submit picks'}), 500

@app.errorhandler(404)
def not_found_error(error):
    print(f"404 Error: {error}")
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"500 Error: {error}")
    import traceback
    traceback.print_exc()
    return render_template('error.html', error="Internal server error"), 500

@app.route('/sync_season', methods=['POST'])
def sync_season():
    """Manual sync of entire NFL season"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        year = request.json.get('year', datetime.datetime.now().year)
        games_added = fetch_all_nfl_weeks(year)
        return jsonify({
            'success': True, 
            'message': f'Synced {games_added} games for {year} season',
            'games_added': games_added
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get weekly winners and stats
        cursor.execute('''
            SELECT u.username, 
                   COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) as wins,
                   AVG(wr.correct_picks) as avg_correct,
                   SUM(wr.points) as total_points
            FROM users u
            LEFT JOIN weekly_results wr ON u.id = wr.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id, u.username
            ORDER BY wins DESC, total_points DESC
        ''')
        
        leaderboard_data = []
        for row in cursor.fetchall():
            leaderboard_data.append({
                'username': row[0],
                'wins': row[1] or 0,
                'avg_correct': round(row[2] or 0, 1),
                'total_points': row[3] or 0
            })
        
        conn.close()
        return render_template('leaderboard.html', leaderboard=leaderboard_data)
        
    except Exception as e:
        print(f"Leaderboard error: {e}")
        flash('Error loading leaderboard', 'error')
        return redirect(url_for('index'))

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    return render_template('admin.html')

if __name__ == '__main__':
    # Create directories if they don't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Initialize database
    print("🚀 Starting La Casa de Todos NFL Fantasy League...")
    print("=" * 60)
    
    try:
        print("📁 Initializing database...")
        init_db()
        print("✅ Database initialized successfully")
        
        # Force auto-populate NFL games
        total_created = auto_populate_nfl_games()
        
        # Validate games were created
        if validate_nfl_games():
            print("✅ NFL games validation passed")
        else:
            print("⚠️  NFL games validation failed - creating emergency games...")
            # Force create games for week 1 at minimum
            ensure_games_exist(1, datetime.datetime.now().year)
        
        # Final check for Week 1 specifically
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = ?', (datetime.datetime.now().year,))
        week1_games = cursor.fetchone()[0]
        conn.close()
        
        print(f"🔍 Week 1 verification: {week1_games} games available")
        
        if week1_games == 0:
            print("🚨 Emergency: Force creating Week 1 games...")
            ensure_games_exist(1, datetime.datetime.now().year)
        
        # Add debug mode
        app.config['DEBUG'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        print("=" * 60)
        print("🏈 Application ready!")
        print("Access at: http://127.0.0.1:5000")
        print("Network access: http://0.0.0.0:5000")
        print("=" * 60)
        
        # Run on all interfaces
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
