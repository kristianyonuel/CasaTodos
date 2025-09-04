from __future__ import annotations

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from setup_database import setup_complete_database
from database_sync import sync_season_from_api, sync_week_from_api, update_live_scores
from utils.timezone_utils import convert_to_ast, format_ast_time
from contextlib import contextmanager
from deadline_manager import DeadlineManager
from deadline_override_manager import DeadlineOverrideManager
import csv
import io
from werkzeug.utils import secure_filename

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
    
    # Get deadline information using deadline manager
    try:
        deadline_manager = DeadlineManager()
        deadline_summary = deadline_manager.get_user_deadline_summary(current_week, current_year, session['user_id'])
        
    except Exception as e:
        logger.error(f"Error getting deadlines: {e}")
        deadline_summary = {
            'thursday': None,
            'sunday': None,
            'monday': None,
            'next_deadline': None,
            'all_deadlines_passed': False
        }
    
    data = {
        'current_week': current_week,
        'current_year': current_year,
        'username': session.get('username', 'User'),
        'user_picks_count': dashboard_data['user_picks_count'],
        'total_games': total_games,
        'user_wins': dashboard_data['user_wins'],
        'total_players': dashboard_data['total_players'],
        'available_weeks': list(range(1, 19)),
        'deadline_summary': deadline_summary
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
    
    with get_db() as conn:
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
    
    # Get deadline information
    try:
        deadline_manager = DeadlineManager()
        deadline_data = deadline_manager.get_week_deadlines(week, year)
        
        # Convert to simple dict for template usage
        deadlines = {}
        deadline_status = {}
        
        for key, value in deadline_data.items():
            if value and isinstance(value, dict) and 'deadline' in value:
                deadlines[key] = value['deadline']
                deadline_status[key] = {
                    'passed': value['status']['is_closed'],
                    'hours_until': value['status']['hours_until_deadline']
                }
        
        # Simplify the key names for template
        simple_deadlines = {
            'thursday': deadlines.get('thursday_night'),
            'sunday': deadlines.get('sunday_games'),  
            'monday': deadlines.get('monday_night')
        }
        
        simple_status = {
            'thursday': deadline_status.get('thursday_night'),
            'sunday': deadline_status.get('sunday_games'),
            'monday': deadline_status.get('monday_night')
        }
        
    except Exception as e:
        logger.error(f"Error getting deadlines for games page: {e}")
        simple_deadlines = {}
        simple_status = {}
    
    return render_template('games.html',
                          games=games_data,
                          user_picks=user_picks,
                          current_week=week,
                          current_year=year,
                          available_weeks=list(range(1, 19)),
                          current_nfl_week=1,
                          total_games=len(games_data),
                          deadlines=simple_deadlines,
                          deadline_status=simple_status)

@app.route('/submit_picks', methods=['POST'])
def submit_picks():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    picks = data.get('picks', [])
    
    # Check deadlines before allowing submissions
    deadline_manager = DeadlineManager()
    
    with get_db() as conn:
        cursor = conn.cursor()
        successful_picks = 0
        failed_picks = 0
        
        for pick in picks:
            game_id = pick.get('game_id')
            selected_team = pick.get('selected_team')
            home_score = pick.get('home_score')
            away_score = pick.get('away_score')
            
            if game_id and selected_team:
                # Get game info to check deadline
                cursor.execute('SELECT week, year, game_date FROM nfl_games WHERE id = ?', (game_id,))
                game_info = cursor.fetchone()
                
                if game_info:
                    week, year, game_date = game_info
                    
                    # Check if picks are still allowed for this game
                    if deadline_manager.can_make_picks(week, year, game_date):
                        cursor.execute('''
                            INSERT OR REPLACE INTO user_picks 
                            (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (session['user_id'], game_id, selected_team, home_score, away_score))
                        successful_picks += 1
                    else:
                        failed_picks += 1
                        logger.warning(f"Pick submission after deadline for game {game_id} by user {session['user_id']}")
        
        conn.commit()
    
    if failed_picks > 0:
        return jsonify({
            'success': False, 
            'message': f'Some picks were rejected due to deadline. {successful_picks} picks saved, {failed_picks} rejected.',
            'partial': True
        })
    
    return jsonify({'success': True, 'message': f'Successfully submitted {successful_picks} picks!'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username: str = request.form.get('username', '').strip()
            password: str = request.form.get('password', '').strip()
            email: str = request.form.get('email', '').strip()
            
            # Validation
            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template('register.html')
            
            if len(username) < 3:
                flash('Username must be at least 3 characters long', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('register.html')
                
            # Optional email validation
            if email and '@' not in email:
                flash('Please enter a valid email address', 'error')
                return render_template('register.html')
            
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Check if username already exists
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                if cursor.fetchone():
                    flash('Username already exists. Please choose a different one.', 'error')
                    return render_template('register.html')
                
                # Check if email already exists (if provided)
                if email:
                    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
                    if cursor.fetchone():
                        flash('Email already registered. Please use a different email.', 'error')
                        return render_template('register.html')
                
                # Create new user
                password_hash = generate_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, is_admin, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password_hash, email or None, False, datetime.now()))
                
                conn.commit()
                logger.info(f"New user registered: {username}")
            
            flash('Registration successful! Please log in with your new account.', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error during registration: {e}")
            flash('Registration failed due to data conflict. Please try different credentials.', 'error')
        except sqlite3.Error as e:
            logger.error(f"Database error during registration: {e}")
            flash('Registration failed due to a database error. Please try again later.', 'error')
        except Exception as e:
            logger.error(f"Unexpected registration error: {e}")
            flash('Registration failed due to an unexpected error. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_legacy()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, 
               COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) as weekly_wins,
               SUM(COALESCE(wr.correct_picks, 0)) as total_games_won,
               COUNT(DISTINCT wr.week) as weeks_played,
               ROUND(AVG(COALESCE(wr.correct_picks, 0)), 1) as avg_games_won_per_week
        FROM users u
        LEFT JOIN weekly_results wr ON u.id = wr.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username
        ORDER BY weekly_wins DESC, total_games_won DESC, avg_games_won_per_week DESC
    ''')
    
    leaderboard_data = []
    for row in cursor.fetchall():
        leaderboard_data.append({
            'username': row[0],
            'weekly_wins': row[1] or 0,
            'total_games_won': row[2] or 0,
            'weeks_played': row[3] or 0,
            'avg_games_won_per_week': row[4] or 0.0
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

@app.route('/admin/all_picks')
def admin_all_picks():
    """Get all user picks for a specific week"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', 2025, type=int)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get picks for the week/year
            cursor.execute('''
                SELECT p.id as pick_id, p.user_id, p.game_id, p.selected_team, 
                       p.predicted_home_score, p.predicted_away_score, p.created_at
                FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE g.week = ? AND g.year = ?
            ''', (week, year))
            
            picks_data = cursor.fetchall()
            
            if not picks_data:
                return jsonify([])

            # Get user info
            user_ids = list(set(row['user_id'] for row in picks_data))
            if user_ids:
                placeholders = ','.join('?' * len(user_ids))
                cursor.execute(f'SELECT id, username FROM users WHERE id IN ({placeholders})', user_ids)
                users = {row['id']: row['username'] for row in cursor.fetchall()}
            else:
                users = {}
            
            # Get game info
            game_ids = list(set(row['game_id'] for row in picks_data))
            if game_ids:
                placeholders = ','.join('?' * len(game_ids))
                cursor.execute(f'''
                    SELECT id, away_team, home_team, game_date as game_time, 
                           COALESCE(is_monday_night, 0) as is_monday_night
                    FROM nfl_games WHERE id IN ({placeholders})
                ''', game_ids)
                games = {row['id']: row for row in cursor.fetchall()}
            else:
                games = {}
            
            # Combine the data
            picks = []
            for pick in picks_data:
                user_id = pick['user_id']
                game_id = pick['game_id']
                
                if user_id in users and game_id in games:
                    game = games[game_id]
                    picks.append({
                        'pick_id': pick['pick_id'],
                        'username': users[user_id],
                        'away_team': game['away_team'],
                        'home_team': game['home_team'],
                        'game_time': game['game_time'],
                        'is_monday_night': bool(game['is_monday_night']),
                        'selected_team': pick['selected_team'],
                        'predicted_home_score': pick['predicted_home_score'],
                        'predicted_away_score': pick['predicted_away_score'],
                        'pick_time': pick['created_at']
                    })
            
            return jsonify(picks)
            
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/admin/update_pick', methods=['POST'])
def admin_update_pick():
    """Update a user's pick"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        pick_id = data.get('pick_id')
        selected_team = data.get('selected_team')
        predicted_away_score = data.get('predicted_away_score')
        predicted_home_score = data.get('predicted_home_score')
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_picks 
                SET selected_team = ?, predicted_away_score = ?, predicted_home_score = ?
                WHERE id = ?
            ''', (selected_team, predicted_away_score, predicted_home_score, pick_id))
            conn.commit()
            
        logger.info(f"Admin {session['username']} updated pick {pick_id}")
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating pick: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete_pick', methods=['POST'])
def admin_delete_pick():
    """Delete a user's pick"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        pick_id = data.get('pick_id')
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_picks WHERE id = ?', (pick_id,))
            conn.commit()
            
        logger.info(f"Admin {session['username']} deleted pick {pick_id}")
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error deleting pick: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM nfl_games 
            WHERE week = ? AND year = ? 
            ORDER BY game_date
        ''', (week, year))
        
        games = []
        for row in cursor.fetchall():
            games.append(dict(row))
    
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
    
    with get_db() as conn:
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
    
    return jsonify({'success': True, 'message': 'Game created successfully'})

@app.route('/admin/update_game', methods=['POST'])
def admin_update_game():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        away_team = data.get('away_team')
        home_team = data.get('home_team')
        game_date = data.get('game_date')
        game_type = data.get('game_type')
        game_status = data.get('game_status')
        away_score = data.get('away_score')
        home_score = data.get('home_score')
        
        with get_db() as conn:
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
        
        return jsonify({'success': True, 'message': 'Game updated successfully'})
        
    except Exception as e:
        logger.error(f"Admin update game error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete_game', methods=['POST'])
def admin_delete_game():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Delete user picks first (foreign key constraint)
            cursor.execute('DELETE FROM user_picks WHERE game_id = ?', (game_id,))
            
            # Delete the game
            cursor.execute('DELETE FROM nfl_games WHERE id = ?', (game_id,))
            
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Game deleted successfully'})
        
    except Exception as e:
        logger.error(f"Admin delete game error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return jsonify({'error': 'Username already exists'}), 400
            
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, is_admin, datetime.now()))
            
            conn.commit()
        
        return jsonify({'success': True, 'message': 'User created successfully'})
        
    except Exception as e:
        logger.error(f"Admin create user error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/results')
def admin_results():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    try:
        with get_db() as conn:
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
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Admin results error: {e}")
        return jsonify({'error': str(e)}), 500

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
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, is_admin, created_at, last_login 
                FROM users 
                ORDER BY username
            ''')
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2] or '',
                    'is_admin': bool(row[3]),
                    'created_at': row[4],
                    'is_active': True,  # Add default value
                    'last_login': row[5]  # Get actual last_login value
                })
        
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
        
        with get_db() as conn:
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
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Delete user picks first (foreign key constraint)
            cursor.execute('DELETE FROM user_picks WHERE user_id = ?', (user_id,))
            
            # Delete weekly results
            cursor.execute('DELETE FROM weekly_results WHERE user_id = ?', (user_id,))
            
            # Delete user
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
        
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
                with get_db() as conn:
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
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT up.game_id, up.selected_team, up.predicted_home_score, up.predicted_away_score,
                       g.home_team, g.away_team, g.game_date
                FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE up.user_id = ? AND g.week = ? AND g.year = ?
                ORDER BY g.game_date
            ''', (user_id, week, year))
            
            picks = []
            for row in cursor.fetchall():
                picks.append({
                    'game_id': row[0],
                    'selected_team': row[1],
                    'predicted_home_score': row[2],
                    'predicted_away_score': row[3],
                    'home_team': row[4],
                    'away_team': row[5],
                    'game_date': row[6]
                })
        
        return jsonify(picks)
        
    except Exception as e:
        logger.error(f"Admin user picks error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/set_user_picks', methods=['POST'])
def admin_set_user_picks():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        picks = data.get('picks', [])
        
        with get_db() as conn:
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
                        (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, game_id, selected_team, home_score, away_score, datetime.now()))
                    successful_picks += 1
            
            conn.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully set {successful_picks} picks for user',
            'picks_set': successful_picks
        })
        
    except Exception as e:
        logger.error(f"Admin set user picks error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/clear_user_picks', methods=['POST'])
def admin_clear_user_picks():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        week = data.get('week')
        year = data.get('year')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM user_picks 
                WHERE user_id = ? AND game_id IN (
                    SELECT id FROM nfl_games WHERE week = ? AND year = ?
                )
            ''', (user_id, week, year))
            
            picks_cleared = cursor.rowcount
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {picks_cleared} picks for user',
            'picks_cleared': picks_cleared
        })
        
    except Exception as e:
        logger.error(f"Admin clear user picks error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/deadline_overrides', methods=['GET'])
def admin_deadline_overrides():
    """Get deadline overrides for admin panel"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        week = request.args.get('week', 1, type=int)
        year = request.args.get('year', 2025, type=int)
        
        override_manager = DeadlineOverrideManager()
        overrides = override_manager.get_active_overrides(week, year)
        
        # Get all users for the dropdown
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users ORDER BY username')
            users = [{'id': row[0], 'username': row[1]} for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'overrides': overrides,
            'users': users
        })
        
    except Exception as e:
        logger.error(f"Error getting deadline overrides: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/create_deadline_override', methods=['POST'])
def admin_create_deadline_override():
    """Create a new deadline override"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        week = data.get('week')
        year = data.get('year')
        deadline_type = data.get('deadline_type')
        user_id = data.get('user_id')
        new_deadline_str = data.get('new_deadline')
        reason = data.get('reason', '')
        
        if not all([week, year, deadline_type, new_deadline_str]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Convert deadline string to datetime
        new_deadline = datetime.fromisoformat(new_deadline_str.replace('T', ' '))
        
        override_manager = DeadlineOverrideManager()
        success = override_manager.create_override(
            week=week,
            year=year,
            deadline_type=deadline_type,
            new_deadline=new_deadline,
            admin_id=session['user_id'],
            user_id=user_id,
            reason=reason
        )
        
        if success:
            logger.info(f"Admin {session['username']} created deadline override for week {week}, {year}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to create override'})
            
    except Exception as e:
        logger.error(f"Error creating deadline override: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/remove_deadline_override', methods=['POST'])
def admin_remove_deadline_override():
    """Remove a deadline override"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        override_id = data.get('override_id')
        
        if not override_id:
            return jsonify({'success': False, 'error': 'Override ID required'})
        
        override_manager = DeadlineOverrideManager()
        success = override_manager.remove_override(override_id, session['user_id'])
        
        if success:
            logger.info(f"Admin {session['username']} removed deadline override {override_id}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to remove override'})
            
    except Exception as e:
        logger.error(f"Error removing deadline override: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/emergency_deadline_extension', methods=['POST'])
def admin_emergency_deadline_extension():
    """Emergency deadline extension - extends all deadlines by specified hours"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        week = data.get('week', 1)
        year = data.get('year', 2025)
        hours_to_extend = data.get('hours', 1)
        reason = data.get('reason', 'Emergency deadline extension')
        
        if not hours_to_extend or hours_to_extend <= 0:
            return jsonify({'success': False, 'error': 'Invalid extension hours'})
        
        override_manager = DeadlineOverrideManager()
        current_time = datetime.now()
        new_deadline = current_time + timedelta(hours=hours_to_extend)
        
        # Create global overrides for all deadline types
        deadline_types = ['thursday', 'sunday', 'monday']
        created_overrides = 0
        
        for deadline_type in deadline_types:
            success = override_manager.create_override(
                week=week,
                year=year,
                deadline_type=deadline_type,
                new_deadline=new_deadline,
                admin_id=session['user_id'],
                user_id=None,  # Global override
                reason=f"EMERGENCY: {reason}"
            )
            if success:
                created_overrides += 1
        
        logger.info(f"Admin {session['username']} created emergency deadline extension: {hours_to_extend} hours for week {week}")
        
        return jsonify({
            'success': True, 
            'message': f'Emergency extension created: {created_overrides} deadline types extended by {hours_to_extend} hours'
        })
        
    except Exception as e:
        logger.error(f"Error creating emergency deadline extension: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/export_picks_csv', methods=['GET'])
def admin_export_picks_csv():
    """Export all user picks for a week as CSV"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        week = request.args.get('week', 1, type=int)
        year = request.args.get('year', 2025, type=int)
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get all games for the week
            cursor.execute('''
                SELECT id, away_team, home_team, game_date, is_monday_night
                FROM nfl_games 
                WHERE week = ? AND year = ?
                ORDER BY game_date
            ''', (week, year))
            
            games = [dict(row) for row in cursor.fetchall()]
            
            if not games:
                return jsonify({'error': f'No games found for Week {week}, {year}'}), 404
            
            # Get all users
            cursor.execute('SELECT id, username FROM users ORDER BY username')
            users = [dict(row) for row in cursor.fetchall()]
            
            # Get existing picks
            cursor.execute('''
                SELECT up.user_id, up.game_id, up.selected_team, 
                       up.predicted_home_score, up.predicted_away_score,
                       u.username
                FROM user_picks up
                JOIN users u ON up.user_id = u.id
                JOIN nfl_games g ON up.game_id = g.id
                WHERE g.week = ? AND g.year = ?
            ''', (week, year))
            
            picks = {}
            for row in cursor.fetchall():
                key = (row['user_id'], row['game_id'])
                picks[key] = {
                    'selected_team': row['selected_team'],
                    'predicted_home_score': row['predicted_home_score'],
                    'predicted_away_score': row['predicted_away_score']
                }
        
        # Create CSV content
        output = io.StringIO()
        fieldnames = ['username', 'game_id', 'away_team', 'home_team', 'selected_team', 
                     'predicted_home_score', 'predicted_away_score']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Write a row for each user-game combination
        for user in users:
            for game in games:
                pick_key = (user['id'], game['id'])
                pick_data = picks.get(pick_key, {})
                
                row = {
                    'username': user['username'],
                    'game_id': game['id'],
                    'away_team': game['away_team'],
                    'home_team': game['home_team'],
                    'selected_team': pick_data.get('selected_team', ''),
                    'predicted_home_score': pick_data.get('predicted_home_score', ''),
                    'predicted_away_score': pick_data.get('predicted_away_score', '')
                }
                writer.writerow(row)
        
        # Prepare response
        csv_content = output.getvalue()
        output.close()
        
        response = app.response_class(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=picks_week_{week}_{year}.csv'}
        )
        
        logger.info(f"Admin {session['username']} exported picks CSV for Week {week}, {year}")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting picks CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/import_picks_csv', methods=['POST'])
def admin_import_picks_csv():
    """Import user picks from CSV file"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        week = request.args.get('week', 1, type=int)
        year = request.args.get('year', 2025, type=int)
        validate_only = request.form.get('validate_only') == 'true'
        overwrite_existing = request.form.get('overwrite_existing') == 'true'
        create_missing_users = request.form.get('create_missing_users') == 'true'
        
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file provided'}), 400
        
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        # Read and parse CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Validation variables
        total_rows = 0
        valid_picks = 0
        empty_picks = 0
        users_found = set()
        missing_users = set()
        warnings = []
        errors = []
        
        # Import variables
        picks_imported = 0
        picks_updated = 0
        users_created = 0
        skipped_picks = 0
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get existing users
            cursor.execute('SELECT id, username FROM users')
            existing_users = {row['username']: row['id'] for row in cursor.fetchall()}
            
            # Get existing games for the week
            cursor.execute('''
                SELECT id, away_team, home_team FROM nfl_games 
                WHERE week = ? AND year = ?
            ''', (week, year))
            existing_games = {row['id']: row for row in cursor.fetchall()}
            
            picks_to_process = []
            
            for row in csv_reader:
                total_rows += 1
                
                username = row.get('username', '').strip()
                game_id = row.get('game_id', '').strip()
                selected_team = row.get('selected_team', '').strip()
                predicted_home_score = row.get('predicted_home_score', '').strip()
                predicted_away_score = row.get('predicted_away_score', '').strip()
                
                if not username:
                    errors.append(f"Row {total_rows}: Missing username")
                    continue
                
                if not game_id or not game_id.isdigit():
                    errors.append(f"Row {total_rows}: Invalid game_id '{game_id}'")
                    continue
                
                game_id = int(game_id)
                
                if game_id not in existing_games:
                    errors.append(f"Row {total_rows}: Game ID {game_id} not found for Week {week}, {year}")
                    continue
                
                if not selected_team:
                    empty_picks += 1
                    continue
                
                # Validate team name
                game = existing_games[game_id]
                if selected_team not in [game['away_team'], game['home_team']]:
                    errors.append(f"Row {total_rows}: '{selected_team}' is not valid for {game['away_team']} @ {game['home_team']}")
                    continue
                
                # Check user exists
                if username in existing_users:
                    users_found.add(username)
                    user_id = existing_users[username]
                else:
                    missing_users.add(username)
                    if not create_missing_users:
                        warnings.append(f"User '{username}' not found and user creation disabled")
                        continue
                    user_id = None  # Will create later
                
                # Validate score predictions
                home_score = None
                away_score = None
                if predicted_home_score:
                    try:
                        home_score = int(predicted_home_score)
                    except ValueError:
                        warnings.append(f"Row {total_rows}: Invalid home score '{predicted_home_score}'")
                
                if predicted_away_score:
                    try:
                        away_score = int(predicted_away_score)
                    except ValueError:
                        warnings.append(f"Row {total_rows}: Invalid away score '{predicted_away_score}'")
                
                picks_to_process.append({
                    'username': username,
                    'user_id': user_id,
                    'game_id': game_id,
                    'selected_team': selected_team,
                    'predicted_home_score': home_score,
                    'predicted_away_score': away_score
                })
                
                valid_picks += 1
            
            # If validation only, return results
            if validate_only:
                return jsonify({
                    'success': True,
                    'total_rows': total_rows,
                    'valid_picks': valid_picks,
                    'empty_picks': empty_picks,
                    'users_found': len(users_found),
                    'missing_users': list(missing_users),
                    'warnings': warnings
                })
            
            # Process imports
            for pick in picks_to_process:
                try:
                    # Create user if needed
                    if pick['user_id'] is None:
                        cursor.execute('''
                            INSERT INTO users (username, password_hash, email, is_admin)
                            VALUES (?, ?, ?, ?)
                        ''', (pick['username'], generate_password_hash('changeme123'), '', False))
                        pick['user_id'] = cursor.lastrowid
                        users_created += 1
                        existing_users[pick['username']] = pick['user_id']
                    
                    # Check if pick already exists
                    cursor.execute('''
                        SELECT id FROM user_picks 
                        WHERE user_id = ? AND game_id = ?
                    ''', (pick['user_id'], pick['game_id']))
                    
                    existing_pick = cursor.fetchone()
                    
                    if existing_pick and not overwrite_existing:
                        skipped_picks += 1
                        continue
                    
                    # Insert or update pick
                    if existing_pick:
                        cursor.execute('''
                            UPDATE user_picks 
                            SET selected_team = ?, predicted_home_score = ?, predicted_away_score = ?
                            WHERE user_id = ? AND game_id = ?
                        ''', (pick['selected_team'], pick['predicted_home_score'], 
                             pick['predicted_away_score'], pick['user_id'], pick['game_id']))
                        picks_updated += 1
                    else:
                        cursor.execute('''
                            INSERT INTO user_picks 
                            (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (pick['user_id'], pick['game_id'], pick['selected_team'], 
                             pick['predicted_home_score'], pick['predicted_away_score']))
                        picks_imported += 1
                
                except Exception as e:
                    errors.append(f"Error processing pick for {pick['username']}: {str(e)}")
            
            conn.commit()
        
        logger.info(f"Admin {session['username']} imported {picks_imported + picks_updated} picks from CSV for Week {week}, {year}")
        
        return jsonify({
            'success': True,
            'picks_imported': picks_imported,
            'picks_updated': picks_updated,
            'users_created': users_created,
            'skipped_picks': skipped_picks,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error importing picks CSV: {e}")
        return jsonify({'error': str(e)}, 500)

@app.route('/admin/simple_picks')
def admin_simple_picks():
    """Simple picks view - shows basic pick data without complex joins"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get all picks with minimal joins
            cursor.execute('''
                SELECT p.id, p.user_id, p.game_id, p.selected_team, p.created_at,
                       u.username
                FROM user_picks p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.id DESC
                LIMIT 50
            ''')
            
            picks = []
            for row in cursor.fetchall():
                picks.append({
                    'pick_id': row['id'],
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'game_id': row['game_id'],
                    'selected_team': row['selected_team'],
                    'pick_time': row['created_at']
                })
            
            return jsonify(picks)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/weekly_leaderboard')
@app.route('/weekly_leaderboard/<int:week>')
@app.route('/weekly_leaderboard/<int:week>/<int:year>')
def weekly_leaderboard(week=None, year=None):
    """Weekly leaderboard with Monday Night tiebreaker logic"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Default to current week if not specified
    if week is None:
        # Calculate current NFL week based on date
        from datetime import datetime
        current_date = datetime.now()
        # NFL season typically starts first week of September
        season_start = datetime(2025, 9, 4)  # 2025 season start
        days_since_start = (current_date - season_start).days
        week = max(1, min(18, (days_since_start // 7) + 1))
    if year is None:
        year = 2025
    
    try:
        conn = get_db_legacy()
        cursor = conn.cursor()
        
        # First, check if we have any completed games for this week
        cursor.execute('''
            SELECT COUNT(*) FROM nfl_games 
            WHERE week = ? AND year = ? AND is_final = 1
        ''', (week, year))
        completed_games = cursor.fetchone()[0]
        
        if completed_games == 0:
            # No completed games, show message
            cursor.execute('''
                SELECT DISTINCT week, year 
                FROM nfl_games 
                WHERE is_final = 1
                ORDER BY year DESC, week DESC
                LIMIT 10
            ''')
            available_weeks = cursor.fetchall()
            conn.close()
            
            return render_template('weekly_leaderboard.html', 
                                 leaderboard=[],
                                 current_week=week,
                                 current_year=year,
                                 available_weeks=available_weeks,
                                 no_data_message=f"No completed games for Week {week}, {year}")
        
        # Get users who made picks for this week with simplified scoring (1 point per win)
        cursor.execute('''
            SELECT u.id, u.username,
                   COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.week = ? AND g.year = ? AND g.is_final = 1 AND u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING total_picks > 0
            ORDER BY correct_picks DESC, u.username
        ''', (week, year))
        
        user_results = cursor.fetchall()
        
        # Get Monday Night data for tiebreakers
        leaderboard_data = []
        for i, (user_id, username, total_picks, correct_picks) in enumerate(user_results, 1):
            
            # Get Monday Night pick data for this user
            cursor.execute('''
                SELECT p.predicted_home_score, p.predicted_away_score,
                       g.home_score, g.away_score, g.home_team, g.away_team
                FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE p.user_id = ? AND g.week = ? AND g.year = ? 
                  AND g.is_monday_night = 1 AND g.is_final = 1
                LIMIT 1
            ''', (user_id, week, year))
            
            monday_pick = cursor.fetchone()
            
            # Calculate Monday Night tiebreaker data
            monday_tiebreaker = {'has_pick': False}
            if monday_pick:
                pred_home = monday_pick[0] or 0
                pred_away = monday_pick[1] or 0
                actual_home = monday_pick[2] or 0
                actual_away = monday_pick[3] or 0
                
                monday_tiebreaker = {
                    'has_pick': True,
                    'home_diff': abs(pred_home - actual_home),
                    'away_diff': abs(pred_away - actual_away),
                    'total_diff': abs((pred_home + pred_away) - (actual_home + actual_away)),
                    'home_team': monday_pick[4] or '',
                    'away_team': monday_pick[5] or '',
                    'predicted_home': pred_home,
                    'predicted_away': pred_away,
                    'actual_home': actual_home,
                    'actual_away': actual_away
                }
            
            leaderboard_data.append({
                'rank': i,
                'username': username,
                'total_score': correct_picks,  # 1 point per correct pick
                'total_picks': total_picks,
                'correct_picks': correct_picks,
                'breakdown': {
                    'games_won': correct_picks,
                    'games_played': total_picks,
                    'win_percentage': round((correct_picks / total_picks * 100) if total_picks > 0 else 0, 1),
                    'total_score': correct_picks  # Same as correct_picks since 1 point per win
                },
                'monday_tiebreaker': monday_tiebreaker,
                'is_winner': i == 1
            })
        
        # Re-sort with Monday Night tiebreaker logic if there are ties
        # Simplified: 1 point per win, then Monday Night tiebreakers
        leaderboard_data.sort(key=lambda x: (
            -x['correct_picks'],                               # Most games won (1 point each)
            x['monday_tiebreaker'].get('home_diff', 999),      # Closest to home team
            x['monday_tiebreaker'].get('away_diff', 999),      # Closest to away team
            x['monday_tiebreaker'].get('total_diff', 999),     # Closest to total
            x['username']                                      # Alphabetical as final tiebreaker
        ))
        
        # Update ranks after sorting
        for i, user in enumerate(leaderboard_data, 1):
            user['rank'] = i
            user['is_winner'] = i == 1
        
        # Get available weeks for navigation
        cursor.execute('''
            SELECT DISTINCT week, year 
            FROM nfl_games 
            WHERE is_final = 1
            ORDER BY year DESC, week DESC
            LIMIT 10
        ''')
        available_weeks = cursor.fetchall()
        conn.close()
        
        return render_template('weekly_leaderboard.html', 
                             leaderboard=leaderboard_data,
                             current_week=week,
                             current_year=year,
                             available_weeks=available_weeks)
    
    except Exception as e:
        logger.error(f"Error in weekly leaderboard: {e}")
        flash(f'Error loading weekly leaderboard: {str(e)}', 'error')
        return redirect(url_for('leaderboard'))

@app.route('/debug_leaderboard')
def debug_leaderboard():
    """Debug route to test leaderboard functionality"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    try:
        debug_info = []
        conn = get_db_legacy()
        cursor = conn.cursor()
        
        # Check database structure
        debug_info.append("=== DATABASE STRUCTURE ===")
        
        # Check users table
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        user_count = cursor.fetchone()[0]
        debug_info.append(f"Non-admin users: {user_count}")
        
        # Check games table
        cursor.execute('SELECT COUNT(*) FROM nfl_games')
        total_games = cursor.fetchone()[0]
        debug_info.append(f"Total games: {total_games}")
        
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final = 1')
        completed_games = cursor.fetchone()[0]
        debug_info.append(f"Completed games: {completed_games}")
        
        # Check picks table
        cursor.execute('SELECT COUNT(*) FROM user_picks')
        total_picks = cursor.fetchone()[0]
        debug_info.append(f"Total picks: {total_picks}")
        
        # Sample games data
        debug_info.append("\n=== SAMPLE GAMES ===")
        cursor.execute('''
            SELECT game_id, week, year, home_team, away_team, is_final, is_monday_night
            FROM nfl_games 
            ORDER BY year DESC, week DESC, game_date DESC
            LIMIT 5
        ''')
        games = cursor.fetchall()
        for game in games:
            debug_info.append(f"Game: {game[0]} - Week {game[1]}/{game[2]} - {game[3]} vs {game[4]} - Final: {game[5]} - MNF: {game[6]}")
        
        # Current week calculation
        debug_info.append("\n=== CURRENT WEEK CALCULATION ===")
        from datetime import datetime
        current_date = datetime.now()
        season_start = datetime(2025, 9, 4)
        days_since_start = (current_date - season_start).days
        calculated_week = max(1, min(18, (days_since_start // 7) + 1))
        debug_info.append(f"Current date: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
        debug_info.append(f"Days since season start: {days_since_start}")
        debug_info.append(f"Calculated week: {calculated_week}")
        
        # Test leaderboard query
        debug_info.append("\n=== LEADERBOARD QUERY TEST ===")
        week = calculated_week
        year = 2025
        
        cursor.execute('''
            SELECT u.id, u.username,
                   COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as games_won
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.week = ? AND g.year = ? AND g.is_final = 1 AND u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING total_picks > 0
            ORDER BY games_won DESC, u.username
        ''', (week, year))
        
        results = cursor.fetchall()
        debug_info.append(f"Query for Week {week}, {year} returned {len(results)} users")
        for result in results:
            debug_info.append(f"  User: {result[1]} - Total Picks: {result[2]} - Games Won: {result[3]} - Points: {result[3]} (1 pt per win)")
        
        conn.close()
        
        # Return debug info as plain text
        return '<pre>' + '\n'.join(debug_info) + '</pre>'
        
    except Exception as e:
        return f'<pre>Error in debug: {str(e)}</pre>'

if __name__ == '__main__':
    import os
    import ssl
    from werkzeug.serving import make_server
    
    # Initialize the database on startup
    initialize_app()
    
    # Simple SSL context setup for existing certificates
    def setup_ssl_context():
        """Setup SSL context using existing certificates"""
        try:
            # Look for standard SSL certificate files
            cert_files = [
                ('cert.pem', 'key.pem'),
                ('certificate.crt', 'private.key'),
                ('ssl_cert.pem', 'ssl_key.pem'),
                ('fullchain.pem', 'privkey.pem')  # Let's Encrypt format
            ]
            
            for cert_file, key_file in cert_files:
                if os.path.exists(cert_file) and os.path.exists(key_file):
                    logger.info(f"Using SSL certificates: {cert_file}, {key_file}")
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    context.load_cert_chain(cert_file, key_file)
                    return context
            
            logger.warning("No SSL certificates found. HTTPS will not be available.")
            return None
            
        except Exception as e:
            logger.error(f"Error setting up SSL: {e}")
            return None
    
    # Serve .well-known directory for SSL validation
    @app.route('/.well-known/<path:filename>')
    def wellknown(filename):
        """Serve files from .well-known directory for SSL validation"""
        try:
            return app.send_static_file(f'.well-known/{filename}')
        except:
            # If not in static, try current directory
            well_known_path = os.path.join('.well-known', filename)
            if os.path.exists(well_known_path):
                with open(well_known_path, 'r') as f:
                    return f.read(), 200, {'Content-Type': 'text/plain'}
            else:
                return 'File not found', 404
    
    # Determine run mode
    import sys
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else 'production'
    
    print("🏈 La Casa de Todos NFL Fantasy Server")
    print("=" * 50)
    
    if mode == 'dev':
        print("🛠️ Development Mode")
        print("📍 Access at: http://localhost:5000")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    else:
        # Production mode - HTTP on 80, HTTPS on 443 if certificates available
        print("🚀 Production Mode")
        print("🌐 HTTP Server: Starting on port 80...")
        
        ssl_context = setup_ssl_context()
        if ssl_context:
            print("🔒 HTTPS Server: SSL certificates found, starting on port 443...")
        else:
            print("⚠️ HTTPS Server: No SSL certificates, HTTPS disabled")
        
        print("📍 Access URLs:")
        print("   🌐 HTTP:  http://your-domain.com")
        if ssl_context:
            print("   🔒 HTTPS: https://your-domain.com")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            # Start HTTP server
            http_server = make_server('0.0.0.0', 80, app, threaded=True)
            print("✅ HTTP server started on port 80")
            
            if ssl_context:
                # Start HTTPS server if SSL is available
                import threading
                
                def run_https():
                    try:
                        https_server = make_server('0.0.0.0', 443, app, ssl_context=ssl_context, threaded=True)
                        print("✅ HTTPS server started on port 443")
                        https_server.serve_forever()
                    except Exception as e:
                        logger.error(f"HTTPS server error: {e}")
                
                https_thread = threading.Thread(target=run_https, daemon=True)
                https_thread.start()
            
            # Run HTTP server in main thread
            http_server.serve_forever()
            
        except PermissionError:
            print("❌ Permission denied for ports 80/443")
            print("💡 Try running with sudo or use development mode:")
            print("   sudo python app.py production")
            print("   python app.py dev")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
        except Exception as e:
            logger.error(f"Server error: {e}")
            print(f"❌ Server error: {e}")
            print("� Try development mode: python app.py dev")
