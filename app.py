from __future__ import annotations

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response, after_this_request
import sqlite3
import os
import logging
import csv
from io import StringIO
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
from background_updater import start_background_updater, stop_background_updater, get_updater_status
import atexit

# Import predictable winner analysis
from predictable_winner import get_winner_prediction_summary, analyze_predictable_winners

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

# Helper function for flexible datetime parsing
def parse_game_date(date_string):
    """Parse game_date string with multiple format support"""
    if not date_string:
        return None
    
    if not isinstance(date_string, str):
        return date_string  # Already a datetime object
    
    # Try multiple datetime formats
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # If none worked, log and return None
    logger.error(f"Unable to parse date format: {date_string}")
    return None

app = Flask(__name__)
app.secret_key = 'nfl-fantasy-secret-key-2024'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True
app.config['DEBUG'] = True

# Force template cache clearing
if app.debug:
    app.jinja_env.cache = {}
    from jinja2 import FileSystemLoader
    app.jinja_loader = FileSystemLoader(app.template_folder)

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
    
    # Ensure weekly_results table exists and is up to date
    try:
        from scoring_updater import create_weekly_results_table_if_not_exists
        create_weekly_results_table_if_not_exists()
        print("Weekly results table verified")
    except Exception as e:
        logger.error(f"Error initializing weekly results table: {e}")

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


# Security middleware to handle suspicious requests
@app.before_request
def security_headers():
    """Add security headers and block suspicious requests"""
    # Block requests for common vulnerability scan paths
    suspicious_paths = [
        '/.env', '/.env.save', '/.env.backup', '/hudson', 
        '/jenkins', '/wp-admin', '/admin.php', '/config.php',
        '/phpinfo.php', '/wp-config.php'
    ]
    
    if request.path in suspicious_paths:
        logger.warning(f"Blocked suspicious request: {request.remote_addr} -> {request.path}")
        return "Not Found", 404
    
    # Add security headers to all responses
    @after_this_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

@app.route('/', methods=['GET', 'POST'])
def index():
    # Handle POST requests (often from bots/crawlers)
    if request.method == 'POST':
        return redirect(url_for('login')), 302
    
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    initialize_app()
    
    # Use smart NFL week calculation based on game completion
    try:
        from nfl_week_calculator import get_current_nfl_week
        current_week = get_current_nfl_week(2025)
    except Exception as e:
        logger.error(f"Error calculating current week: {e}")
        current_week = 1  # Fallback
    
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
        'deadline_summary': deadline_summary,
        'is_admin': session.get('is_admin', False)
    }
    
    # Create response with cache-busting headers to prevent browser caching issues
    response = make_response(render_template('index.html', **data))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    return response


@app.after_request
def add_cache_busting_headers(response):
    """Add cache-busting headers to prevent browser caching issues"""
    # Only add to HTML responses to avoid breaking static files
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        # Add cache buster to force refresh
        response.headers['X-Cache-Buster'] = str(int(datetime.now().timestamp()))
    return response


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
                # Case-insensitive username lookup using LOWER()
                cursor.execute('SELECT id, username, password_hash, is_admin FROM users WHERE LOWER(username) = LOWER(?)', (username,))
                user = cursor.fetchone()
            
                if user and check_password_hash(user[2], password):
                    session['user_id'] = user[0]
                    session['username'] = user[1]  # Use the actual username from database (preserves original case)
                    session['is_admin'] = bool(user[3])
                    session['login_time'] = datetime.now().isoformat()  # Track login time
                    
                    # Update last_login timestamp within the same transaction
                    try:
                        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user[0]))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Failed to update last_login for user {user[1]}: {e}")
                    
                    logger.info(f"Successful login for user: {user[1]} (entered as: {username})")
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

@app.route('/reset_password', methods=['POST'])
def reset_password():
    """Handle password reset requests"""
    username = request.form.get('username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    if not username or not new_password or not confirm_password:
        flash('All fields are required for password reset', 'error')
        return redirect(url_for('login'))
    
    if new_password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('login'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('login'))
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT id FROM users WHERE LOWER(username) = LOWER(?)', (username,))
            user = cursor.fetchone()
            
            if not user:
                flash('Username not found', 'error')
                return redirect(url_for('login'))
            
            # Update password
            password_hash = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user[0]))
            conn.commit()
            
            logger.info(f"Password reset successful for user: {username}")
            flash('Password reset successful! You can now login with your new password.', 'success')
            
    except sqlite3.Error as e:
        logger.error(f"Database error during password reset: {e}")
        flash('A system error occurred. Please try again later.', 'error')
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
    
    return redirect(url_for('login'))

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
    elif games_added == 0:
        # Check if sync was blocked due to existing picks
        import sqlite3
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM user_picks up 
            JOIN nfl_games g ON up.game_id = g.id 
            WHERE g.year = ?
        ''', (year,))
        existing_picks = cursor.fetchone()[0]
        conn.close()
        
        if existing_picks > 0:
            return jsonify({
                'error': f'Sync blocked: {existing_picks} user picks exist for {year}. Use "Update Game Results" for safe updates instead.'
            }), 400
        else:
            return jsonify({
                'error': f'Failed to sync season data from BallDontLie API for {year}. Check API configuration.'
            }), 500
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
    """Update live scores - can be called by anyone but respects rate limits"""
    from api_rate_limiter import check_api_rate_limit, get_api_calls_remaining
    
    if not check_api_rate_limiter():
        return jsonify({
            'error': 'API rate limit exceeded',
            'calls_remaining': get_api_calls_remaining(),
            'message': f'Please wait before making another API call. Calls remaining: {get_api_calls_remaining()}'
        }), 429
    
    games_updated = update_live_scores(week, year)
    remaining_calls = get_api_calls_remaining()
    
    return jsonify({
        'success': True,
        'games_updated': games_updated,
        'calls_remaining': remaining_calls,
        'message': f'Updated {games_updated} games with live scores. API calls remaining: {remaining_calls}'
    })

@app.route('/api_status')
def api_status():
    """Check API rate limit status"""
    from api_rate_limiter import get_api_calls_remaining, get_next_api_call_time
    
    remaining = get_api_calls_remaining()
    next_call_time = get_next_api_call_time()
    
    return jsonify({
        'calls_remaining': remaining,
        'next_available_call': next_call_time.isoformat() if next_call_time else None,
        'can_make_call': remaining > 0
    })

@app.route('/games')
def games():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    initialize_app()
    
    # Use smart NFL week calculation for current week display
    try:
        from nfl_week_calculator import get_current_nfl_week
        current_nfl_week = get_current_nfl_week(2025)
    except Exception as e:
        logger.error(f"Error calculating current week: {e}")
        current_nfl_week = 1  # Fallback
    
    # Get week from URL parameter or use current week
    week = request.args.get('week', current_nfl_week, type=int)
    year = request.args.get('year', 2025, type=int)
    
    # Auto-cleanup obsolete Monday Night Football score predictions
    try:
        from mnf_cleanup_utils import cleanup_obsolete_mnf_predictions
        cleaned_count = cleanup_obsolete_mnf_predictions(DATABASE_PATH, week, year)
        if cleaned_count > 0:
            logger.info(f"Auto-cleaned {cleaned_count} obsolete MNF predictions for Week {week}")
    except Exception as e:
        logger.warning(f"MNF auto-cleanup failed: {e}")
    
    # Get dashboard data for the selected week
    dashboard_data = get_dashboard_data(session['user_id'], week, year)
    
    # Get deadline information for display
    try:
        deadline_manager = DeadlineManager()
        deadline_summary = deadline_manager.get_user_deadline_summary(week, year, session['user_id'])
    except Exception as e:
        logger.error(f"Error getting deadline summary: {e}")
        deadline_summary = None
    
    # DON'T auto-update live scores on every page load to avoid hitting API rate limits
    # Admin can manually trigger updates using the update_scores endpoint
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM nfl_games 
            WHERE week = ? AND year = ? 
            ORDER BY game_date
        ''', (week, year))
        games_raw = cursor.fetchall()
        
        # Find the actual Monday Night Football game (latest game on Monday)
        cursor.execute('''
            SELECT id FROM nfl_games 
            WHERE week = ? AND year = ? 
            AND strftime('%w', game_date) = '1'  -- Monday
            ORDER BY game_date DESC, id DESC
            LIMIT 1
        ''', (week, year))
        
        monday_night_game = cursor.fetchone()
        monday_night_game_id = monday_night_game[0] if monday_night_game else None
        
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
            
            # Add team names to game data for easy access in template
            game_dict['away_team_name'] = get_team_name(game_dict['away_team'])
            game_dict['home_team_name'] = get_team_name(game_dict['home_team'])
            
            # Add team logos
            game_dict['away_team_logo'] = get_team_logo_url(game_dict['away_team'])
            game_dict['home_team_logo'] = get_team_logo_url(game_dict['home_team'])
            
            # Add actual Monday Night Football detection
            game_dict['is_actual_monday_night'] = (game_dict['id'] == monday_night_game_id)
            
            # Add Thursday Night Football detection
            game_dict['is_actual_thursday_night'] = game_dict.get('is_thursday_night', False)
            
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

        # Get all users' picks for games where deadlines have passed
        # This will be used to show everyone's picks after deadlines
        cursor.execute('''
            SELECT g.id, u.username, up.selected_team, up.predicted_home_score, up.predicted_away_score
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            JOIN users u ON up.user_id = u.id
            WHERE g.week = ? AND g.year = ? AND u.is_admin = 0
            ORDER BY u.username
        ''', (week, year))
        
        all_picks = {}
        for row in cursor.fetchall():
            game_id = row[0]
            if game_id not in all_picks:
                all_picks[game_id] = []
            all_picks[game_id].append({
                'username': row[1],
                'selected_team': row[2],
                'predicted_home_score': row[3],
                'predicted_away_score': row[4]
            })
    
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
    
    # Add deadline status for game day visibility
    thursday_deadline_passed = (simple_status.get('thursday', {}).get('passed', False) 
                               if simple_status else False)
    
    # Monday deadline status - same as Sunday deadline
    monday_deadline_passed = (simple_status.get('monday', {}).get('passed', False)
                             if simple_status else False)
    
    for game in games_data:
        # Show Monday Night predictions if it's Monday game and deadline open
        game['show_mnf_predictions'] = (game.get('is_actual_monday_night', False) and
                                       not monday_deadline_passed)
        
    return render_template('games.html',
                         games=games_data,
                         user_picks=user_picks,
                         all_picks=all_picks,
                         current_week=week,
                         current_year=year,
                         current_nfl_week=current_nfl_week,
                         available_weeks=list(range(1, 19)),
                         total_games=len(games_data),
                         deadlines=simple_deadlines,
                         deadline_status=simple_status,
                         deadline_summary=deadline_summary,
                         thursday_deadline_passed=thursday_deadline_passed,
                         # Dashboard data
                         user_picks_count=dashboard_data['user_picks_count'],
                         total_players=dashboard_data['total_players'],
                         user_wins=dashboard_data['user_wins'],
                         username=session.get('username', 'User'),
                         is_admin=session.get('is_admin', False))

