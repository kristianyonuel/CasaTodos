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
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login error occurred. Please try again.', 'error')
    
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
    
    conn.close()
    
    games = []
    for game in db_games:
        games.append({
            'id': game[0],
            'week': game[1],
            'year': game[2],
            'game_id': game[3],
            'home_team': game[4],
            'away_team': game[5],
            'game_date': game[6],
            'is_monday_night': game[7],
            'is_thursday_night': game[8],
            'home_score': game[9],
            'away_score': game[10],
            'is_final': game[11]
        })
    
    return render_template('games.html', 
                           games=games, 
                           current_week=week, 
                           current_year=year,
                           username=session.get('username'))

@app.route('/picks', methods=['GET', 'POST'])
def picks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    if request.method == 'POST':
        # Handle form submission for picks
        try:
            picks = request.form.getlist('picks')
            scores = request.form.getlist('scores')
            
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            # Update or insert user picks
            for pick in picks:
                game_id, selected_team = pick.split('_')
                predicted_home_score = int(scores[0]) if len(scores) > 0 else 0
                predicted_away_score = int(scores[1]) if len(scores) > 1 else 0
                
                cursor.execute('''
                    INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, game_id) DO UPDATE SET
                        selected_team = excluded.selected_team,
                        predicted_home_score = excluded.predicted_home_score,
                        predicted_away_score = excluded.predicted_away_score,
                        created_at = CURRENT_TIMESTAMP
                ''', (user_id, game_id, selected_team, predicted_home_score, predicted_away_score))
            
            conn.commit()
            flash('Your picks have been saved!', 'success')
            return redirect(url_for('picks', week=week, year=year))
        
        except Exception as e:
            print(f"Error saving picks: {e}")
            flash('An error occurred while saving your picks. Please try again.', 'error')
    
    # Get games for the current week
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT g.*, p.selected_team, p.predicted_home_score, p.predicted_away_score 
        FROM nfl_games g
        LEFT JOIN user_picks p ON g.id = p.game_id AND p.user_id = ?
        WHERE g.week = ? AND g.year = ?
    ''', (user_id, week, year))
    
    games = cursor.fetchall()
    
    conn.close()
    
    return render_template('picks.html', 
                           games=games, 
                           current_week=week, 
                           current_year=year,
                           username=session.get('username'))

@app.route('/results')
def results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    # Calculate results
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get user picks
    cursor.execute('''
        SELECT game_id, selected_team, predicted_home_score, predicted_away_score 
        FROM user_picks 
        WHERE user_id = ? AND week = ? AND year = ?
    ''', (user_id, week, year))
    
    user_picks = {row[0]: row[1:] for row in cursor.fetchall()}
    
    # Get actual game results
    cursor.execute('''
        SELECT home_team, away_team, home_score, away_score 
        FROM nfl_games 
        WHERE week = ? AND year = ?
    ''', (week, year))
    
    game_results = {row[0]: row[1:] for row in cursor.fetchall()}
    
    # Calculate correct picks and score
    correct_picks = 0
    total_picks = len(user_picks)
    score_diff = 0
    
    for game_id, (selected_team, predicted_home_score, predicted_away_score) in user_picks.items():
        if game_id in game_results:
            home_team, away_team, home_score, away_score = game_results[game_id]
            
            # Check if the pick was correct
            if (selected_team == 'home' and home_score > away_score) or (selected_team == 'away' and away_score > home_score):
                correct_picks += 1
            
            # Calculate score difference for tiebreaker
            score_diff += abs((predicted_home_score + predicted_away_score) - (home_score + away_score))
    
    # Update weekly results
    cursor.execute('''
        INSERT INTO weekly_results (user_id, week, year, correct_picks, total_picks, monday_score_diff, is_winner, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, week, year) DO UPDATE SET
            correct_picks = excluded.correct_picks,
            total_picks = excluded.total_picks,
            monday_score_diff = excluded.monday_score_diff,
            is_winner = excluded.is_winner,
            points = excluded.points
    ''', (user_id, week, year, correct_picks, total_picks, score_diff, 0, correct_picks * 10 - score_diff))
    
    conn.commit()
    conn.close()
    
    flash('Results calculated and saved!', 'success')
    return redirect(url_for('results', week=week, year=year))

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin.html', username=session.get('username'))

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, is_admin, created_at FROM users')
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_users.html', 
                           users=users, 
                           username=session.get('username'))

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Update settings
        try:
            settings = request.form.getlist('settings')
            
            for setting in settings:
                setting_name, setting_value = setting.split('_')
                
                cursor.execute('''
                    UPDATE league_settings 
                    SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE setting_name = ?
                ''', (setting_value, setting_name))
            
            conn.commit()
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('admin_settings'))
        
        except Exception as e:
            print(f"Error updating settings: {e}")
            flash('An error occurred while updating settings. Please try again.', 'error')
    
    cursor.execute('SELECT setting_name, setting_value, description FROM league_settings')
    settings = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_settings.html', 
                           settings=settings, 
                           username=session.get('username'))

@app.route('/admin/games')
def admin_games():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    # Get games from database
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
    ''', (week, year))
    
    db_games = cursor.fetchall()
    
    games = []
    for game in db_games:
        games.append({
            'id': game[0],
            'week': game[1],
            'year': game[2],
            'game_id': game[3],
            'home_team': game[4],
            'away_team': game[5],
            'game_date': game[6],
            'is_monday_night': game[7],
            'is_thursday_night': game[8],
            'home_score': game[9],
            'away_score': game[10],
            'is_final': game[11]
        })
    
    conn.close()
    
    return render_template('admin_games.html', 
                           games=games, 
                           current_week=week, 
                           current_year=year,
                           username=session.get('username'))

@app.route('/admin/stats')
def admin_stats():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    # Get weekly results
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT week, correct_picks, total_picks, points 
        FROM weekly_results 
        WHERE year = ?
        ORDER BY week
    ''', (year,))
    
    weekly_results = cursor.fetchall()
    
    # Get top players
    cursor.execute('''
        SELECT u.username, SUM(w.points) as total_points
        FROM weekly_results w
        JOIN users u ON w.user_id = u.id
        WHERE w.year = ?
        GROUP BY u.username
        ORDER BY total_points DESC
        LIMIT 10
    ''', (year,))
    
    top_players = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_stats.html', 
                           weekly_results=weekly_results, 
                           top_players=top_players,
                           current_year=year,
                           username=session.get('username'))

@app.route('/admin/refresh_games', methods=['POST'])
def admin_refresh_games():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    # Fetch new games from API and update database
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Fetch from API
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
    conn.close()
    
    flash('NFL games updated successfully!', 'success')
    return redirect(url_for('admin_games'))

@app.route('/admin/reset_results', methods=['POST'])
def admin_reset_results():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    # Reset weekly results for the year
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM weekly_results WHERE year = ?
    ''', (year,))
    
    conn.commit()
    conn.close()
    
    flash('Weekly results reset successfully!', 'success')
    return redirect(url_for('admin_stats'))

@app.route('/admin/backup', methods=['GET', 'POST'])
def admin_backup():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Create a backup of the database
        try:
            backup_file = f"nfl_fantasy_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            with open('nfl_fantasy.db', 'rb') as f:
                content = f.read()
            
            with open(backup_file, 'wb') as f:
                f.write(content)
            