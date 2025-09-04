from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import logging
from datetime import datetime, timedelta
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager
from setup_database import setup_complete_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nfl_fantasy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'nfl-fantasy-secret-key-2024'

# Database Configuration
DATABASE_PATH = 'nfl_fantasy.db'

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_complete_database():
    """Initialize complete database schema"""
    # Use the comprehensive setup function
    return setup_complete_database()

def create_sample_games(cursor, year):
    """Create sample NFL games for testing"""
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 'MIA', 'NYJ']
    
    for week in range(1, 6):  # Create first 5 weeks
        base_date = datetime(year, 9, 5) + timedelta(weeks=week-1)
        
        # Thursday Night Football (except week 1)
        if week > 1:
            thursday_date = base_date + timedelta(days=3)
            cursor.execute('''
                INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_thursday_night)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (week, year, f'tnf_{week}_{year}', teams[0], teams[1], thursday_date.replace(hour=20, minute=15), True))
        
        # Sunday games
        sunday = base_date + timedelta(days=6)
        for i in range(2, min(len(teams), 10), 2):
            if i + 1 < len(teams):
                cursor.execute('''
                    INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (week, year, f'sun_{week}_{year}_{i//2}', teams[i], teams[i+1], sunday.replace(hour=13)))
        
        # Monday Night Football
        monday = base_date + timedelta(days=7)
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_monday_night)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (week, year, f'mnf_{week}_{year}', teams[-2], teams[-1], monday.replace(hour=20, minute=15), True))

def get_dashboard_data(user_id):
    """Get dashboard data from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get current week and year
        current_year = datetime.now().year
        current_week = 1  # Simplified for now
        
        # Get user's picks count for current week
        cursor.execute('''
            SELECT COUNT(*) FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = ? AND g.year = ?
        ''', (user_id, current_week, current_year))
        user_picks_count = cursor.fetchone()[0]
        
        # Get total games for current week
        cursor.execute('''
            SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?
        ''', (current_week, current_year))
        total_games = cursor.fetchone()[0]
        
        # Get user's total wins
        cursor.execute('''
            SELECT COUNT(*) FROM weekly_results WHERE user_id = ? AND is_winner = 1
        ''', (user_id,))
        user_wins = cursor.fetchone()[0]
        
        # Get total players
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        total_players = cursor.fetchone()[0]
        
        # Get available weeks
        cursor.execute('SELECT DISTINCT week FROM nfl_games WHERE year = ? ORDER BY week', (current_year,))
        available_weeks = [row[0] for row in cursor.fetchall()]
        
        return {
            'current_week': current_week,
            'current_year': current_year,
            'user_picks_count': user_picks_count,
            'total_games': total_games,
            'user_wins': user_wins,
            'total_players': total_players,
            'available_weeks': available_weeks or list(range(1, 19))
        }

def get_games_for_week(week, year):
    """Get games for a specific week from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM nfl_games 
            WHERE week = ? AND year = ? 
            ORDER BY 
                CASE 
                    WHEN is_thursday_night = 1 THEN 1
                    WHEN is_monday_night = 1 THEN 3
                    ELSE 2
                END, 
                datetime(game_date)
        ''', (week, year))
        return cursor.fetchall()

def get_user_picks_for_week(user_id, week, year):
    """Get user's picks for a specific week"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.id, up.selected_team, up.predicted_home_score, up.predicted_away_score
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = ? AND g.year = ?
        ''', (user_id, week, year))
        return {row[0]: {
            'selected_team': row[1],
            'predicted_home_score': row[2],
            'predicted_away_score': row[3]
        } for row in cursor.fetchall()}