@app.route('/submit_picks', methods=['POST'])
def submit_picks():
    if 'user_id' not in session:
        flash('Please log in to submit picks', 'error')
        return redirect(url_for('login'))
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        picks = data.get('picks', [])
    else:
        # Handle form data
        picks = []
        form_data = request.form
        
        # Process form data - each pick is like: game_<game_id> = team_name
        for key, value in form_data.items():
            if key.startswith('game_') and value:
                game_id = key.replace('game_', '')
                pick = {'game_id': game_id, 'selected_team': value}
                
                # Also get score predictions for Monday Night games
                home_score_key = f'home_score_{game_id}'
                away_score_key = f'away_score_{game_id}'
                
                if home_score_key in form_data:
                    pick['home_score'] = form_data[home_score_key]
                if away_score_key in form_data:
                    pick['away_score'] = form_data[away_score_key]
                
                picks.append(pick)
    
    # Check deadlines before allowing submissions
    deadline_manager = DeadlineManager()
    
    with get_db() as conn:
        cursor = conn.cursor()
        successful_picks = 0
        failed_picks = 0
        rejected_games = []
        
        for pick in picks:
            game_id = pick.get('game_id')
            selected_team = pick.get('selected_team')
            home_score = pick.get('home_score')
            away_score = pick.get('away_score')
            
            if game_id and selected_team:
                # Get game info to check deadline
                cursor.execute('SELECT week, year, game_date, away_team, home_team FROM nfl_games WHERE id = ?', (game_id,))
                game_info = cursor.fetchone()
                
                if game_info:
                    week, year, game_date, away_team, home_team = game_info
                    
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
                        rejected_games.append(f"{away_team} @ {home_team}")
                        logger.warning(f"Pick submission after deadline for game {game_id} ({away_team} @ {home_team}) by user {session['user_id']}")
        
        conn.commit()
    
    # Handle responses based on request type
    if request.is_json:
        # JSON response for AJAX requests
        if failed_picks > 0:
            rejected_list = ", ".join(rejected_games)
            return jsonify({
                'success': False, 
                'message': f'Some picks were rejected due to deadline. {successful_picks} picks saved, {failed_picks} rejected: {rejected_list}',
                'partial': True
            })
        return jsonify({'success': True, 'message': f'Successfully submitted {successful_picks} picks!'})
    else:
        # Form submission response with flash messages and redirect
        if failed_picks > 0:
            rejected_list = ", ".join(rejected_games)
            flash(f'Some picks were rejected due to deadline. {successful_picks} picks saved, {failed_picks} rejected: {rejected_list}', 'warning')
        else:
            flash(f'Successfully submitted {successful_picks} picks!', 'success')
        
        return redirect(url_for('games'))
@app.route('/debug_thursday')
def debug_thursday():
    """Debug route to check Thursday pick revelation variables"""
    if not session.get('is_admin'):
        return "Admin access required", 403
    
    week = 2
    year = 2025
    
    try:
        # Get deadline status
        deadline_manager = DeadlineManager()
        deadline_data = deadline_manager.get_week_deadlines(week, year)
        
        simple_status = {}
        for key, value in deadline_data.items():
            if value and isinstance(value, dict) and 'deadline' in value:
                simple_status[key.replace('_night', '').replace('_games', '')] = {
                    'passed': value['status']['is_closed'],
                    'hours_until': value['status']['hours_until_deadline']
                }
        
        thursday_deadline_passed = simple_status.get('thursday', {}).get('passed', False)
        
        # Get games
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, away_team, home_team, is_thursday_night FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            games = cursor.fetchall()
            
            thursday_games = [g for g in games if g[3] == 1]  # is_thursday_night = 1
            
            # Get picks
            cursor.execute('''
                SELECT g.id, u.username, up.selected_team
                FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                JOIN users u ON up.user_id = u.id
                WHERE g.week = ? AND g.year = ? AND g.is_thursday_night = 1
            ''', (week, year))
            
            thursday_picks = cursor.fetchall()
        
        debug_info = {
            'thursday_deadline_passed': thursday_deadline_passed,
            'simple_status': simple_status,
            'thursday_games_count': len(thursday_games),
            'thursday_games': [f"Game {g[0]}: {g[1]} @ {g[2]}" for g in thursday_games],
            'thursday_picks_count': len(thursday_picks),
            'thursday_picks': [f"{p[1]}: {p[2]}" for p in thursday_picks],
            'should_show_revelation': thursday_deadline_passed and len(thursday_games) > 0
        }
        
        return f"<pre>{debug_info}</pre>"
        
    except Exception as e:
        return f"Error: {e}"


