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
    
    return render_template('games.html', games=games, week=week, year=year)

@app.route('/picks', methods=['GET', 'POST'])
def picks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # User made a new pick
        game_id = request.form['game_id']
        selected_team = request.form['selected_team']
        predicted_home_score = request.form.get('predicted_home_score', type=int)
        predicted_away_score = request.form.get('predicted_away_score', type=int)
        
        cursor.execute('''
            INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], game_id, selected_team, predicted_home_score, predicted_away_score))
        
        conn.commit()
        flash('Your pick has been saved!', 'success')
        return redirect(url_for('picks'))
    
    # Get current week's games
    week = get_current_nfl_week()
    year = datetime.datetime.now().year
    
    cursor.execute('''
        SELECT ng.*, up.selected_team, up.predicted_home_score, up.predicted_away_score 
        FROM nfl_games ng
        LEFT JOIN user_picks up ON ng.id = up.game_id AND up.user_id = ?
        WHERE ng.week = ? AND ng.year = ?
    ''', (session['user_id'], week, year))
    
    games = cursor.fetchall()
    
    picks = []
    for game in games:
        picks.append({
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
            'is_final': game[11],
            'selected_team': game[12],
            'predicted_home_score': game[13],
            'predicted_away_score': game[14]
        })
    
    conn.close()
    
    return render_template('picks.html', picks=picks, week=week, year=year)

@app.route('/results')
def results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get current week
    week = get_current_nfl_week()
    year = datetime.datetime.now().year
    
    # Calculate results for the current week
    cursor.execute('''
        SELECT ng.*, up.selected_team, up.predicted_home_score, up.predicted_away_score, 
               CASE 
                   WHEN (ng.home_score - up.predicted_home_score) * (ng.away_score - up.predicted_away_score) > 0 THEN 1
                   WHEN (ng.home_score - up.predicted_home_score) * (ng.away_score - up.predicted_away_score) < 0 THEN -1
                   ELSE 0
               END as result
        FROM nfl_games ng
        JOIN user_picks up ON ng.id = up.game_id
        WHERE ng.week = ? AND ng.year = ? AND up.user_id = ?
    ''', (week, year, session['user_id']))
    
    picks = cursor.fetchall()
    
    # Calculate score differences for Monday Night games
    cursor.execute('''
        SELECT SUM(ABS(up.predicted_home_score - ng.home_score)) as home_score_diff,
               SUM(ABS(up.predicted_away_score - ng.away_score)) as away_score_diff
        FROM nfl_games ng
        JOIN user_picks up ON ng.id = up.game_id
        WHERE ng.week = ? AND ng.year = ? AND up.user_id = ? AND ng.is_monday_night = 1
    ''', (week, year, session['user_id']))
    
    monday_score_diff = cursor.fetchone()
    
    # Update or insert weekly results
    cursor.execute('''
        INSERT INTO weekly_results (user_id, week, year, correct_picks, total_picks, monday_score_diff)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, week, year) DO UPDATE SET
            correct_picks = excluded.correct_picks,
            total_picks = excluded.total_picks,
            monday_score_diff = excluded.monday_score_diff
    ''', (session['user_id'], week, year, sum(1 for p in picks if p[-1] == 1), len(picks), monday_score_diff[0] if monday_score_diff else 0))
    
    conn.commit()
    
    # Get updated results
    cursor.execute('''
        SELECT * FROM weekly_results WHERE user_id = ? ORDER BY year DESC, week DESC
    ''', (session['user_id'],))
    
    results = cursor.fetchall()
    
    conn.close()
    
    return render_template('results.html', picks=picks, results=results, week=week, year=year)

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    # Get all games
    cursor.execute('SELECT * FROM nfl_games ORDER BY game_date')
    games = cursor.fetchall()
    
    # Get all picks
    cursor.execute('''
        SELECT up.*, u.username, ng.home_team, ng.away_team, ng.game_date
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        JOIN nfl_games ng ON up.game_id = ng.id
        ORDER BY ng.game_date, u.username
    ''')
    picks = cursor.fetchall()
    
    # Get weekly results
    cursor.execute('''
        SELECT wr.*, u.username
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        ORDER BY wr.year DESC, wr.week DESC, u.username
    ''')
    weekly_results = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin.html', users=users, games=games, picks=picks, weekly_results=weekly_results)

@app.route('/api/games', methods=['GET'])
def api_games():
    week = request.args.get('week', type=int)
    year = request.args.get('year', type=int)
    
    games = fetch_nfl_games(week, year)
    
    return jsonify(games)

@app.route('/api/picks', methods=['POST'])
def api_picks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    game_id = data.get('game_id')
    selected_team = data.get('selected_team')
    predicted_home_score = data.get('predicted_home_score')
    predicted_away_score = data.get('predicted_away_score')
    
    if not all([game_id, selected_team, predicted_home_score, predicted_away_score]):
        return jsonify({'error': 'Missing data'}), 400
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], game_id, selected_team, predicted_home_score, predicted_away_score))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/results', methods=['GET'])
def api_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT wr.*, u.username
        FROM weekly_results wr
        JOIN users u ON wr.user_id = u.id
        WHERE wr.user_id = ?
        ORDER BY wr.year DESC, wr.week DESC
    ''', (session['user_id'],))
    
    results = cursor.fetchall()
    
    conn.close()
    
    return jsonify(results)

if __name__ == '__main__':
    # Create directories if they don't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Initialize database
    init_db()
    
    print("Starting La Casa de Todos NFL Fantasy League...")
    
    # Try to run on port 443 with different configurations
    import ssl
    
    try:
        # Try HTTPS with self-signed certificate
        print("Attempting to start HTTPS server on port 443...")
        print("Access at: https://127.0.0.1:443")
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        app.run(debug=False, host='0.0.0.0', port=443, ssl_context='adhoc')
    except PermissionError:
        print("Permission denied for port 443. Trying HTTP on port 443...")
        try:
            app.run(debug=False, host='0.0.0.0', port=443)
        except PermissionError:
            print("Port 443 requires administrator privileges.")
            print("Falling back to port 8443...")
            app.run(debug=True, host='0.0.0.0', port=8443)
    except Exception as e:
        print(f"Failed to start on port 443: {e}")
        print("Falling back to port 5000...")
        app.run(debug=True, host='127.0.0.1', port=5000)
