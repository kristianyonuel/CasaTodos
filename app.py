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
        
        # Initialize default values
        user_picks_count = 0
        total_games = get_week_game_count(current_week, current_year)
        user_wins = 0
        total_players = 0
        available_weeks = get_available_weeks(current_year)
        
        # Get database stats safely
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            # Get user's picks for current week
            cursor.execute('''
                SELECT COUNT(*) FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE up.user_id = ? AND g.week = ? AND g.year = ?
            ''', (session['user_id'], current_week, current_year))
            result = cursor.fetchone()
            user_picks_count = result[0] if result else 0
            
            # Get user's total wins
            cursor.execute('''
                SELECT COUNT(*) FROM weekly_results
                WHERE user_id = ? AND is_winner = 1
            ''', (session['user_id'],))
            result = cursor.fetchone()
            user_wins = result[0] if result else 0
            
            # Get total players
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

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

def auto_populate_nfl_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        for week in range(1, 19):
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, year)
                total_games_created += games_created
    
    return total_games_created

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/')
def index():
    return render_template('index.html')

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
            
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

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

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.username, 
                   COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) as wins,
                   AVG(wr.correct_picks) as avg_correct,
                   SUM(wr.points) as total_points
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
        
    except Exception as e:
        print(f"Leaderboard error: {e}")
        flash('Error loading leaderboard', 'error')
        return redirect(url_for('index'))

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
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.username, g.home_team, g.away_team, g.is_monday_night,
               up.selected_team, up.predicted_home_score, up.predicted_away_score, up.id, u.id
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        JOIN nfl_games g ON up.game_id = g.id
        WHERE g.week = ? AND g.year = ?
        ORDER BY u.username, g.game_date
    ''', (week, year))
    
    picks_data = []
    for row in cursor.fetchall():
        picks_data.append({
            'username': row[0],
            'home_team': row[1],
            'away_team': row[2],
            'is_monday_night': bool(row[3]),
            'selected_team': row[4],
            'predicted_home_score': row[5],
            'predicted_away_score': row[6],
            'pick_id': row[7],
            'user_id': row[8]
        })
    
    conn.close()
    return jsonify(picks_data)

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

@app.route('/admin/modify_pick', methods=['POST'])
def admin_modify_pick():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        pick_id = data.get('pick_id')
        selected_team = data.get('selected_team')
        home_score = data.get('home_score')
        away_score = data.get('away_score')
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_picks 
            SET selected_team = ?, predicted_home_score = ?, predicted_away_score = ?
            WHERE id = ?
        ''', (selected_team, home_score, away_score, pick_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Pick updated successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete_pick', methods=['POST'])
def admin_delete_pick():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        pick_id = data.get('pick_id')
        
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_picks WHERE id = ?', (pick_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Pick deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/force_create_games/<int:week>/<int:year>')
def force_create_games(week, year):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('games'))
    
    try:
        games_created = ensure_games_exist(week, year)
        flash(f'Successfully created {games_created} games for Week {week}', 'success')
    except Exception as e:
        flash(f'Error creating games: {str(e)}', 'error')
    
    return redirect(url_for('games', week=week, year=year))

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

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

def auto_populate_nfl_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        for week in range(1, 19):
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, year)
                total_games_created += games_created
    
    return total_games_created

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/')
def index():
    return render_template('index.html')

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
            session['is_admin'] = user[2] == 1
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'is_admin': user[3]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/weekly_results')
def api_weekly_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT correct_picks, total_picks, monday_score_diff, is_winner, points 
        FROM weekly_results 
        WHERE user_id = ? AND year = ? AND week = ?
    ''', (user_id, year, week))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'correct_picks': result[0],
            'total_picks': result[1],
            'monday_score_diff': result[2],
            'is_winner': result[3],
            'points': result[4]
        })
    else:
        return jsonify({'error': 'Results not found'}), 404

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

def auto_populate_nfl_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        for week in range(1, 19):
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, year)
                total_games_created += games_created
    
    return total_games_created

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/')
def index():
    return render_template('index.html')

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
            session['is_admin'] = user[2] == 1
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'is_admin': user[3]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/weekly_results')
def api_weekly_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT correct_picks, total_picks, monday_score_diff, is_winner, points 
        FROM weekly_results 
        WHERE user_id = ? AND year = ? AND week = ?
    ''', (user_id, year, week))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'correct_picks': result[0],
            'total_picks': result[1],
            'monday_score_diff': result[2],
            'is_winner': result[3],
            'points': result[4]
        })
    else:
        return jsonify({'error': 'Results not found'}), 404

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

