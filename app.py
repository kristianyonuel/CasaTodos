from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from setup_database import setup_complete_database

app = Flask(__name__)
app.secret_key = 'nfl-fantasy-secret-key-2024'

DATABASE_PATH = 'nfl_fantasy.db'

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_app():
    if not os.path.exists(DATABASE_PATH):
        print("Database not found, running setup...")
        setup_complete_database()
    else:
        print("Database exists, ready to run")

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Initialize app on first access
    initialize_app()
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = ?', (datetime.now().year,))
    total_games = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
    total_players = cursor.fetchone()[0]
    
    conn.close()
    
    data = {
        'current_week': 1,
        'current_year': datetime.now().year,
        'username': session.get('username', 'User'),
        'user_picks_count': 0,
        'total_games': total_games,
        'user_wins': 0,
        'total_players': total_players,
        'available_weeks': list(range(1, 19))
    }
    
    return render_template('index.html', **data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        conn = get_db()
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

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM nfl_games 
        WHERE week = ? AND year = ? 
        ORDER BY game_date
    ''', (week, year))
    games_data = cursor.fetchall()
    
    cursor.execute('''
        SELECT g.id, up.selected_team, up.predicted_home_score, up.predicted_away_score
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND g.week = ? AND g.year = ?
    ''', (session['user_id'], week, year))
    
    user_picks = {}
    for row in cursor.fetchall():
        user_picks[row[0]] = {
            'selected_team': row[1],
            'predicted_home_score': row[2],
            'predicted_away_score': row[3]
        }
    
    conn.close()
    
    return render_template('games.html',
                          games=games_data,
                          user_picks=user_picks,
                          current_week=week,
                          current_year=year,
                          available_weeks=list(range(1, 19)),
                          current_nfl_week=1,
                          total_games=len(games_data))

@app.route('/submit_picks', methods=['POST'])
def submit_picks():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    picks = data.get('picks', [])
    
    conn = get_db()
    cursor = conn.cursor()
    successful_picks = 0
    
    for pick in picks:
        game_id = pick.get('game_id')
        selected_team = pick.get('selected_team')
        home_score = pick.get('home_score')
        away_score = pick.get('away_score')
        
        if game_id and selected_team:
            cursor.execute('''
                INSERT OR REPLACE INTO user_picks 
                (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (session['user_id'], game_id, selected_team, home_score, away_score))
            successful_picks += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Successfully submitted {successful_picks} picks!'})

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
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                flash('Username already exists', 'error')
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

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, 
               COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) as wins,
               AVG(wr.correct_picks) as avg_correct,
               SUM(wr.total_points) as total_points
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

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    return render_template('admin.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    print("🚀 Starting La Casa de Todos NFL Fantasy League...")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
