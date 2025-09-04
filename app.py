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
    """Get current NFL week based on actual NFL calendar"""
    try:
        now = datetime.datetime.now()
        
        # NFL season dates (approximate)
        if now.year <= 2024:
            season_start = datetime.datetime(2024, 9, 5)  # Week 1 typically starts first Thursday of September
            season_end = datetime.datetime(2025, 1, 8)    # Week 18 ends first week of January
        else:
            season_start = datetime.datetime(now.year, 9, 7)
            season_end = datetime.datetime(now.year + 1, 1, 7)
        
        if now < season_start:
            # Pre-season or last year
            return 1
        elif now > season_end:
            # Post-season
            return 18
        else:
            # Calculate week based on days since season start
            days_since_start = (now - season_start).days
            week = min(18, max(1, (days_since_start // 7) + 1))
            return week
            
    except Exception as e:
        print(f"Error calculating NFL week: {e}")
        return 1

def fetch_all_nfl_weeks(year=None):
    """Fetch all 18 weeks of NFL games for the season"""
    if not year:
        year = datetime.datetime.now().year
    
    print(f"Fetching all NFL weeks for {year} season...")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    total_games_added = 0
    
    for week in range(1, 19):  # Weeks 1-18
        print(f"Processing week {week}...")
        
        # Check if we already have games for this week
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, year))
        existing_games = cursor.fetchone()[0]
        
        if existing_games > 0:
            print(f"Week {week} already has {existing_games} games, skipping...")
            continue
        
        try:
            # Fetch from ESPN API
            url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            params = {'seasontype': 2, 'week': week, 'year': year}
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            week_games = 0
            for event in data.get('events', []):
                try:
                    game_date = datetime.datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                    
                    # Determine game type
                    is_monday_night = game_date.weekday() == 0 and game_date.hour >= 20
                    is_thursday_night = game_date.weekday() == 3 and game_date.hour >= 20
                    
                    game_data = {
                        'game_id': event['id'],
                        'week': week,
                        'year': year,
                        'home_team': event['competitions'][0]['competitors'][0]['team']['abbreviation'],
                        'away_team': event['competitions'][0]['competitors'][1]['team']['abbreviation'],
                        'home_team_name': event['competitions'][0]['competitors'][0]['team']['displayName'],
                        'away_team_name': event['competitions'][0]['competitors'][1]['team']['displayName'],
                        'game_date': game_date,
                        'is_monday_night': is_monday_night,
                        'is_thursday_night': is_thursday_night,
                        'is_final': event['status']['type']['completed']
                    }
                    
                    # Add scores if game is final
                    if game_data['is_final']:
                        competitors = event['competitions'][0]['competitors']
                        game_data['home_score'] = int(competitors[0].get('score', 0))
                        game_data['away_score'] = int(competitors[1].get('score', 0))
                    
                    # Insert into database
                    cursor.execute('''
                        INSERT OR REPLACE INTO nfl_games 
                        (game_id, week, year, home_team, away_team, game_date, 
                         is_monday_night, is_thursday_night, home_score, away_score, is_final)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (game_data['game_id'], game_data['week'], game_data['year'], 
                          game_data['home_team'], game_data['away_team'], game_data['game_date'],
                          game_data['is_monday_night'], game_data['is_thursday_night'], 
                          game_data.get('home_score'), game_data.get('away_score'), game_data['is_final']))
                    
                    week_games += 1
                    total_games_added += 1
                    
                except Exception as game_error:
                    print(f"Error processing game in week {week}: {game_error}")
                    continue
            
            print(f"Added {week_games} games for week {week}")
            
            # Small delay to be respectful to the API
            if week < 18:
                import time
                time.sleep(0.5)
                
        except requests.exceptions.RequestException as e:
            print(f"API error for week {week}: {e}")
            # Create sample games if API fails
            sample_games = create_sample_games(week, year)
            for game in sample_games:
                cursor.execute('''
                    INSERT OR REPLACE INTO nfl_games 
                    (game_id, week, year, home_team, away_team, game_date, is_monday_night, is_thursday_night)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (game['game_id'], game['week'], game['year'], game['home_team'], 
                      game['away_team'], game['game_date'], game['is_monday_night'], game['is_thursday_night']))
                total_games_added += len(sample_games)
            
        except Exception as e:
            print(f"Unexpected error for week {week}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"Season sync complete! Added {total_games_added} total games.")
    return total_games_added

def get_available_weeks(year=None):
    """Get list of weeks that have games in the database"""
    if not year:
        year = datetime.datetime.now().year
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT week FROM nfl_games 
        WHERE year = ? 
        ORDER BY week
    ''', (year,))
    
    weeks = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return weeks

@app.route('/')
def index():
    print(f"Index route accessed - Session: {dict(session)}")
    
    if 'user_id' not in session:
        print("No user_id in session, redirecting to login")
        return redirect(url_for('login'))
    
    try:
        current_week = get_current_nfl_week()
        current_year = datetime.datetime.now().year
        
        # Initialize default values
        user_picks_count = 0
        total_games = 0
        user_wins = 0
        total_players = 0
        available_weeks = []
        
        # Try to get database stats safely
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            # Get user's total picks this week (safe query)
            cursor.execute('''
                SELECT COUNT(*) FROM user_picks up
                JOIN nfl_games g ON up.game_id = g.id
                WHERE up.user_id = ? AND g.week = ? AND g.year = ?
            ''', (session['user_id'], current_week, current_year))
            result = cursor.fetchone()
            user_picks_count = result[0] if result else 0
            
            # Get total games this week (safe query)
            cursor.execute('''
                SELECT COUNT(*) FROM nfl_games
                WHERE week = ? AND year = ?
            ''', (current_week, current_year))
            result = cursor.fetchone()
            total_games = result[0] if result else 0
            
            # Get user's total wins (safe query)
            cursor.execute('''
                SELECT COUNT(*) FROM weekly_results
                WHERE user_id = ? AND is_winner = 1
            ''', (session['user_id'],))
            result = cursor.fetchone()
            user_wins = result[0] if result else 0
            
            # Get league stats (safe query)
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
            result = cursor.fetchone()
            total_players = result[0] if result else 0
            
            # Get available weeks (safe query)
            cursor.execute('''
                SELECT DISTINCT week FROM nfl_games 
                WHERE year = ? 
                ORDER BY week
            ''', (current_year,))
            available_weeks = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            print(f"Database queries completed successfully")
            
        except Exception as db_error:
            print(f"Database error (using defaults): {db_error}")
            if 'conn' in locals():
                conn.close()
        
        # Auto-sync NFL games if we have no weeks available
        if len(available_weeks) == 0:
            print("No weeks available, creating sample data...")
            try:
                # Create sample games for current week only
                sample_games = create_sample_games(current_week, current_year)
                conn = sqlite3.connect('nfl_fantasy.db')
                cursor = conn.cursor()
                
                for game in sample_games:
                    cursor.execute('''
                        INSERT OR IGNORE INTO nfl_games 
                        (game_id, week, year, home_team, away_team, game_date, is_monday_night, is_thursday_night)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (game['game_id'], game['week'], game['year'], game['home_team'], 
                          game['away_team'], game['game_date'], game['is_monday_night'], game['is_thursday_night']))
                
                conn.commit()
                conn.close()
                
                available_weeks = [current_week]
                total_games = len(sample_games)
                print(f"Created {len(sample_games)} sample games for week {current_week}")
                
            except Exception as create_error:
                print(f"Error creating sample games: {create_error}")
                available_weeks = [current_week]
        
        template_data = {
            'current_week': current_week, 
            'current_year': current_year,
            'username': session.get('username', 'User'),
            'user_picks_count': user_picks_count,
            'total_games': total_games,
            'user_wins': user_wins,
            'total_players': total_players,
            'available_weeks': available_weeks
        }
        
        print(f"Dashboard data prepared: {template_data}")
        return render_template('index.html', **template_data)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        
        # Return minimal dashboard if all else fails
        return render_template('index.html', 
                             current_week=1, 
                             current_year=2024,
                             username=session.get('username', 'User'),
                             user_picks_count=0,
                             total_games=0,
                             user_wins=0,
                             total_players=0,
                             available_weeks=[1])

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"Login route accessed - Method: {request.method}")
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"Login attempt - Username: {username}")
            
            if not username or not password:
                print("Missing username or password")
                flash('Please enter both username and password', 'error')
                return render_template('login.html')
            
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            
            print(f"User lookup result: {user is not None}")
            
            if user:
                print(f"User found - ID: {user[0]}, Admin: {user[2]}")
                password_check = check_password_hash(user[1], password)
                print(f"Password check result: {password_check}")
                
                if password_check:
                    session['user_id'] = user[0]
                    session['username'] = username
                    session['is_admin'] = bool(user[2])
                    print(f"Login successful - Session set for user: {username}")
                    flash('Successfully logged in!', 'success')
                    return redirect(url_for('index'))
                else:
                    print("Password check failed")
            else:
                print("User not found")
                
            flash('Invalid username or password', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            flash('Login error occurred. Please try again.', 'error')
    
    print("Rendering login template")
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

@app.route('/games')
def games():
    print(f"Games route accessed - Session: {dict(session)}")
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    week = request.args.get('week', get_current_nfl_week(), type=int)
    year = request.args.get('year', datetime.datetime.now().year, type=int)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get games for the week
        cursor.execute('''
            SELECT id, week, year, game_id, home_team, away_team, game_date, 
                   is_monday_night, is_thursday_night, home_score, away_score, is_final
            FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
        ''', (week, year))
        
        db_games = cursor.fetchall()
        
        # If no games found, try to fetch them
        if not db_games:
            print(f"No games found for week {week}, fetching from API...")
            try:
                api_games = fetch_nfl_games(week, year)
                if api_games:
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
                    
                    # Fetch again
                    cursor.execute('''
                        SELECT id, week, year, game_id, home_team, away_team, game_date, 
                               is_monday_night, is_thursday_night, home_score, away_score, is_final
                        FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
                    ''', (week, year))
                    db_games = cursor.fetchall()
            except Exception as fetch_error:
                print(f"Failed to fetch games from API: {fetch_error}")
                # Fall back to sample games
                sample_games = create_sample_games(week, year)
                for game in sample_games:
                    cursor.execute('''
                        INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_monday_night, is_thursday_night)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (game['week'], game['year'], game['game_id'], game['home_team'], 
                          game['away_team'], game['game_date'], game['is_monday_night'], game['is_thursday_night']))
                conn.commit()
                
                cursor.execute('''
                    SELECT id, week, year, game_id, home_team, away_team, game_date, 
                           is_monday_night, is_thursday_night, home_score, away_score, is_final
                    FROM nfl_games WHERE week = ? AND year = ? ORDER BY game_date
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
            games_list.append({
                'id': game[0],
                'week': game[1],
                'year': game[2],
                'game_id': game[3],
                'home_team': game[4],
                'away_team': game[5],
                'game_date': game[6],
                'is_monday_night': bool(game[7]),
                'is_thursday_night': bool(game[8]),
                'home_score': game[9],
                'away_score': game[10],
                'is_final': bool(game[11])
            })
        
        # Get available weeks for navigation
        available_weeks = get_available_weeks(year)
        current_nfl_week = get_current_nfl_week()
        
        print(f"Games page loaded: {len(games_list)} games, {len(user_picks)} user picks")
        
        return render_template('games.html', 
                             games=games_list, 
                             user_picks=user_picks,
                             current_week=week,
                             current_year=year,
                             available_weeks=available_weeks,
                             current_nfl_week=current_nfl_week)
                             
    except Exception as e:
        print(f"Games page error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading games. Please try again.', 'error')
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
        
        for pick in picks:
            game_id = pick.get('game_id')
            selected_team = pick.get('selected_team')
            home_score = pick.get('home_score')
            away_score = pick.get('away_score')
            
            if not game_id or not selected_team:
                continue
                
            # Check if pick already exists
            cursor.execute('''
                SELECT id FROM user_picks WHERE user_id = ? AND game_id = ?
            ''', (session['user_id'], game_id))
            
            existing_pick = cursor.fetchone()
            
            if existing_pick:
                cursor.execute('''
                    UPDATE user_picks 
                    SET selected_team = ?, predicted_home_score = ?, predicted_away_score = ?
                    WHERE id = ?
                ''', (selected_team, home_score, away_score, existing_pick[0]))
            else:
                cursor.execute('''
                    INSERT INTO user_picks 
                    (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session['user_id'], game_id, selected_team, home_score, away_score))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Picks submitted successfully!'})
    
    except Exception as e:
        print(f"Submit picks error: {e}")
        return jsonify({'error': 'Failed to submit picks'}), 500

@app.errorhandler(404)
def not_found_error(error):
    print(f"404 Error: {error}")
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"500 Error: {error}")
    import traceback
    traceback.print_exc()
    return render_template('error.html', error="Internal server error"), 500

@app.route('/sync_season', methods=['POST'])
def sync_season():
    """Manual sync of entire NFL season"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        year = request.json.get('year', datetime.datetime.now().year)
        games_added = fetch_all_nfl_weeks(year)
        return jsonify({
            'success': True, 
            'message': f'Synced {games_added} games for {year} season',
            'games_added': games_added
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Creating database and starting application...")
    
    try:
        init_db()
        print("Database initialized successfully")
        
        # Add debug mode and network configuration
        app.config['DEBUG'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        print("Starting Flask application on all network interfaces...")
        print("Access locally at: http://127.0.0.1:5000")
        print("Access from network at: http://[YOUR-IP]:5000")
        print("To find your IP: ipconfig (Windows) or ip addr (Linux)")
        
        # Run on all network interfaces (0.0.0.0) on port 5000
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    except Exception as e:
        print(f"Application startup failed: {e}")
        import traceback
        traceback.print_exc()