def auto_populate_nfl_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        for week in range(1, 19):
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, year)
                total_games_created += games_created
    
    return total_games_created

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/')
def index():
    return render_template('index.html')

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
            session['is_admin'] = user[2] == 1
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'is_admin': user[3]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/weekly_results')
def api_weekly_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT correct_picks, total_picks, monday_score_diff, is_winner, points 
        FROM weekly_results 
        WHERE user_id = ? AND year = ? AND week = ?
    ''', (user_id, year, week))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'correct_picks': result[0],
            'total_picks': result[1],
            'monday_score_diff': result[2],
            'is_winner': result[3],
            'points': result[4]
        })
    else:
        return jsonify({'error': 'Results not found'}), 404

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

def auto_populate_nfl_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        for week in range(1, 19):
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, year)
                total_games_created += games_created
    
    return total_games_created

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/')
def index():
    return render_template('index.html')

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
            session['is_admin'] = user[2] == 1
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'is_admin': user[3]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/weekly_results')
def api_weekly_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT correct_picks, total_picks, monday_score_diff, is_winner, points 
        FROM weekly_results 
        WHERE user_id = ? AND year = ? AND week = ?
    ''', (user_id, year, week))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'correct_picks': result[0],
            'total_picks': result[1],
            'monday_score_diff': result[2],
            'is_winner': result[3],
            'points': result[4]
        })
    else:
        return jsonify({'error': 'Results not found'}), 404

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

def auto_populate_nfl_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        for week in range(1, 19):
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, year)
                total_games_created += games_created
    
    return total_games_created

@app.route('/admin/schedule')
def admin_schedule():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, year, week, home_team, away_team, game_time, is_monday_night, is_thursday_night
            FROM nfl_schedule 
            WHERE year = ?
            ORDER BY week, game_time
        ''', (year,))
        
        schedule = []
        for row in cursor.fetchall():
            schedule.append({
                'id': row[0],
                'year': row[1],
                'week': row[2],
                'home_team': row[3],
                'away_team': row[4],
                'game_time': row[5],
                'is_monday_night': bool(row[6]),
                'is_thursday_night': bool(row[7])
            })
        
        conn.close()
        return jsonify(schedule)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/')
def index():
    return render_template('index.html')

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
            session['is_admin'] = user[2] == 1
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin_dashboard.html')

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'is_admin': user[3]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/weekly_results')
def api_weekly_results():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    week = request.args.get('week', datetime.datetime.now().isocalendar()[1], type=int)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT correct_picks, total_picks, monday_score_diff, is_winner, points 
        FROM weekly_results 
        WHERE user_id = ? AND year = ? AND week = ?
    ''', (user_id, year, week))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'correct_picks': result[0],
            'total_picks': result[1],
            'monday_score_diff': result[2],
            'is_winner': result[3],
            'points': result[4]
        })
    else:
        return jsonify({'error': 'Results not found'}), 404

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

def auto_populate_nfl_games():
    """Auto-populate NFL games for 2025-2026 seasons"""
    print("🏈 Auto-populating NFL games for 2025-2026 seasons...")
    
    total_games_created = 0
    for year in [2025, 2026]:
        for week in range(1, 19):
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
            existing_games = cursor.fetchone()[0]
            conn.close()
            
            if existing_games == 0:
                games_created = ensure_games_exist(week, year)
                total_games_created += games_created
    
    return total_games_created
