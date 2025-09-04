from __future__ import annotations

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from setup_database import setup_complete_database
from database_sync import sync_season_from_api, sync_week_from_api, update_live_scores
from utils.timezone_utils import convert_to_ast, format_ast_time
from contextlib import contextmanager

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'nfl-fantasy-secret-key-2024'

DATABASE_PATH = 'nfl_fantasy.db'

@contextmanager
def get_db():
    """Database connection context manager for better resource management"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_db_legacy():
    """Legacy database connection function - kept for compatibility"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_app():
    if not os.path.exists(DATABASE_PATH):
        print("Database not found, running setup...")
        setup_complete_database()
    else:
        print("Database exists, ready to run")

def get_dashboard_data(user_id: int, week: int, year: int) -> Dict[str, int]:
    """Get dashboard data with accurate game counts"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get actual games count for the week
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
        total_games = cursor.fetchone()[0]
        
        # If no games in DB, get expected count from schedule
        if total_games == 0 and year == 2025:
            from nfl_2025_schedule import get_week_game_count
            total_games = get_week_game_count(week)
        
        # Get user's picks for this week
        cursor.execute('''
            SELECT COUNT(*) FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = ? AND g.year = ?
        ''', (user_id, week, year))
        user_picks_count = cursor.fetchone()[0]
        
        # Get other stats
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        total_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM weekly_results WHERE user_id = ? AND is_winner = 1', (user_id,))
        user_wins = cursor.fetchone()[0]
        
        return {
            'total_games': total_games,
            'user_picks_count': user_picks_count,
            'total_players': total_players,
            'user_wins': user_wins
        }

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    initialize_app()
    
    current_week = 1
    current_year = 2025  # Use 2025 for NFL schedule
    
    # Get actual game count from database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (current_week, current_year))
        total_games = cursor.fetchone()[0]
        
        # If no games exist, get expected count and suggest creation
        if total_games == 0:
            from nfl_2025_schedule import get_week_game_count
            expected_games = get_week_game_count(current_week)
            total_games = expected_games
    
    dashboard_data = get_dashboard_data(session['user_id'], current_week, current_year)
    
    data = {
        'current_week': current_week,
        'current_year': current_year,
        'username': session.get('username', 'User'),
        'user_picks_count': dashboard_data['user_picks_count'],
        'total_games': total_games,
        'user_wins': dashboard_data['user_wins'],
        'total_players': dashboard_data['total_players'],
        'available_weeks': list(range(1, 19))
    }
    
    return render_template('index.html', **data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username: str = request.form.get('username', '').strip()
        password: str = request.form.get('password', '').strip()
        
        if not username or not password:
            logger.warning(f"Login attempt with missing credentials from IP: {request.remote_addr}")
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['username'] = username
                session['is_admin'] = bool(user[2])
                logger.info(f"Successful login for user: {username}")
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                logger.warning(f"Failed login attempt for username: {username} from IP: {request.remote_addr}")
                flash('Invalid username or password', 'error')
                
        except sqlite3.Error as e:
            logger.error(f"Database error during login: {e}")
            flash('A system error occurred. Please try again later.', 'error')
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/sync_season', methods=['POST'])
def sync_season():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json or {}
    year = data.get('year', 2025)
    
    # Ensure we're using 2025 or later for BallDontLie API
    if year < 2025:
        year = 2025
    
    games_added = sync_season_from_api(year)
    
    if games_added > 0:
        return jsonify({
            'success': True,
            'message': f'Successfully synced {games_added} games from BallDontLie API for {year} season',
            'games_added': games_added
        })
    else:
        return jsonify({
            'error': f'Failed to sync season data from BallDontLie API for {year}. Check API configuration.'
        }), 500

@app.route('/admin/generate_week', methods=['POST'])
def admin_generate_week():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    week = data.get('week')
    year = data.get('year', 2025)
    
    games_created = sync_week_from_api(week, year)
    
    if games_created > 0:
        return jsonify({
            'success': True, 
            'games_created': games_created, 
            'message': f'Synced {games_created} games from NFL API for Week {week}'
        })
    else:
        return jsonify({
            'error': f'Failed to sync Week {week} from NFL API'
        }), 500

@app.route('/update_scores/<int:week>/<int:year>')
def update_scores(week, year):
    """Update live scores - can be called by anyone"""
    games_updated = update_live_scores(week, year)
    return jsonify({
        'success': True,
        'games_updated': games_updated,
        'message': f'Updated {games_updated} games with live scores'
    })

@app.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', 2025, type=int)
    
    # Auto-update live scores on page load
    update_live_scores(week, year)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM nfl_games 
        WHERE week = ? AND year = ? 
        ORDER BY game_date
    ''', (week, year))
    games_raw = cursor.fetchall()
    
    # Convert games to proper format with AST datetime objects
    games_data = []
    for game in games_raw:
        game_dict = dict(game)
        # Convert string date to datetime object and ensure AST
        if game_dict['game_date']:
            try:
                if isinstance(game_dict['game_date'], str):
                    dt = datetime.strptime(game_dict['game_date'], '%Y-%m-%d %H:%M:%S')
                    # Convert to AST
                    game_dict['game_date'] = convert_to_ast(dt)
            except (ValueError, TypeError):
                game_dict['game_date'] = None
        games_data.append(game_dict)
    
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
            logger.error(f"Registration error: {e}")
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

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM nfl_games 
        WHERE week = ? AND year = ? 
        ORDER BY game_date
    ''', (week, year))
    
    games = []
    for row in cursor.fetchall():
        games.append(dict(row))
    
    conn.close()
    return jsonify(games)

@app.route('/admin/create_game', methods=['POST'])
def admin_create_game():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    week = data.get('week')
    year = data.get('year')
    away_team = data.get('away_team')
    home_team = data.get('home_team')
    game_date = data.get('game_date')
    game_type = data.get('game_type', 'regular')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Generate unique game_id
    game_id = f"{game_type}_{year}_week_{week}_{away_team}_{home_team}"
    
    # Set game type flags
    is_thursday = game_type == 'thursday'
    is_sunday = game_type == 'sunday'
    is_monday = game_type == 'monday'
    
    cursor.execute('''
        INSERT INTO nfl_games 
        (week, year, game_id, away_team, home_team, game_date, 
         is_thursday_night, is_sunday_night, is_monday_night, game_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (week, year, game_id, away_team, home_team, game_date,
          is_thursday, is_sunday, is_monday, 'scheduled'))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Game created successfully'})

@app.route('/admin/update_game', methods=['POST'])
def admin_update_game():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    game_id = data.get('game_id')
    away_team = data.get('away_team')
    home_team = data.get('home_team')
    game_date = data.get('game_date')
    game_type = data.get('game_type')
    game_status = data.get('game_status')
    away_score = data.get('away_score')
    home_score = data.get('home_score')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Set game type flags
    is_thursday = game_type == 'thursday'
    is_sunday = game_type == 'sunday'
    is_monday = game_type == 'monday'
    is_final = game_status == 'final'
    
    cursor.execute('''
        UPDATE nfl_games SET 
        away_team = ?, home_team = ?, game_date = ?, 
        is_thursday_night = ?, is_sunday_night = ?, is_monday_night = ?,
        game_status = ?, away_score = ?, home_score = ?, is_final = ?
        WHERE id = ?
    ''', (away_team, home_team, game_date, is_thursday, is_sunday, is_monday,
          game_status, away_score, home_score, is_final, game_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Game updated successfully'})

@app.route('/admin/delete_game', methods=['POST'])
def admin_delete_game():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    game_id = data.get('game_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Delete user picks first
    cursor.execute('DELETE FROM user_picks WHERE game_id = ?', (game_id,))
    
    # Delete the game
    cursor.execute('DELETE FROM nfl_games WHERE id = ?', (game_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Game deleted successfully'})

@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if username exists
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400
    
    password_hash = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO users (username, password_hash, email, is_admin)
        VALUES (?, ?, ?, ?)
    ''', (username, password_hash, email, is_admin))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'User created successfully'})

@app.route('/admin/results')
def admin_results():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.*, 
               COUNT(up.id) as total_picks,
               COUNT(CASE WHEN up.selected_team = 
                   CASE WHEN g.home_score > g.away_score THEN g.home_team
                        WHEN g.away_score > g.home_score THEN g.away_team
                        ELSE NULL END THEN 1 END) as correct_picks
        FROM nfl_games g
        LEFT JOIN user_picks up ON g.id = up.game_id
        WHERE g.week = ? AND g.year = ?
        GROUP BY g.id
        ORDER BY g.game_date
    ''', (week, year))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    conn.close()
    return jsonify(results)

@app.route('/admin/calculate_results', methods=['POST'])
def admin_calculate_results():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    week = data.get('week')
    year = data.get('year')
    
    # Calculate weekly results logic here
    # This would determine winners based on picks vs actual results
    
    return jsonify({'success': True, 'message': 'Results calculated', 'winner': 'TBD'})

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, is_admin, created_at FROM users ORDER BY username')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2] or '',
                'is_admin': bool(row[3]),
                'created_at': row[4],
                'is_active': True,  # Add default value
                'last_login': None  # Add default value
            })
        
        conn.close()
        return jsonify(users)
        
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        return jsonify({'error': f'Failed to load users: {str(e)}'}), 500

@app.route('/admin/modify_user', methods=['POST'])
def admin_modify_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        email = data.get('email')
        is_admin = data.get('is_admin', False)
        new_password = data.get('new_password')
        
        conn = get_db()
        cursor = conn.cursor()
        
        if new_password:
            password_hash = generate_password_hash(new_password)
            cursor.execute('''
                UPDATE users SET username = ?, email = ?, is_admin = ?, password_hash = ? WHERE id = ?
            ''', (username, email, is_admin, password_hash, user_id))
        else:
            cursor.execute('''
                UPDATE users SET username = ?, email = ?, is_admin = ? WHERE id = ?
            ''', (username, email, is_admin, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User updated successfully'})
        
    except Exception as e:
        logger.error(f"Admin modify user error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete_user', methods=['POST'])
def admin_delete_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if user_id == session['user_id']:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Delete user picks first
        cursor.execute('DELETE FROM user_picks WHERE user_id = ?', (user_id,))
        
        # Delete weekly results
        cursor.execute('DELETE FROM weekly_results WHERE user_id = ?', (user_id,))
        
        # Delete user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        logger.error(f"Admin delete user error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

@app.route('/force_create_games/<int:week>/<int:year>')
def force_create_games(week, year):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('games'))
    
    try:
        if year == 2025:
            from nfl_2025_schedule import get_2025_nfl_schedule
            schedule = get_2025_nfl_schedule()
            
            if week in schedule:
                conn = get_db()
                cursor = conn.cursor()
                
                # Clear existing games for this week
                cursor.execute('DELETE FROM nfl_games WHERE week = ? AND year = ?', (week, year))
                
                games_created = 0
                for game in schedule[week]:
                    game_id = f"nfl_{year}_w{week}_{game['away_team']}_{game['home_team']}"
                    
                    cursor.execute('''
                        INSERT INTO nfl_games 
                        (week, year, game_id, away_team, home_team, game_date, 
                         is_thursday_night, is_monday_night, is_sunday_night, 
                         game_status, tv_network)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        week, year, game_id, game['away_team'], game['home_team'],
                        game['game_date'].strftime('%Y-%m-%d %H:%M:%S'),
                        game.get('is_thursday_night', False),
                        game.get('is_monday_night', False),
                        game.get('is_sunday_night', False),
                        'scheduled',
                        game.get('tv_network', 'TBD')
                    ))
                    games_created += 1
                
                conn.commit()
                conn.close()
                
                flash(f'Successfully created {games_created} games for Week {week}', 'success')
            else:
                flash(f'No schedule data available for Week {week}', 'error')
        else:
            flash(f'Schedule not available for year {year}', 'error')
    except Exception as e:
        flash(f'Error creating games: {str(e)}', 'error')
    
    return redirect(url_for('games', week=week, year=year))

@app.route('/admin/user_picks')
def admin_user_picks():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    user_id = request.args.get('user_id', type=int)
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', 2025, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT up.game_id, up.selected_team, up.predicted_home_score, up.predicted_away_score
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND g.week = ? AND g.year = ?
    ''', (user_id, week, year))
    
    picks = []
    for row in cursor.fetchall():
        picks.append({
            'game_id': row[0],
            'selected_team': row[1],
            'predicted_home_score': row[2],
            'predicted_away_score': row[3]
        })
    
    conn.close()
    return jsonify(picks)

@app.route('/admin/set_user_picks', methods=['POST'])
def admin_set_user_picks():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
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
            ''', (user_id, game_id, selected_team, home_score, away_score))
            successful_picks += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'message': f'Successfully set {successful_picks} picks for user',
        'picks_set': successful_picks
    })

@app.route('/admin/clear_user_picks', methods=['POST'])
def admin_clear_user_picks():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    week = data.get('week')
    year = data.get('year')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM user_picks 
        WHERE user_id = ? AND game_id IN (
            SELECT id FROM nfl_games WHERE week = ? AND year = ?
        )
    ''', (user_id, week, year))
    
    picks_cleared = cursor.rowcount
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Cleared {picks_cleared} picks for user',
        'picks_cleared': picks_cleared
    })

if __name__ == '__main__':
    print("🚀 Starting La Casa de Todos NFL Fantasy League...")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
