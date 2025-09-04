"""
Clean version of app.py with no syntax errors or duplicate routes
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import datetime
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Import our custom modules
from database import init_database, get_week_game_count, get_available_weeks
from game_manager import ensure_games_exist, auto_populate_all_games
from nfl_schedule import get_current_nfl_week

app = Flask(__name__)
app.secret_key = 'nfl-fantasy-secret-key-2024'

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        current_week = get_current_nfl_week()
        current_year = datetime.datetime.now().year
        
        user_picks_count = 0
        total_games = get_week_game_count(current_week, current_year)
        user_wins = 0
        total_players = 0
        available_weeks = get_available_weeks(current_year)
        
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE up.user_id = ? AND g.week = ? AND g.year = ?
            ''', (session['user_id'], current_week, current_year))
            result = cursor.fetchone()
            user_picks_count = result[0] if result else 0
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
            result = cursor.fetchone()
            total_players = result[0] if result else 0
            
            conn.close()
            
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        template_data = {
            'current_week': current_week, 
            'current_year': current_year,
            'username': session.get('username', 'User'),
            'user_picks_count': user_picks_count,
            'total_games': total_games,
            'user_wins': user_wins,
            'total_players': total_players,
            'available_weeks': available_weeks or list(range(1, 19))
        }
        
        return render_template('index.html', **template_data)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('login'))

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

# Add all other routes here without duplicates...

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("🚀 Starting La Casa de Todos NFL Fantasy League...")
    
    try:
        init_database()
        auto_populate_all_games()
        
        app.config['DEBUG'] = True
        print("🏈 Application ready! Access at: http://127.0.0.1:5000")
        
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