@app.route('/register', methods=['GET', 'POST'])
def register():
    # TEMPORARY: Registration disabled for a couple of months
    flash('New user registration is temporarily disabled. Please contact an administrator for account creation.', 'info')
    return redirect(url_for('login'))
    
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
                
                # Check if username already exists (case-insensitive)
                cursor.execute('SELECT username FROM users WHERE LOWER(username) = LOWER(?)', (username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    flash(f'Username already exists as "{existing_user[0]}". Please choose a different one.', 'error')
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
    
    # Calculate leaderboard directly from picks and games (like weekly leaderboard)
    # This ensures it shows current data even if weekly_results isn't populated
    cursor.execute('''
        SELECT u.username,
               COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.week || '-' || wr.year END) as weekly_wins,
               SUM(CASE WHEN p.is_correct = 1 AND g.is_final = 1 THEN 1 ELSE 0 END) as total_games_won,
               COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) as weeks_played,
               COUNT(CASE WHEN g.is_final = 1 THEN 1 END) as total_games_played,
               ROUND(
                   CASE 
                       WHEN COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) > 0
                       THEN CAST(SUM(CASE WHEN p.is_correct = 1 AND g.is_final = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
                            COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END)
                       ELSE 0 
                   END, 1
               ) as avg_games_won_per_week
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        LEFT JOIN weekly_results wr ON u.id = wr.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id, u.username
        HAVING COUNT(CASE WHEN g.is_final = 1 THEN 1 END) > 0 OR COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) > 0
        ORDER BY weekly_wins DESC, total_games_won DESC, avg_games_won_per_week DESC, u.username
    ''')
    
    leaderboard_data = []
    for row in cursor.fetchall():
        leaderboard_data.append({
            'username': row[0],
            'weekly_wins': row[1] or 0,
            'total_games_won': row[2] or 0,
            'weeks_played': row[3] or 0,
            'total_games_played': row[4] or 0,
            'avg_games_won_per_week': row[5] or 0.0,
            # Map to template expected names
            'wins': row[1] or 0,  # weekly wins
            'avg_correct': row[5] or 0.0,  # avg games won per week
            'total_points': row[2] or 0  # total games won (1 point per game)
        })
    
    conn.close()
    return render_template('leaderboard.html', leaderboard=leaderboard_data)

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # First, try to add the favorite_team column if it doesn't exist
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN favorite_team TEXT')
                conn.commit()
                logger.info("Added favorite_team column to users table")
            except Exception:
                # Column probably already exists
                pass
            
            # Get user information including favorite_team
            try:
                cursor.execute('SELECT username, email, full_name, favorite_team FROM users WHERE id = ?', (session['user_id'],))
                user = cursor.fetchone()
            except Exception:
                # If favorite_team column still doesn't exist, get without it
                cursor.execute('SELECT username, email, full_name FROM users WHERE id = ?', (session['user_id'],))
                user_basic = cursor.fetchone()
                user = user_basic + (None,) if user_basic else None
            
            if not user:
                flash('User not found', 'error')
                return redirect(url_for('logout'))
            
            # Convert to dict for easier access
            user_data = {
                'username': user[0],
                'email': user[1],
                'full_name': user[2]
            }
            favorite_team = user[3] if len(user) > 3 else None
            
            return render_template('profile.html', 
                                 user=user_data, 
                                 favorite_team=favorite_team,
                                 nfl_teams=NFL_TEAM_NAMES)
    
    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        flash('Error loading profile', 'error')
        return redirect(url_for('index'))

@app.route('/profile/update', methods=['POST'])
def update_profile():
    """Update user profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Login required'}), 401
    
    try:
        data = request.get_json()
        favorite_team = data.get('favorite_team')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Validate current password if trying to change password
            if new_password:
                if not current_password:
                    return jsonify({'error': 'Current password required to change password'}), 400
                
                cursor.execute('SELECT password_hash FROM users WHERE id = ?', (session['user_id'],))
                user = cursor.fetchone()
                
                if not check_password_hash(user[0], current_password):
                    return jsonify({'error': 'Current password is incorrect'}), 400
                
                if len(new_password) < 6:
                    return jsonify({'error': 'New password must be at least 6 characters long'}), 400
                
                # Update password
                new_password_hash = generate_password_hash(new_password)
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                             (new_password_hash, session['user_id']))
            
            # Update favorite team
            if favorite_team and favorite_team in NFL_TEAM_NAMES:
                try:
                    # First try to add the column if it doesn't exist
                    cursor.execute('ALTER TABLE users ADD COLUMN favorite_team TEXT')
                except Exception:
                    # Column probably already exists
                    pass
                
                # Update favorite team
                cursor.execute('UPDATE users SET favorite_team = ? WHERE id = ?', 
                             (favorite_team, session['user_id']))
            
            conn.commit()
            
            updates = []
            if favorite_team:
                updates.append('favorite team')
            if new_password:
                updates.append('password')
            
            message = f"Successfully updated {' and '.join(updates)}" if updates else "Profile updated"
            
            logger.info(f"User {session['username']} updated profile: {', '.join(updates)}")
            
            return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    # Calculate current NFL week to set as default
    try:
        from nfl_week_calculator import get_current_nfl_week
        current_week = get_current_nfl_week(2025)
    except Exception as e:
        logger.error(f"Error calculating current week: {e}")
        current_week = 1  # Fallback
    
    return render_template('admin.html', 
                         is_admin=session.get('is_admin', False),
                         current_week=current_week,
                         current_year=2025)

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
        
        week_year = None
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get week/year for this pick to trigger scoring update
            cursor.execute('''
                SELECT g.week, g.year FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE p.id = ?
            ''', (pick_id,))
            game_info = cursor.fetchone()
            if game_info:
                week_year = (game_info[0], game_info[1])
            
            cursor.execute('''
                UPDATE user_picks 
                SET selected_team = ?, predicted_away_score = ?, predicted_home_score = ?
                WHERE id = ?
            ''', (selected_team, predicted_away_score, predicted_home_score, pick_id))
            conn.commit()
        
        # Auto-update scoring for this week
        scoring_message = ""
        if week_year:
            try:
                from database_sync import update_pick_correctness
                from scoring_updater import ScoringUpdater
                
                week, year = week_year
                picks_updated = update_pick_correctness(week, year)
                
                updater = ScoringUpdater()
                updater.update_weekly_results(week, year)
                
                # Update season standings by refreshing all completed weeks
                total_weeks_updated = updater.update_all_completed_weeks()
                
                scoring_message = f" (Auto-updated scoring for Week {week}, {year} and season standings)"
                logger.info(f"Auto-updated scoring and season standings for Week {week}, {year} after admin pick update")
                
            except Exception as e:
                logger.error(f"Failed to auto-update scoring after pick update: {e}")
        
        logger.info(f"Admin {session['username']} updated pick {pick_id}{scoring_message}")
        return jsonify({'success': True, 'message': f'Pick updated{scoring_message}'})
        
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
        
        week_year = None
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get week/year for this pick before deleting
            cursor.execute('''
                SELECT g.week, g.year FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE p.id = ?
            ''', (pick_id,))
            game_info = cursor.fetchone()
            if game_info:
                week_year = (game_info[0], game_info[1])
            
            cursor.execute('DELETE FROM user_picks WHERE id = ?', (pick_id,))
            conn.commit()
        
        # Auto-update scoring for this week
        scoring_message = ""
        if week_year:
            try:
                from database_sync import update_pick_correctness
                from scoring_updater import ScoringUpdater
                
                week, year = week_year
                update_pick_correctness(week, year)
                
                updater = ScoringUpdater()
                updater.update_weekly_results(week, year)
                
                # Update season standings by refreshing all completed weeks
                updater.update_all_completed_weeks()
                
                scoring_message = f" (Auto-updated scoring for Week {week}, {year} and season standings)"
                logger.info(f"Auto-updated scoring and season standings for Week {week}, {year} after admin pick deletion")
                
            except Exception as e:
                logger.error(f"Failed to auto-update scoring after pick deletion: {e}")
        
        logger.info(f"Admin {session['username']} deleted pick {pick_id}{scoring_message}")
        return jsonify({'success': True, 'message': f'Pick deleted{scoring_message}'})
        
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
            game_dict = dict(row)
            # Add team names for admin interface
            game_dict['away_team_name'] = get_team_name(game_dict['away_team'])
            game_dict['home_team_name'] = get_team_name(game_dict['home_team'])
            games.append(game_dict)
    
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
            
            # Check if username exists (case-insensitive)
            cursor.execute('SELECT username FROM users WHERE LOWER(username) = LOWER(?)', (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                return jsonify({'error': f'Username already exists as "{existing_user[0]}"'}), 400
            
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
            
            # Check if username already exists for a different user (case-insensitive)
            cursor.execute('SELECT id, username FROM users WHERE LOWER(username) = LOWER(?) AND id != ?', (username, user_id))
            existing_user = cursor.fetchone()
            if existing_user:
                return jsonify({'error': f'Username already exists as "{existing_user[1]}" for another user'}), 400
            
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

@app.route('/admin/update_scoring', methods=['POST'])
def admin_update_scoring():
    """Admin endpoint to manually trigger scoring updates"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        week = data.get('week')
        year = data.get('year', 2025)
        
        if not week:
            return jsonify({'error': 'Week number required'}), 400
        
        # First update pick correctness for this week (this was the missing step!)
        from database_sync import update_pick_correctness
        picks_updated = update_pick_correctness(week, year)
        
        # Then update weekly results
        from scoring_updater import ScoringUpdater
        updater = ScoringUpdater()
        success = updater.update_weekly_results(week, year)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Scoring updated for Week {week}, {year}. Pick correctness updated for {picks_updated} picks.'
            })
        else:
            return jsonify({
                'error': f'Failed to update scoring for Week {week}, {year}'
            }), 500
    
    except Exception as e:
        logger.error(f"Admin scoring update error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    # Log suspicious 404s but don't spam logs for common paths
    path = request.path
    suspicious_paths = ['/.env', '/hudson', '/wp-admin', '.php', '.asp']
    
    if any(sus in path for sus in suspicious_paths):
        logger.warning(f"404 blocked suspicious path: {request.remote_addr} -> {path}")
    else:
        logger.info(f"404 Not Found: {path}")
    
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {error}")
    return render_template('error.html', error="Internal server error"), 500


@app.errorhandler(405)
def method_not_allowed_error(error):
    logger.warning(f"405 Method Not Allowed: {request.method} {request.path} from {request.remote_addr}")
    return jsonify({'error': 'Method not allowed'}), 405


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
        
        # Track weeks/years that need scoring updates
        weeks_to_update = set()
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            successful_picks = 0
            
            for pick in picks:
                game_id = pick.get('game_id')
                selected_team = pick.get('selected_team')
                home_score = pick.get('home_score')
                away_score = pick.get('away_score')
                
                if game_id and selected_team:
                    # Get week/year for this game to trigger scoring update
                    cursor.execute('SELECT week, year FROM nfl_games WHERE id = ?', (game_id,))
                    game_info = cursor.fetchone()
                    if game_info:
                        weeks_to_update.add((game_info[0], game_info[1]))
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_picks 
                        (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, game_id, selected_team, home_score, away_score, datetime.now()))
                    successful_picks += 1
            
            conn.commit()
        
        # Auto-update scoring for affected weeks
        scoring_updates = []
        for week, year in weeks_to_update:
            try:
                from database_sync import update_pick_correctness
                from scoring_updater import ScoringUpdater
                
                # Update pick correctness
                picks_updated = update_pick_correctness(week, year)
                
                # Update weekly results for this specific week
                updater = ScoringUpdater()
                updater.update_weekly_results(week, year)
                
                # Update season standings by refreshing all completed weeks
                # This ensures the overall leaderboard reflects the changes
                total_weeks_updated = updater.update_all_completed_weeks()
                
                scoring_updates.append(f"Week {week}/{year}: {picks_updated} picks updated, season standings refreshed ({total_weeks_updated} weeks)")
                logger.info(f"Auto-updated scoring and season standings for Week {week}, {year} after admin set user picks")
                
            except Exception as e:
                logger.error(f"Failed to auto-update scoring for Week {week}, {year}: {e}")
                scoring_updates.append(f"Week {week}/{year}: Failed to update")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully set {successful_picks} picks for user',
            'picks_set': successful_picks,
            'scoring_updates': scoring_updates
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
        
        # Auto-update scoring for this week after clearing picks
        scoring_message = ""
        try:
            from database_sync import update_pick_correctness
            from scoring_updater import ScoringUpdater
            
            # Update pick correctness for remaining picks
            picks_updated = update_pick_correctness(week, year)
            
            # Update weekly results for this specific week
            updater = ScoringUpdater()
            updater.update_weekly_results(week, year)
            
            # Update season standings by refreshing all completed weeks
            total_weeks_updated = updater.update_all_completed_weeks()
            
            scoring_message = f" Scoring updated: {picks_updated} picks recalculated, season standings refreshed ({total_weeks_updated} weeks)."
            logger.info(f"Auto-updated scoring and season standings for Week {week}, {year} after admin clear user picks")
            
        except Exception as e:
            logger.error(f"Failed to auto-update scoring for Week {week}, {year}: {e}")
            scoring_message = " Warning: Scoring update failed - manual update may be needed."
        
        return jsonify({
            'success': True,
            'message': f'Cleared {picks_cleared} picks for user.{scoring_message}',
            'picks_cleared': picks_cleared
        })
        
    except Exception as e:
        logger.error(f"Admin clear user picks error: {e}")
        return jsonify({'error': str(e)}), 500
        
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
        return jsonify({'error': str(e)}, 500)

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
        picks = []  # Initialize the picks list
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
    
    # Handle query parameters if no path parameters provided
    if week is None:
        week = request.args.get('week', type=int)
    if year is None:
        year = request.args.get('year', type=int)
    
    # Default to current week if still not specified
    if week is None:
        # Use smart NFL week calculation - default to most recent week with completed games
        try:
            conn = get_db_legacy()
            cursor = conn.cursor()
            
            # First, try to find the most recent week with significant completed games (at least 8 games)
            cursor.execute('''
                SELECT week, COUNT(*) as completed_games
                FROM nfl_games 
                WHERE year = 2025 AND is_final = 1
                GROUP BY week
                HAVING completed_games >= 8
                ORDER BY week DESC
                LIMIT 1
            ''')
            recent_completed = cursor.fetchone()
            
            if recent_completed:
                week = recent_completed[0]
                logger.info(f"Weekly leaderboard defaulting to Week {week} (most recent with {recent_completed[1]} completed games)")
            else:
                # Fallback to current NFL week if no completed weeks found
                from nfl_week_calculator import get_current_nfl_week
                week = get_current_nfl_week(2025)
                logger.info(f"Weekly leaderboard defaulting to current Week {week} (no completed weeks found)")
            
            conn.close()
        except Exception as e:
            logger.error(f"Error calculating leaderboard week: {e}")
            # Fallback to calendar calculation
            from datetime import datetime
            current_date = datetime.now()
            season_start = datetime(2025, 9, 5)  # 2025 season start
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
            
            # Get Monday Night pick data for this user (actual MNF game)
            # First, find the actual Monday Night Football game
            cursor.execute('''
                SELECT id FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND strftime('%w', game_date) = '1'  -- Monday
                ORDER BY game_date DESC, id DESC
                LIMIT 1
            ''', (week, year))
            
            monday_night_game = cursor.fetchone()
            monday_night_game_id = monday_night_game[0] if monday_night_game else None
            
            monday_pick = None
            if monday_night_game_id:
                cursor.execute('''
                    SELECT p.predicted_home_score, p.predicted_away_score,
                           g.home_score, g.away_score, g.home_team, g.away_team, g.is_final,
                           p.selected_team
                    FROM user_picks p
                    JOIN nfl_games g ON p.game_id = g.id
                    WHERE p.user_id = ? AND g.id = ?
                    LIMIT 1
                ''', (user_id, monday_night_game_id))
                
                monday_pick = cursor.fetchone()
            
            # Get all picks for this user for this week
            cursor.execute('''
                SELECT p.selected_team, p.predicted_home_score, p.predicted_away_score,
                       g.home_team, g.away_team, g.home_score, g.away_score, 
                       g.is_final, p.is_correct, g.game_date
                FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE p.user_id = ? AND g.week = ? AND g.year = ?
                ORDER BY g.game_date
            ''', (user_id, week, year))
            
            all_picks = cursor.fetchall()
            
            # Calculate Monday Night tiebreaker data
            monday_tiebreaker = {
                'has_pick': False, 
                'correct_winner': False,
                'home_diff': 999,
                'away_diff': 999,
                'total_diff': 999
            }
            if monday_pick:
                pred_home = monday_pick[0] or 0
                pred_away = monday_pick[1] or 0
                actual_home = monday_pick[2] or 0
                actual_away = monday_pick[3] or 0
                home_team = monday_pick[4] or ''
                away_team = monday_pick[5] or ''
                is_final = monday_pick[6] or False
                selected_team = monday_pick[7] if len(monday_pick) > 7 else None
                
                # Check if user predicted correct winner based on selected_team
                if selected_team and is_final and actual_home is not None and actual_away is not None:
                    actual_winner = away_team if actual_away > actual_home else home_team
                    correct_winner = selected_team == actual_winner
                else:
                    correct_winner = False
                
                monday_tiebreaker = {
                    'has_pick': True,
                    'correct_winner': correct_winner,
                    'home_diff': abs(pred_home - actual_home) if is_final and actual_home is not None else 999,
                    'away_diff': abs(pred_away - actual_away) if is_final and actual_away is not None else 999,
                    'total_diff': abs((pred_home + pred_away) - (actual_home + actual_away)) if is_final and actual_home is not None and actual_away is not None else 999,
                    'home_team': home_team,
                    'away_team': away_team,
                    'predicted_home': pred_home,
                    'predicted_away': pred_away,
                    'actual_home': actual_home,
                    'actual_away': actual_away,
                    'selected_team': selected_team,
                    'is_final': is_final
                }
            
            # Format all picks for display
            picks_detail = []
            for pick in all_picks:
                selected_team, pred_home, pred_away, home_team, away_team, actual_home, actual_away, is_final, is_correct, game_date = pick
                
                # Parse game_date string to datetime object if needed
                parsed_game_date = parse_game_date(game_date)
                
                pick_detail = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'selected_team': selected_team,
                    'predicted_home': pred_home or 0,
                    'predicted_away': pred_away or 0,
                    'actual_home': actual_home,
                    'actual_away': actual_away,
                    'is_final': is_final,
                    'is_correct': is_correct,
                    'game_date': parsed_game_date
                }
                picks_detail.append(pick_detail)
            
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
                'picks_detail': picks_detail,  # Add detailed picks
                'is_winner': i == 1
            })
        
        # Re-sort with Monday Night tiebreaker logic if there are ties
        # Simplified: 1 point per win, then Monday Night tiebreakers
        leaderboard_data.sort(key=lambda x: (
            -x['correct_picks'],                               # Most games won (1 point each)
            not x['monday_tiebreaker'].get('correct_winner', False),  # Correct winner first
            x['monday_tiebreaker'].get('home_diff', 999),      # Closest to home team
            x['monday_tiebreaker'].get('away_diff', 999),      # Closest to away team
            x['monday_tiebreaker'].get('total_diff', 999),     # Closest to total
            x['username']                                      # Alphabetical as final tiebreaker
        ))
        
        # Update ranks after sorting
        for i, user in enumerate(leaderboard_data, 1):
            user['rank'] = i
            # Only mark as winner if:
            # 1. They have more correct picks than others, OR
            # 2. Monday Night game is final and they're ranked first
            if i == 1:
                # Check if this user is actually ahead or tied
                if len(leaderboard_data) > 1:
                    second_place_score = leaderboard_data[1]['correct_picks']
                    user_score = user['correct_picks']
                    
                    # Check if Monday Night game is final
                    mnf_is_final = user['monday_tiebreaker'].get('is_final', False)
                    
                    # Only mark as winner if clearly ahead OR MNF is final and properly sorted
                    user['is_winner'] = (user_score > second_place_score) or mnf_is_final
                else:
                    # Only one user, they win
                    user['is_winner'] = True
            else:
                user['is_winner'] = False
        
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
        
        # Get predictable winner analysis for Monday Night
        try:
            winner_prediction = get_winner_prediction_summary(week, year)
            winner_analysis = analyze_predictable_winners(week, year)
        except Exception as e:
            logger.error(f"Error getting winner prediction: {e}")
            winner_prediction = None
            winner_analysis = None
        
        # Check deadline statuses for pick revelations
        thursday_deadline_passed = False
        friday_deadline_passed = False
        saturday_deadline_passed = False
        sunday_deadline_passed = False
        
        try:
            from deadline_manager import DeadlineManager
            deadline_manager = DeadlineManager()
            deadline_data = deadline_manager.get_week_deadlines(week, year)
            
            # Thursday deadline
            thursday_data = deadline_data.get('thursday_night')
            if thursday_data and isinstance(thursday_data, dict):
                thursday_status = thursday_data.get('status', {})
                thursday_deadline_passed = thursday_status.get('is_closed', False)
            
            # Friday deadline
            friday_data = deadline_data.get('friday_games')
            if friday_data and isinstance(friday_data, list):
                friday_deadline_passed = any(game.get('status', {}).get('is_closed', False) for game in friday_data)
            
            # Saturday deadline  
            saturday_data = deadline_data.get('saturday_games')
            if saturday_data and isinstance(saturday_data, list):
                saturday_deadline_passed = any(game.get('status', {}).get('is_closed', False) for game in saturday_data)
            
            # Sunday deadline
            sunday_data = deadline_data.get('sunday_games', {})
            if sunday_data and isinstance(sunday_data, dict):
                sunday_status = sunday_data.get('status', {})
                sunday_deadline_passed = sunday_status.get('is_closed', False)
                
        except Exception as e:
            logger.error(f"Error checking deadlines: {e}")
        
        # Check if week is completed (all games final)
        week_completed = False
        try:
            conn = get_db_legacy()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as completed_games
                FROM nfl_games 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            game_counts = cursor.fetchone()
            if game_counts and game_counts[0] > 0:
                week_completed = game_counts[0] == game_counts[1]
            conn.close()
        except Exception as e:
            logger.error(f"Error checking week completion: {e}")
        
        # Get all picks data with game results for CSV-style display
        all_picks = []
        picks_by_game = {}
        try:
            conn = get_db_legacy()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT g.id, u.username, up.selected_team, up.predicted_home_score, up.predicted_away_score,
                       up.is_correct, g.away_team, g.home_team, g.home_score, g.away_score, g.is_final,
                       g.is_monday_night
                FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                JOIN users u ON up.user_id = u.id
                WHERE g.week = ? AND g.year = ? AND u.is_admin = 0
                ORDER BY g.game_date, u.username
            ''', (week, year))
            
            for row in cursor.fetchall():
                pick_data = {
                    'game_id': row[0],
                    'username': row[1],
                    'selected_team': row[2],
                    'predicted_home_score': row[3],
                    'predicted_away_score': row[4],
                    'is_correct': row[5],
                    'away_team': row[6],
                    'home_team': row[7],
                    'home_score': row[8],
                    'away_score': row[9],
                    'is_final': row[10],
                    'is_monday_night': row[11]
                }
                all_picks.append(pick_data)
                
                # Group picks by game for CSV-style display
                if row[0] not in picks_by_game:
                    picks_by_game[row[0]] = {
                        'game_id': row[0],
                        'away_team': row[6],
                        'home_team': row[7],
                        'home_score': row[8],
                        'away_score': row[9],
                        'is_final': row[10],
                        'is_monday_night': row[11],
                        'picks': []
                    }
                picks_by_game[row[0]]['picks'].append(pick_data)
            conn.close()
        except Exception as e:
            logger.error(f"Error getting all picks data: {e}")
        
        # Get games data for Thursday revelation
        games = []
        try:
            conn = get_db_legacy()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, away_team, home_team, game_date, is_thursday_night, is_final
                FROM nfl_games 
                WHERE week = ? AND year = ?
                ORDER BY game_date, id
            ''', (week, year))
            
            for row in cursor.fetchall():
                # Parse game_date string to datetime object
                game_date = parse_game_date(row[3])
                
                games.append({
                    'id': row[0],
                    'away_team': row[1],
                    'home_team': row[2],
                    'game_date': game_date,
                    'is_thursday_night': bool(row[4]),
                    'is_final': bool(row[5])
                })
            conn.close()
        except Exception as e:
            logger.error(f"Error getting games data: {e}")

        return render_template('weekly_leaderboard.html',
                                 leaderboard=leaderboard_data,
                                 current_week=week,
                                 current_year=year,
                                 available_weeks=available_weeks,
                                 winner_prediction=winner_prediction,
                                 winner_analysis=winner_analysis,
                                 sunday_deadline_passed=sunday_deadline_passed,
                                 thursday_deadline_passed=thursday_deadline_passed,
                                 friday_deadline_passed=friday_deadline_passed,
                                 saturday_deadline_passed=saturday_deadline_passed,
                                 week_completed=week_completed,
                                 all_picks=all_picks,
                                 picks_by_game=picks_by_game,
                                 games=games)
    
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
        
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE is_final =  1')
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