@app.before_first_request
def initialize_app():
    """Initialize application on first request"""
    try:
        logger.info("Initializing application with complete database setup...")
        if setup_complete_database():
            logger.info("Application initialized successfully")
        else:
            logger.error("Database setup failed")
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        dashboard_data = get_dashboard_data(session['user_id'])
        dashboard_data['username'] = session.get('username', 'User')
        
        logger.info(f"Dashboard loaded for user: {session.get('username')}")
        return render_template('index.html', **dashboard_data)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
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
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['username'] = username
                session['is_admin'] = bool(user[2])
                
                logger.info(f"User {username} logged in successfully")
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('Login error occurred. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    logger.info(f"User {username} logged out")
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week = request.args.get('week', 1, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    try:
        games_data = get_games_for_week(week, year)
        user_picks = get_user_picks_for_week(session['user_id'], week, year)
        
        return render_template('games.html',
                             games=games_data,
                             user_picks=user_picks,
                             current_week=week,
                             current_year=year,
                             available_weeks=list(range(1, 19)),
                             current_nfl_week=1,
                             total_games=len(games_data))
                             
    except Exception as e:
        logger.error(f"Games page error: {e}")
        flash(f'Error loading games for Week {week}', 'error')
        return redirect(url_for('index'))

@app.route('/submit_picks', methods=['POST'])
def submit_picks():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        picks = data.get('picks', [])
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            successful_picks = 0
            
            for pick in picks:
                game_id = pick.get('game_id')
                selected_team = pick.get('selected_team')
                home_score = pick.get('home_score')
                away_score = pick.get('away_score')
                
                if not game_id or not selected_team:
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_picks 
                    (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session['user_id'], game_id, selected_team, home_score, away_score))
                successful_picks += 1
            
            conn.commit()
        
        logger.info(f"User {session['user_id']} submitted {successful_picks} picks")
        return jsonify({'success': True, 'message': f'Successfully submitted {successful_picks} picks!'})
        
    except Exception as e:
        logger.error(f"Submit picks error: {e}")
        return jsonify({'error': 'Failed to submit picks'}), 500

# ...existing code for other routes...

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return render_template('error.html', error="An unexpected error occurred"), 500

if __name__ == '__main__':
    try:
        logger.info("🚀 Starting La Casa de Todos NFL Fantasy League...")
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

# Make sure this is inside a function, not at the top level!
@app.route('/sync_season', methods=['POST'])
def sync_season():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    try:
        year = request.json.get('year', datetime.datetime.now().year)
        games_added = auto_populate_all_games()
        return jsonify({
            'success': True,
            'message': f'Synced games for {year} season',
            'games_added': games_added
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("🚀 Starting La Casa de Todos NFL Fantasy League...")
    print("=" * 60)
    
    try:
        print("📁 Initializing database...")
        init_database()
        
        print("🏈 Auto-populating NFL games...")
        auto_populate_all_games()
        
        app.config['DEBUG'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        print("=" * 60)
        print("🏈 Application ready!")
        print("Access at: http://127.0.0.1:5000")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Games page error: {e}")
        flash(f'Error loading games for Week {week}', 'error')
        return redirect(url_for('index'))

@app.route('/submit_picks', methods=['POST'])
def submit_picks():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        data = request.get_json()
        picks = data.get('picks', [])
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            successful_picks = 0
            
            for pick in picks:
                game_id = pick.get('game_id')
                selected_team = pick.get('selected_team')
                home_score = pick.get('home_score')
                away_score = pick.get('away_score')
                
                if not game_id or not selected_team:
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_picks 
                    (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session['user_id'], game_id, selected_team, home_score, away_score))
                successful_picks += 1
            
            conn.commit()
        
        logger.info(f"User {session['user_id']} submitted {successful_picks} picks")
        return jsonify({'success': True, 'message': f'Successfully submitted {successful_picks} picks!'})
        
    except Exception as e:
        logger.error(f"Submit picks error: {e}")
        return jsonify({'error': 'Failed to submit picks'}), 500

# ...existing code for other routes...

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return render_template('error.html', error="An unexpected error occurred"), 500

if __name__ == '__main__':
    try:
        logger.info("🚀 Starting La Casa de Todos NFL Fantasy League...")
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

# Make sure this is inside a function, not at the top level!
@app.route('/sync_season', methods=['POST'])
def sync_season():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    try:
        year = request.json.get('year', datetime.datetime.now().year)
        games_added = auto_populate_all_games()
        return jsonify({
            'success': True,
            'message': f'Synced games for {year} season',
            'games_added': games_added
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("🚀 Starting La Casa de Todos NFL Fantasy League...")
    print("=" * 60)
    
    try:
        print("📁 Initializing database...")
        init_database()
        
        print("🏈 Auto-populating NFL games...")
        auto_populate_all_games()
        
        app.config['DEBUG'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        print("=" * 60)
        print("🏈 Application ready!")
        print("Access at: http://127.0.0.1:5000")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
