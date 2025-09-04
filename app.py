from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import datetime
import os
import requests
import json
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'nfl-fantasy-secret-key-2024'

# Initialize database
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
    
    # Initialize league settings
    default_settings = [
        ('weekly_fee', '5.00', 'Weekly pool entry fee'),
        ('season_fee', '10.00', 'Full season pool entry fee'),
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
    """Get current NFL week"""
    now = datetime.datetime.now()
    # NFL season typically starts first week of September
    season_start = datetime.datetime(now.year, 9, 5)
    if now < season_start:
        season_start = datetime.datetime(now.year - 1, 9, 5)
    
    days_since_start = (now - season_start).days
    week = max(1, min(18, (days_since_start // 7) + 1))
    return week

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
            game_date = datetime.datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
            
            game = {
                'id': event['id'],
                'week': week,
                'year': year,
                'home_team': event['competitions'][0]['competitors'][0]['team']['abbreviation'],
                'away_team': event['competitions'][0]['competitors'][1]['team']['abbreviation'],
                'home_team_name': event['competitions'][0]['competitors'][0]['team']['displayName'],
                'away_team_name': event['competitions'][0]['competitors'][1]['team']['displayName'],
                'game_date': game_date,
                'is_monday_night': game_date.weekday() == 0,
                'is_thursday_night': game_date.weekday() == 3,
                'is_final': event['status']['type']['completed']
            }
            
            if game['is_final']:
                competitors = event['competitions'][0]['competitors']
                game['home_score'] = int(competitors[0].get('score', 0))
                game['away_score'] = int(competitors[1].get('score', 0))
            
            games.append(game)
        
        return games
    except Exception as e:
        print(f"Error fetching NFL games: {e}")
        return []

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_week = get_current_nfl_week()
    current_year = datetime.datetime.now().year
    
    return render_template('index.html', 
                         current_week=current_week, 
                         current_year=current_year,
                         username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not password:
                flash('Please enter both username and password', 'error')
                return render_template('login.html')
            
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['username'] = username
                session['is_admin'] = bool(user[2])
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login error occurred. Please try again.', 'error')
    
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

@app.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        # Get games from database or fetch new ones
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, week, year, game_id, home_team, away_team, game_date, 
                   is_monday_night, is_thursday_night, home_score, away_score, is_final
            FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
        ''', (week, year))
        
        db_games = cursor.fetchall()
        
        if not db_games:
            # Fetch from API and store
            api_games = fetch_nfl_games(week, year)
            for game in api_games:
                cursor.execute('''
                    INSERT OR REPLACE INTO nfl_games 
                    (game_id, week, year, home_team, away_team, game_date, 
                     is_monday_night, is_thursday_night, home_score, away_score, is_final)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (game['id'], game['week'], game['year'], game['home_team'], 
                      game['away_team'], game['game_date'], game['is_monday_night'],
                      game['is_thursday_night'], game.get('home_score'), 
                      game.get('away_score'), game['is_final']))
            
            conn.commit()
            
            # Fetch again from database
            cursor.execute('''
                SELECT id, week, year, game_id, home_team, away_team, game_date, 
                       is_monday_night, is_thursday_night, home_score, away_score, is_final
                FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
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
        
        # Format games for template
        games_list = []
        for game in db_games:
            games_list.append({
                'id': game[0],
                'week': game[1],
                'year': game[2],
                'game_id': game[3],
                'home_team': game[4],
                'away_team': game[5],
                'game_date': game[6],
                'is_monday_night': bool(game[7]),
                'is_thursday_night': bool(game[8]),
                'home_score': game[9],
                'away_score': game[10],
                'is_final': bool(game[11])
            })
        
        return render_template('games.html', 
                             games=games_list, 
                             user_picks=user_picks,
                             current_week=week,
                             current_year=year)
                             
    except Exception as e:
        print(f"Games page error: {e}")
        flash('Error loading games. Please try again.', 'error')
        return redirect(url_for('index'))

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