@app.route('/export_my_picks_csv')
def export_my_picks_csv():
    """Export current user's picks for a specific week as CSV - Beautiful Format"""
    if 'user_id' not in session:
        return jsonify({'error': 'Login required'}), 401
    
    # Check if user wants display format instead of download
    display_format = request.args.get('display_format', '').lower() == 'true'
    
    try:
        week = request.args.get('week', type=int)
        year = request.args.get('year', type=int)
        
        # If no week/year specified, use current week
        if not week or not year:
            # Use smart NFL week calculation
            try:
                from nfl_week_calculator import get_current_nfl_week
                week = get_current_nfl_week(2025)
                year = 2025
            except Exception as e:
                logger.error(f"Error calculating current week: {e}")
                from datetime import datetime
                now = datetime.now()
                week = 1  # Default fallback
                year = now.year
        
        user_id = session['user_id']
        username = session['username']
        
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
            
            # Get user's picks for this week
            cursor.execute('''
                SELECT up.game_id, up.selected_team, 
                       up.predicted_home_score, up.predicted_away_score
                FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE up.user_id = ? AND g.week = ? AND g.year = ?
            ''', (user_id, week, year))
            
            user_picks = {}
            for row in cursor.fetchall():
                user_picks[row['game_id']] = {
                    'selected_team': row['selected_team'],
                    'predicted_home_score': row['predicted_home_score'],
                    'predicted_away_score': row['predicted_away_score']
                }
            
            # Find the actual Monday Night Football game (latest game on Monday)
            cursor.execute('''
                SELECT id FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND strftime('%w', game_date) = '1'  -- Monday
                ORDER BY game_date DESC, id DESC
                LIMIT 1
            ''', (week, year))
            
            monday_night_game = cursor.fetchone()
            monday_night_game_id = monday_night_game[0] if monday_night_game else None

            # Create CSV content with beautiful format (similar to admin export)
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header row with user info
            writer.writerow([f'{username} - Week {week}, {year}', 'My Pick', 'Monday Night Score'])
            
            # Subheader row
            writer.writerow(['Game', 'Selected Team', 'Score Prediction'])
            
            # Separate regular games and Monday Night
            regular_games = []
            monday_night_games = []
            
            # Write game picks
            for game in games:
                game_id = game['id']
                is_actual_monday_night = (game_id == monday_night_game_id)
                game_label = f"{game['away_team']} @ {game['home_team']}"
                
                pick_data = user_picks.get(game_id, {})
                selected_team = pick_data.get('selected_team', 'No Pick Made')
                
                if is_actual_monday_night:
                    # For actual Monday Night Football, include score prediction
                    home_score = pick_data.get('predicted_home_score', '')
                    away_score = pick_data.get('predicted_away_score', '')
                    # Format as text to prevent Excel from converting numbers to months
                    score_prediction = f"'{home_score}-{away_score}" if home_score and away_score else ''
                    
                    monday_night_games.append([game_label, selected_team, score_prediction])
                else:
                    regular_games.append([game_label, selected_team, ''])
            
            # Write regular games first
            for game_row in regular_games:
                writer.writerow(game_row)
            
            # Write Monday Night games
            for game_row in monday_night_games:
                writer.writerow(game_row)
            
            # Add summary section
            writer.writerow([])  # Empty row
            writer.writerow(['Summary', '', ''])
            
            # Count picks made
            total_games = len(games)
            picks_made = len([p for p in user_picks.values() if p.get('selected_team')])
            
            writer.writerow([f'Total Games: {total_games}', '', ''])
            writer.writerow([f'Picks Made: {picks_made}', '', ''])
            writer.writerow([f'Completion: {picks_made}/{total_games}', '', ''])
            
            # Monday Night prediction summary (already have the data from above)
            monday_prediction = None
            if monday_night_game_id:
                pick_data = user_picks.get(monday_night_game_id, {})
                home_score = pick_data.get('predicted_home_score', '')
                away_score = pick_data.get('predicted_away_score', '')
                if home_score and away_score:
                    # Format as text to prevent Excel conversion
                    monday_prediction = f"'{home_score}-{away_score}"
            
            if monday_prediction:
                writer.writerow([f'Monday Night Prediction: {monday_prediction}', '', ''])
            
            # Prepare response
            csv_content = output.getvalue()
            output.close()
            
            # Check if user wants display format instead of download
            if display_format:
                # Return HTML page with CSV content for copy-paste
                return render_template('picks_display.html',
                                     username=username,
                                     week=week,
                                     year=year,
                                     csv_content=csv_content,
                                     total_games=total_games,
                                     picks_made=picks_made)
        
        # Default: return downloadable CSV
        response = app.response_class(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={username}_picks_week_{week}_{year}.csv'}
        )
        
        logger.info(f"User {username} exported their picks CSV for Week {week}, {year}")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting user picks CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/my_picks_export')
