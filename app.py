from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import logging
from datetime import datetime
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Import existing working modules
from database import init_database
from nfl_schedule import get_current_nfl_week

# Remove imports that don't exist yet
# from config import config, Config  
# from models import DatabaseManager, UserRepository, User
# from services.game_service import GameService
# from services.nfl_service import NFLService

# Temporary config class
class Config:
    SECRET_KEY = 'nfl-fantasy-secret-key-2024'
    DEBUG = True
    CURRENT_SEASON = datetime.now().year
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'nfl_fantasy.log'

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Simple database functions until models are ready
def get_user_by_username(username):
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password_hash, is_admin FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        current_week = get_current_nfl_week()
        current_year = Config.CURRENT_SEASON
        
        template_data = {
            'current_week': current_week,
            'current_year': current_year,
            'username': session.get('username', 'User'),
            'user_picks_count': 0,
            'total_games': 0,
            'user_wins': 0,
            'total_players': 0,
            'available_weeks': list(range(1, 19))
        }
        
        return render_template('index.html', **template_data)
        
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
            
            user = get_user_by_username(username)
            
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['is_admin'] = bool(user[3])
                
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('Login error occurred. Please try again.', 'error')
    
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
    
    # Placeholder until game service is ready
    return render_template('games.html', 
                          games=[], 
                          user_picks={},
                          current_week=1,
                          current_year=2025,
                          available_weeks=list(range(1, 19)),
                          current_nfl_week=1,
                          total_games=0)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return render_template('error.html', error="An unexpected error occurred"), 500

if __name__ == '__main__':
    try:
        print("🚀 Starting La Casa de Todos NFL Fantasy League...")
        init_database()
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        print(f"❌ Startup failed: {e}")
                                 available_weeks=list(range(1, 19)),
                                 current_nfl_week=nfl_service.get_current_nfl_week(),
                                 total_games=len(games_list))
                                 
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
            
            successful_picks = game_service.submit_user_picks(session['user_id'], picks)
            
            return jsonify({
                'success': True,
                'message': f'Successfully submitted {successful_picks} picks!'
            })
            
        except Exception as e:
            logger.error(f"Submit picks error: {e}")
            return jsonify({'error': 'Failed to submit picks'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return render_template('error.html', error="An unexpected error occurred"), 500
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    
    logger.info("Starting La Casa de Todos NFL Fantasy League...")
    logger.info("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/games')
def games():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        # Ensure games exist for this week
        games_count = ensure_games_exist(week, year)
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get games for the week
        cursor.execute('''
            SELECT id, week, year, game_id, home_team, away_team, game_date, 
                   is_monday_night, is_thursday_night, home_score, away_score, is_final
            FROM nfl_games WHERE week = ? AND year = ? 
            ORDER BY 
                CASE 
                    WHEN is_thursday_night = 1 THEN 1
                    WHEN is_monday_night = 1 THEN 3
                    ELSE 2
                END, 
                datetime(game_date)
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
            game_date = None
            if game[6]:
                try:
                    if isinstance(game[6], str):
                        game_date = datetime.datetime.fromisoformat(game[6])
                    else:
                        game_date = game[6]
                except:
                    game_date = datetime.datetime.now()
            
            games_list.append({
                'id': game[0],
                'week': game[1],
                'year': game[2],
                'game_id': game[3],
                'home_team': game[4],
                'away_team': game[5],
                'game_date': game_date,
                'is_monday_night': bool(game[7]),
                'is_thursday_night': bool(game[8]),
                'home_score': game[9],
                'away_score': game[10],
                'is_final': bool(game[11])
            })
        
        available_weeks = get_available_weeks(year) or list(range(1, 19))
        current_nfl_week = get_current_nfl_week()
        
        return render_template('games.html', 
                             games=games_list, 
                             user_picks=user_picks,
                             current_week=week,
                             current_year=year,
                             available_weeks=available_weeks,
                             current_nfl_week=current_nfl_week,
                             total_games=len(games_list))
                             
    except Exception as e:
        print(f"Games page error: {e}")
        flash(f'Error loading games for Week {week}. Please try again.', 'error')
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
        conn.close()
        
        return jsonify({'success': True, 'message': f'Successfully submitted {successful_picks} picks!'})
    
    except Exception as e:
        print(f"Submit picks error: {e}")
        return jsonify({'error': 'Failed to submit picks'}), 500

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/admin/schedule', methods=['GET', 'POST'])
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            year = data.get('year', datetime.datetime.now().year)
            
            # Check if schedule already exists
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE year = ?', (year,))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games > 0:
                return jsonify({'error': f'Games for {year} already exist'}), 400
            
            # Create schedule for the year
            games_added = auto_populate_all_games()
            return jsonify({
                'success': True,
                'message': f'Created schedule for {year}',
                'games_added': games_added
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # GET request - return schedule management page
    return render_template('admin_schedule.html')

@app.route('/admin/create_schedule', methods=['POST'])
def admin_create_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        year = data.get('year')
        
        # Check if schedule already exists
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM nfl_schedule WHERE year = ?', (year,))
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        if existing_count > 0:
            return jsonify({'error': f'Schedule for {year} already exists'}), 400
        
        # Create schedule
        create_default_schedule_in_db(year)
        
        return jsonify({'success': True, 'message': f'Schedule created for {year}'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, is_admin, created_at FROM users ORDER BY username')
    
    users = []
    for row in cursor.fetchall():
        users.append({
            'id': row[0],
            'username': row[1],
            'email': row[2] or '',
            'is_admin': bool(row[3]),
            'created_at': row[4]
        })
    
    conn.close()
    return jsonify(users)

@app.route('/admin/modify_user', methods=['POST'])
def admin_modify_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    is_admin = data.get('is_admin', False)
    new_password = data.get('new_password')
    
    conn = sqlite3.connect('nfl_fantasy.db')
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
