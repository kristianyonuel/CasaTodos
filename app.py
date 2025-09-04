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
    
    # Create default admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin@lacasadetodos.com', True))
    
    conn.commit()
    conn.close()

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
        username = request.form['username']
        password = request.form['password']
        
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
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        
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
    
    # Get games from database or fetch new ones
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
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
            SELECT * FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
        ''', (week, year))
        db_games = cursor.fetchall()
   