def my_picks_export():
    """Show export page for user's picks"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get current week for default selection
        from nfl_week_calculator import get_current_nfl_week
        current_week = get_current_nfl_week(2025)
        
        # Get selected week from query params
        selected_week = request.args.get('week', current_week, type=int)
        selected_year = request.args.get('year', 2025, type=int)
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get available weeks
            cursor.execute('''
                SELECT DISTINCT week, year FROM nfl_games 
                ORDER BY year DESC, week DESC
            ''')
            available_weeks = cursor.fetchall()
            
            # Get user's picks for selected week if specified
            user_picks_data = None
            games_data = None
            total_games = 0
            picks_made = 0
            
            if selected_week and selected_year:
                # Get all games for the selected week
                cursor.execute('''
                    SELECT id, away_team, home_team, game_date, is_monday_night
                    FROM nfl_games 
                    WHERE week = ? AND year = ?
                    ORDER BY game_date
                ''', (selected_week, selected_year))
                
                games_data = [dict(row) for row in cursor.fetchall()]
                total_games = len(games_data)
                
                if games_data:
                    # Get user's picks for this week
                    cursor.execute('''
                        SELECT up.game_id, up.selected_team, 
                               up.predicted_home_score, up.predicted_away_score
                        FROM user_picks up
                        JOIN nfl_games g ON up.game_id = g.id
                        WHERE up.user_id = ? AND g.week = ? AND g.year = ?
                    ''', (session['user_id'], selected_week, selected_year))
                    
                    user_picks = {}
                    for row in cursor.fetchall():
                        user_picks[row['game_id']] = {
                            'selected_team': row['selected_team'],
                            'predicted_home_score': row['predicted_home_score'],
                            'predicted_away_score': row['predicted_away_score']
                        }
                    
                    # Find Monday Night game
                    cursor.execute('''
                        SELECT id FROM nfl_games 
                        WHERE week = ? AND year = ? 
                        AND strftime('%w', game_date) = '1'
                        ORDER BY game_date DESC, id DESC
                        LIMIT 1
                    ''', (selected_week, selected_year))
                    
                    monday_night_game = cursor.fetchone()
                    monday_night_game_id = monday_night_game[0] if monday_night_game else None
                    
                    # Build picks display data
                    picks_display = []
                    for game in games_data:
                        game_id = game['id']
                        pick_data = user_picks.get(game_id, {})
                        selected_team = pick_data.get('selected_team', 'No Pick Made')
                        
                        is_monday_night = (game_id == monday_night_game_id)
                        home_score = pick_data.get('predicted_home_score', '') if is_monday_night else ''
                        away_score = pick_data.get('predicted_away_score', '') if is_monday_night else ''
                        
                        picks_display.append({
                            'game_label': f"{game['away_team']} @ {game['home_team']}",
                            'away_team': game['away_team'],
                            'home_team': game['home_team'],
                            'selected_team': selected_team,
                            'has_pick': selected_team != 'No Pick Made',
                            'is_monday_night': is_monday_night,
                            'predicted_home_score': home_score,
                            'predicted_away_score': away_score,
                            'game_id': game_id
                        })
                    
                    user_picks_data = picks_display
                    picks_made = len([p for p in picks_display if p['has_pick']])
        
        return render_template('my_picks_export.html', 
                               username=session['username'],
                               available_weeks=available_weeks,
                               current_week=current_week,
                               selected_week=selected_week,
                               selected_year=selected_year,
                               user_picks_data=user_picks_data,
                               total_games=total_games,
                               picks_made=picks_made)
                               
    except Exception as e:
        logger.error(f"Error loading export page: {e}")
        flash('Error loading export page', 'error')
        return redirect(url_for('index'))

@app.route('/admin/reset_password', methods=['POST'])
def admin_reset_password():
    """Admin endpoint to reset a user's password without modifying other fields"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        new_password = data.get('new_password')
        
        if not user_id or not new_password:
            return jsonify({'error': 'User ID and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify user exists
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Update only the password
            password_hash = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
            conn.commit()
            
            logger.info(f"Admin {session['username']} reset password for user: {user[0]}")
        
        return jsonify({'success': True, 'message': 'Password reset successfully'})
        
    except Exception as e:
        logger.error(f"Admin password reset error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/import_weekly_picks', methods=['POST'])
def import_weekly_picks():
    """Import picks from CSV with username headers format"""
    if 'user_id' not in session:
        return jsonify({'error': 'Login required'}), 401
    
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        content = file.read().decode('utf-8')
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return jsonify({'error': 'Invalid CSV format - need at least header and one data row'}), 400
        
        # Parse header row (usernames)
        usernames = [name.strip() for name in lines[0].split(',') if name.strip()]
        
        if not usernames:
            return jsonify({'error': 'No usernames found in header row'}), 400
        
        imported_count = 0
        error_messages = []
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get user IDs for usernames (case-insensitive)
            user_map = {}
            for username in usernames:
                cursor.execute('SELECT id, username FROM users WHERE LOWER(username) = LOWER(?)', (username,))
                user_data = cursor.fetchone()
                if user_data:
                    user_map[username] = {'id': user_data[0], 'actual_name': user_data[1]}
                else:
                    error_messages.append(f"User '{username}' not found")
            
            # Process each data row (picks for games)
            for row_num, line in enumerate(lines[1:], 2):
                picks = [pick.strip() for pick in line.split(',')]
                
                if len(picks) != len(usernames):
                    error_messages.append(f"Row {row_num}: Expected {len(usernames)} picks, got {len(picks)}")
                    continue
                
                # Try to find the game for this row
                # For now, assume rows correspond to games in chronological order
                cursor.execute('''
                    SELECT id, home_team, away_team, week, year 
                    FROM nfl_games 
                    ORDER BY game_date, id 
                    LIMIT 1 OFFSET ?
                ''', (row_num - 2,))
                game = cursor.fetchone()
                
                if not game:
                    error_messages.append(f"Row {row_num}: No game found for this row")
                    continue
                
                game_id, home_team, away_team, week, year = game
                
                # Process each pick in this row
                for username, pick in zip(usernames, picks):
                    if username not in user_map or not pick:
                        continue
                    
                    user_id = user_map[username]['id']
                    
                    # Validate pick is either home or away team
                    if pick.upper() not in [home_team.upper(), away_team.upper()]:
                        error_messages.append(f"Row {row_num}: Invalid pick '{pick}' for user '{username}' (game: {away_team} @ {home_team})")
                        continue
                    
                    # Insert or update pick
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_picks (user_id, game_id, selected_team, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, game_id, pick, datetime.now()))
                    
                    imported_count += 1
            
            conn.commit()
        
        result = {
            'success': True,
            'message': f'Successfully imported {imported_count} picks',
            'imported_count': imported_count
        }
        
        if error_messages:
            result['warnings'] = error_messages[:10]  # Limit to first 10 errors
            if len(error_messages) > 10:
                result['warnings'].append(f"... and {len(error_messages) - 10} more errors")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        return jsonify({'error': f'Import failed: {str(e)}'}), 500

@app.route('/export_weekly_dashboard_pdf')
def export_weekly_dashboard_pdf():
    """Export weekly dashboard as PDF"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    try:
        week = request.args.get('week', 1, type=int)
        year = request.args.get('year', 2025, type=int)
        
        # Validate parameters
        if not (1 <= week <= 18):
            flash('Invalid week number. Must be between 1 and 18.', 'error')
            return redirect(url_for('admin'))
        
        if not (2020 <= year <= 2030):
            flash('Invalid year. Must be between 2020 and 2030.', 'error')
            return redirect(url_for('admin'))
        
        logger.info(f"Generating PDF for Week {week}, {year}")
        
        # Import PDF generator
        from pdf_generator import generate_weekly_dashboard_pdf
        
        # Generate PDF
        pdf_bytes = generate_weekly_dashboard_pdf(week, year, DATABASE_PATH)
        
        if not pdf_bytes:
            logger.error("PDF generation returned empty bytes")
            flash('PDF generation failed: No data generated', 'error')
            return redirect(url_for('admin'))
        
        if len(pdf_bytes) < 100:  # PDF should be at least 100 bytes
            logger.error(f"PDF generation returned insufficient data: {len(pdf_bytes)} bytes")
            flash('PDF generation failed: Insufficient data', 'error')
            return redirect(url_for('admin'))
        
        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        
        # Create response with proper headers
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="weekly_dashboard_week_{week}_{year}.pdf"'
        response.headers['Content-Length'] = str(len(pdf_bytes))
        
        # Add cache control headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        # Add CORS headers if needed
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        
        logger.info(f"Admin {session['username']} exported weekly dashboard PDF for Week {week}, {year}")
        
        return response
        
    except ImportError as e:
        logger.error(f"PDF library import error: {e}")
        flash('PDF generation unavailable: Missing library', 'error')
        return redirect(url_for('admin'))
    except Exception as e:
        logger.error(f"Error generating weekly dashboard PDF: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        flash(f'PDF generation failed: {str(e)}', 'error')
        return redirect(url_for('admin'))

@app.route('/export_all_users_picks_csv')
def export_all_users_picks_csv():
    """Export all users' picks in CSV format with usernames as headers (Fantasy League Format)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    try:
        week = request.args.get('week', 1, type=int)
        year = request.args.get('year', 2025, type=int)
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get all users (excluding admin) ordered by username
            cursor.execute('SELECT id, username FROM users WHERE is_admin = 0 ORDER BY username')
            users = cursor.fetchall()
            
            if not users:
                flash('No users found', 'error')
                return redirect(url_for('admin'))
            
            # Get all games for the week ordered by game_date
            cursor.execute('''
                SELECT id, home_team, away_team, game_date, is_monday_night,
                       home_score, away_score
                FROM nfl_games 
                WHERE week = ? AND year = ? 
                ORDER BY game_date
            ''', (week, year))
            games = cursor.fetchall()
            
            if not games:
                flash(f'No games found for Week {week}, {year}', 'error')
                return redirect(url_for('admin'))
            
            # Create CSV content
            output = StringIO()
            writer = csv.writer(output)
            
            # Header row: Game column + usernames (Fantasy League Format)
            header_row = ['Game']
            for user in users:
                header_row.append(user[1])  # username
            writer.writerow(header_row)
            
            # Find the actual Monday Night Football game (latest game on Monday)
            cursor.execute('''
                SELECT id FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND strftime('%w', game_date) = '1'  -- Monday
                ORDER BY game_date DESC, id DESC
                LIMIT 1
            ''', (week, year))
            
            monday_night_game = cursor.fetchone()
            monday_night_game_id = monday_night_game[0] if monday_night_game else None

            # Data rows: each game's picks (one row per game)
            regular_games = []
            monday_night_games = []
            
            for game in games:
                game_id, home_team, away_team, game_date, is_monday_night, home_score, away_score = game
                
                # Check if this is the actual Monday Night Football game
                is_actual_monday_night = (game_id == monday_night_game_id)
                
                # Create game label
                game_label = f"{away_team} @ {home_team}"
                
                picks_row = [game_label]
                for user in users:
                    user_id = user[0]
                    
                    # Get user's pick for this game
                    cursor.execute('''
                        SELECT selected_team 
                        FROM user_picks 
                        WHERE user_id = ? AND game_id = ?
                    ''', (user_id, game_id))
                    
                    pick = cursor.fetchone()
                    picks_row.append(pick[0] if pick else '')
                
                if is_actual_monday_night:
                    monday_night_games.append(picks_row)
                else:
                    regular_games.append(picks_row)
            
            # Write regular games first
            for picks_row in regular_games:
                writer.writerow(picks_row)
            
            # Write Monday Night games
            for picks_row in monday_night_games:
                writer.writerow(picks_row)
            
            # Add empty row before Monday Night scores
            writer.writerow([''] * (len(users) + 1))
            
            # Add Monday Night total scores row (only for the actual Monday Night Football game)
            monday_scores_header = ['Monday Night Scores']
            
            # Find the actual Monday Night Football game (latest game on Monday)
            cursor.execute('''
                SELECT id FROM nfl_games 
                WHERE week = ? AND year = ? 
                AND strftime('%w', game_date) = '1'  -- Monday (0=Sunday, 1=Monday, etc.)
                ORDER BY game_date DESC, id DESC
                LIMIT 1
            ''', (week, year))
            
            monday_night_game = cursor.fetchone()
            monday_night_game_id = monday_night_game[0] if monday_night_game else None
            
            for user in users:
                user_id = user[0]
                
                if monday_night_game_id:
                    # Get user's Monday Night score prediction for the actual MNF game
                    cursor.execute('''
                        SELECT predicted_home_score, predicted_away_score
                        FROM user_picks 
                        WHERE user_id = ? AND game_id = ?
                    ''', (user_id, monday_night_game_id))
                    
                    scores = cursor.fetchone()
                    if scores and scores[0] is not None and scores[1] is not None:
                        home_score = str(scores[0])  # Ensure it's treated as text
                        away_score = str(scores[1])  # Ensure it's treated as text
                        # Format as text to prevent Excel from converting to months
                        monday_scores_header.append(f"'{home_score}-{away_score}")
                    else:
                        monday_scores_header.append("")
                else:
                    monday_scores_header.append("")
            
            # Write Monday Night scores row
            writer.writerow(monday_scores_header)
            
            # Prepare response with better headers for download reliability
            output.seek(0)
            csv_content = output.getvalue()
            
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=fantasy_league_picks_week_{week}_{year}.csv'
            
            # Add headers to prevent SSL/HTTPS download issues
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Content-Length'] = str(len(csv_content.encode('utf-8')))
            
            # Add CORS headers to prevent mixed content issues
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            # Force download by ensuring proper MIME type
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            return response
            
    except Exception as e:
        logger.error(f"Export all users picks error: {e}")
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('admin'))

@app.route('/weekly_results')
def weekly_results():
    """Display weekly results (redirect to leaderboard for now)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # For now, redirect to leaderboard as they serve similar purpose
    # TODO: Create dedicated weekly results page if needed
    return redirect(url_for('leaderboard'))

@app.route('/admin/background_updater_status')
def admin_background_updater_status():
    """Get status of the background game updater"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        status = get_updater_status()
        return jsonify({
            'success': True,
            'status': status,
            'message': 'Background updater running' if status['running'] else 'Background updater stopped'
        })
    except Exception as e:
        logger.error(f"Error getting background updater status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/control_background_updater', methods=['POST'])
def admin_control_background_updater():
    """Start or stop the background game updater"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        action = data.get('action', '').lower()
        
        if action == 'start':
            start_background_updater()
            logger.info(f"Admin {session.get('username')} started background updater")
            return jsonify({'success': True, 'message': 'Background updater started'})
        elif action == 'stop':
            stop_background_updater()
            logger.info(f"Admin {session.get('username')} stopped background updater")
            return jsonify({'success': True, 'message': 'Background updater stopped'})
        else:
            return jsonify({'success': False, 'error': 'Invalid action. Use "start" or "stop"'})
            
    except Exception as e:
        logger.error(f"Error controlling background updater: {e}")
        return jsonify({'success': False, 'error': str(e)})
        
# NFL Score Updater Integration
@app.route('/admin/update_scores', methods=['POST'])
def admin_update_scores():
    """Admin endpoint to manually trigger score updates"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from score_updater import NFLScoreUpdater
        
        updater = NFLScoreUpdater(DATABASE_PATH)
        results = updater.run_update_cycle()
        
        logger.info(f"Admin {session['username']} triggered manual score update")
        
        return jsonify({
            'success': True,
            'message': f'Score update completed: {results["games_updated"]} games updated',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in manual score update: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/scores_status')
def admin_scores_status():
    """Get current scores status for admin panel"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from score_updater import NFLScoreUpdater
        
        updater = NFLScoreUpdater(DATABASE_PATH)
        summary = updater.get_latest_scores_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting scores status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/auto_update_scores', methods=['POST'])
def admin_auto_update_scores():
    """Enable/disable automatic score updates"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        enable = data.get('enable', False)
        
        if enable:
            # Start automatic score updating (integrate with background updater)
            logger.info(f"Admin {session['username']} enabled automatic score updates")
            message = "Automatic score updates enabled"
        else:
            logger.info(f"Admin {session['username']} disabled automatic score updates")
            message = "Automatic score updates disabled"
        
        return jsonify({
            'success': True,
            'message': message,
            'enabled': enable
        })
        
    except Exception as e:
        logger.error(f"Error toggling auto score updates: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and auto-restart systems"""
    try:
        # Check database connectivity
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users LIMIT 1')
            user_count = cursor.fetchone()[0]
        
        # Check background updater status (if available)
        updater_status = "unknown"
        try:
            from background_updater import get_updater_status
            status = get_updater_status()
            updater_status = "running" if status.get('running') else "stopped"
        except:
            updater_status = "not_available"
        
        # Return health status
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'users_count': user_count,
            'background_updater': updater_status,
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'version': '1.0.0'
        }), 500
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/health/simple')
def simple_health_check():
    """Simple health check that just returns OK"""
    return "OK", 200

# Register shutdown handler to stop background updater
def shutdown_handler():
    """Clean shutdown of background services"""
    try:
        stop_background_updater()
        logger.info("Background updater stopped on shutdown")
    except Exception as e:
        logger.error(f"Error stopping background updater: {e}")

atexit.register(shutdown_handler)

# NFL team name mappings
NFL_TEAM_NAMES = {
    'ARI': 'Arizona Cardinals',
    'ATL': 'Atlanta Falcons', 
    'BAL': 'Baltimore Ravens',
    'BUF': 'Buffalo Bills',
    'CAR': 'Carolina Panthers',
    'CHI': 'Chicago Bears',
    'CIN': 'Cincinnati Bengals',
    'CLE': 'Cleveland Browns',
    'DAL': 'Dallas Cowboys',
    'DEN': 'Denver Broncos',
    'DET': 'Detroit Lions',
    'GB': 'Green Bay Packers',
    'HOU': 'Houston Texans',
    'IND': 'Indianapolis Colts',
    'JAX': 'Jacksonville Jaguars',
    'KC': 'Kansas City Chiefs',
    'LAC': 'Los Angeles Chargers',
    'LAR': 'Los Angeles Rams',
    'LV': 'Las Vegas Raiders',
    'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings',
    'NE': 'New England Patriots',
    'NO': 'New Orleans Saints',
    'NYG': 'New York Giants',
    'NYJ': 'New York Jets',
    'PHI': 'Philadelphia Eagles',
    'PIT': 'Pittsburgh Steelers',
    'SF': 'San Francisco 49ers',
    'SEA': 'Seattle Seahawks',
    'TB': 'Tampa Bay Buccaneers',
    'TEN': 'Tennessee Titans',
    'WAS': 'Washington Commanders'
}

def get_team_name(abbreviation):
    """Get full team name from abbreviation"""
    return NFL_TEAM_NAMES.get(abbreviation, abbreviation)

def get_team_logo_url(abbreviation):
    """Get team logo URL from abbreviation"""
    # ESPN logos are reliable and high quality
    return f"https://a.espncdn.com/i/teamlogos/nfl/500/{abbreviation.lower()}.png"

def get_team_display(abbreviation):
    """Get team display as 'ABB - Full Name'"""
    full_name = NFL_TEAM_NAMES.get(abbreviation, abbreviation)
    return f"{abbreviation} - {full_name}"

# Add team names to template context
@app.context_processor
def inject_team_names():
    return {
        'get_team_name': get_team_name,
        'get_team_logo_url': get_team_logo_url,
        'get_team_display': get_team_display,
        'nfl_team_names': NFL_TEAM_NAMES
    }

if __name__ == '__main__':
    import os
    import ssl
    from werkzeug.serving import make_server
    
    # Initialize the database on startup
    initialize_app()
    
    # Start background game updater (every 15 minutes)
    try:
        start_background_updater()
        logger.info("✅ Background game updater started (updates every 15 minutes)")
    except Exception as e:
        logger.error(f"❌ Failed to start background updater: {e}")
    
    # Simple SSL context setup for existing certificates
    def setup_ssl_context():
        """Setup SSL context using existing certificates"""
        try:
            # Look for standard SSL certificate files in current directory and common paths
            cert_paths = [
                # Current directory
                ('certificate.crt', 'private.key'),
                ('cert.pem', 'key.pem'),
                ('ssl_cert.pem', 'ssl_key.pem'),
                ('fullchain.pem', 'privkey.pem'),  # Let's Encrypt format
                # Common SSL paths
                ('/etc/ssl/certs/certificate.crt', '/etc/ssl/private/private.key'),
                ('/etc/letsencrypt/live/casadetodos.eastus.cloudapp.azure.com/fullchain.pem', 
                 '/etc/letsencrypt/live/casadetodos.eastus.cloudapp.azure.com/privkey.pem'),
            ]
            
            print("🔍 Looking for SSL certificates...")
            for cert_file, key_file in cert_paths:
                print(f"   Checking: {cert_file} & {key_file}")
                if os.path.exists(cert_file) and os.path.exists(key_file):
                    print(f"✅ Found SSL certificates: {cert_file}, {key_file}")
                    logger.info(f"Using SSL certificates: {cert_file}, {key_file}")
                    
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    context.load_cert_chain(cert_file, key_file)
                    print("✅ SSL context created successfully")
                    return context
                else:
                    print(f"❌ Not found: {cert_file} or {key_file}")
            
            print("⚠️ No SSL certificates found. HTTPS will not be available.")
            print("💡 To enable HTTPS, place your SSL files as:")
            print("   - certificate.crt (your SSL certificate)")
            print("   - private.key (your private key)")
            logger.warning("No SSL certificates found. HTTPS will not be available.")
            return None
            
        except Exception as e:
            print(f"❌ SSL setup error: {e}")
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
    
    elif mode == 'http' or mode == 'http-only':
        print("🌐 HTTP-Only Mode")
        print("📍 Access at: http://localhost:8080")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)
        
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
