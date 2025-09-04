"""
Complete database setup and initialization for La Casa de Todos NFL Fantasy League
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def create_all_tables():
    """Create all database tables with complete schema"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Drop existing tables if they exist to ensure clean schema
        tables_to_drop = [
            'audit_log', 'league_prizes', 'game_comments', 'notifications', 
            'user_statistics', 'league_settings', 'weekly_results', 'user_picks', 
            'nfl_games', 'nfl_seasons', 'nfl_teams', 'users'
        ]
        
        for table in tables_to_drop:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        
        logger.info("Dropped existing tables for clean rebuild")
        
        # Enable foreign keys and WAL mode for better performance
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute('PRAGMA journal_mode = WAL')
        
        # Users table with enhanced fields
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                phone TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                timezone TEXT DEFAULT 'America/Puerto_Rico',
                notification_preferences TEXT DEFAULT 'all',
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                password_reset_token TEXT,
                password_reset_expires TIMESTAMP
            )
        ''')
        
        # NFL Teams reference table
        cursor.execute('''
            CREATE TABLE nfl_teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                abbreviation TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                city TEXT NOT NULL,
                conference TEXT NOT NULL,
                division TEXT NOT NULL,
                primary_color TEXT,
                secondary_color TEXT,
                logo_url TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # NFL Seasons table
        cursor.execute('''
            CREATE TABLE nfl_seasons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER UNIQUE NOT NULL,
                name TEXT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                playoff_start DATE,
                superbowl_date DATE,
                is_current BOOLEAN DEFAULT FALSE,
                total_weeks INTEGER DEFAULT 18,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced NFL Games table with game_status
        cursor.execute('''
            CREATE TABLE nfl_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_id INTEGER,
                week INTEGER NOT NULL,
                year INTEGER NOT NULL,
                game_id TEXT UNIQUE,
                home_team_id INTEGER,
                away_team_id INTEGER,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                game_date TIMESTAMP NOT NULL,
                stadium TEXT,
                weather_conditions TEXT,
                temperature INTEGER,
                wind_speed INTEGER,
                is_monday_night BOOLEAN DEFAULT FALSE,
                is_thursday_night BOOLEAN DEFAULT FALSE,
                is_sunday_night BOOLEAN DEFAULT FALSE,
                is_playoff BOOLEAN DEFAULT FALSE,
                tv_network TEXT,
                betting_line REAL,
                over_under REAL,
                home_score INTEGER,
                away_score INTEGER,
                quarter INTEGER DEFAULT 0,
                time_remaining TEXT,
                game_status TEXT DEFAULT 'scheduled',
                is_final BOOLEAN DEFAULT FALSE,
                overtime BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (season_id) REFERENCES nfl_seasons(id),
                FOREIGN KEY (home_team_id) REFERENCES nfl_teams(id),
                FOREIGN KEY (away_team_id) REFERENCES nfl_teams(id)
            )
        ''')
        
        # Enhanced User Picks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_picks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game_id INTEGER NOT NULL,
                selected_team TEXT NOT NULL,
                selected_team_id INTEGER,
                predicted_home_score INTEGER,
                predicted_away_score INTEGER,
                confidence_level INTEGER DEFAULT 1,
                pick_notes TEXT,
                is_locked BOOLEAN DEFAULT FALSE,
                lock_reason TEXT,
                is_correct BOOLEAN,
                points_earned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                locked_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (game_id) REFERENCES nfl_games(id) ON DELETE CASCADE,
                FOREIGN KEY (selected_team_id) REFERENCES nfl_teams(id),
                UNIQUE(user_id, game_id)
            )
        ''')
        
        # Weekly Results with detailed scoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                season_id INTEGER,
                week INTEGER NOT NULL,
                year INTEGER NOT NULL,
                correct_picks INTEGER DEFAULT 0,
                total_picks INTEGER DEFAULT 0,
                confidence_points INTEGER DEFAULT 0,
                bonus_points INTEGER DEFAULT 0,
                monday_score_diff INTEGER,
                exact_score_bonus INTEGER DEFAULT 0,
                perfect_week_bonus INTEGER DEFAULT 0,
                is_winner BOOLEAN DEFAULT FALSE,
                weekly_rank INTEGER,
                total_points INTEGER DEFAULT 0,
                prize_amount DECIMAL(10,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (season_id) REFERENCES nfl_seasons(id),
                UNIQUE(user_id, week, year)
            )
        ''')
        
        # League Settings with categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS league_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL DEFAULT 'general',
                setting_name TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                setting_type TEXT DEFAULT 'string',
                display_name TEXT,
                description TEXT,
                is_public BOOLEAN DEFAULT TRUE,
                is_editable BOOLEAN DEFAULT TRUE,
                validation_rule TEXT,
                sort_order INTEGER DEFAULT 0,
                updated_by INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (updated_by) REFERENCES users(id),
                UNIQUE(category, setting_name)
            )
        ''')
        
        # User Statistics and Analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                seasons_played INTEGER DEFAULT 0,
                total_weeks_played INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                best_week_score INTEGER DEFAULT 0,
                worst_week_score INTEGER DEFAULT 0,
                average_score REAL DEFAULT 0.0,
                win_percentage REAL DEFAULT 0.0,
                monday_night_accuracy REAL DEFAULT 0.0,
                confidence_accuracy REAL DEFAULT 0.0,
                exact_score_predictions INTEGER DEFAULT 0,
                perfect_weeks INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                favorite_team TEXT,
                lucky_day TEXT,
                total_prize_money DECIMAL(10,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Notifications system
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT DEFAULT 'info',
                priority TEXT DEFAULT 'normal',
                is_read BOOLEAN DEFAULT FALSE,
                action_url TEXT,
                action_text TEXT,
                image_url TEXT,
                expires_at TIMESTAMP,
                sent_at TIMESTAMP,
                read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Game Comments and Social Features
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                comment_type TEXT DEFAULT 'general',
                is_prediction BOOLEAN DEFAULT FALSE,
                is_trash_talk BOOLEAN DEFAULT FALSE,
                likes_count INTEGER DEFAULT 0,
                is_pinned BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES nfl_games(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # League Prizes and Payouts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS league_prizes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season_id INTEGER,
                prize_type TEXT NOT NULL,
                week INTEGER,
                position INTEGER,
                amount DECIMAL(10,2) NOT NULL,
                winner_id INTEGER,
                description TEXT,
                is_paid BOOLEAN DEFAULT FALSE,
                paid_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (season_id) REFERENCES nfl_seasons(id),
                FOREIGN KEY (winner_id) REFERENCES users(id)
            )
        ''')
        
        # Audit Log for important actions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        logger.info("All database tables created successfully")

def create_indexes():
    """Create database indexes for performance optimization"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_games_week_year ON nfl_games(week, year)',
            'CREATE INDEX IF NOT EXISTS idx_games_date ON nfl_games(game_date)',
            'CREATE INDEX IF NOT EXISTS idx_games_status ON nfl_games(game_status)',
            'CREATE INDEX IF NOT EXISTS idx_picks_user_game ON user_picks(user_id, game_id)',
            'CREATE INDEX IF NOT EXISTS idx_picks_user_week ON user_picks(user_id, game_id, created_at)',
            'CREATE INDEX IF NOT EXISTS idx_results_user_week ON weekly_results(user_id, week, year)',
            'CREATE INDEX IF NOT EXISTS idx_results_week_year ON weekly_results(week, year)',
            'CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read)',
            'CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at)',
            'CREATE INDEX IF NOT EXISTS idx_comments_game ON game_comments(game_id)',
            'CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id, created_at)',
            'CREATE INDEX IF NOT EXISTS idx_user_stats_user ON user_statistics(user_id)'
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        conn.commit()
        logger.info("Database indexes created successfully")

def populate_nfl_teams():
    """Populate NFL teams reference data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if teams already exist
        cursor.execute('SELECT COUNT(*) FROM nfl_teams')
        if cursor.fetchone()[0] > 0:
            logger.info("NFL teams already populated")
            return
        
        nfl_teams_data = [
            ('ARI', 'Arizona Cardinals', 'Arizona', 'NFC', 'West', '#97233F', '#000000'),
            ('ATL', 'Atlanta Falcons', 'Atlanta', 'NFC', 'South', '#A71930', '#000000'),
            ('BAL', 'Baltimore Ravens', 'Baltimore', 'AFC', 'North', '#241773', '#000000'),
            ('BUF', 'Buffalo Bills', 'Buffalo', 'AFC', 'East', '#00338D', '#C60C30'),
            ('CAR', 'Carolina Panthers', 'Carolina', 'NFC', 'South', '#0085CA', '#000000'),
            ('CHI', 'Chicago Bears', 'Chicago', 'NFC', 'North', '#0B162A', '#C83803'),
            ('CIN', 'Cincinnati Bengals', 'Cincinnati', 'AFC', 'North', '#FB4F14', '#000000'),
            ('CLE', 'Cleveland Browns', 'Cleveland', 'AFC', 'North', '#311D00', '#FF3C00'),
            ('DAL', 'Dallas Cowboys', 'Dallas', 'NFC', 'East', '#003594', '#869397'),
            ('DEN', 'Denver Broncos', 'Denver', 'AFC', 'West', '#FB4F14', '#002244'),
            ('DET', 'Detroit Lions', 'Detroit', 'NFC', 'North', '#0076B6', '#B0B7BC'),
            ('GB', 'Green Bay Packers', 'Green Bay', 'NFC', 'North', '#203731', '#FFB612'),
            ('HOU', 'Houston Texans', 'Houston', 'AFC', 'South', '#03202F', '#A71930'),
            ('IND', 'Indianapolis Colts', 'Indianapolis', 'AFC', 'South', '#002C5F', '#A2AAAD'),
            ('JAX', 'Jacksonville Jaguars', 'Jacksonville', 'AFC', 'South', '#006778', '#9F792C'),
            ('KC', 'Kansas City Chiefs', 'Kansas City', 'AFC', 'West', '#E31837', '#FFB81C'),
            ('LV', 'Las Vegas Raiders', 'Las Vegas', 'AFC', 'West', '#000000', '#A5ACAF'),
            ('LAC', 'Los Angeles Chargers', 'Los Angeles', 'AFC', 'West', '#0080C6', '#FFC20E'),
            ('LAR', 'Los Angeles Rams', 'Los Angeles', 'NFC', 'West', '#003594', '#FFA300'),
            ('MIA', 'Miami Dolphins', 'Miami', 'AFC', 'East', '#008E97', '#FC4C02'),
            ('MIN', 'Minnesota Vikings', 'Minnesota', 'NFC', 'North', '#4F2683', '#FFC62F'),
            ('NE', 'New England Patriots', 'New England', 'AFC', 'East', '#002244', '#C60C30'),
            ('NO', 'New Orleans Saints', 'New Orleans', 'NFC', 'South', '#D3BC8D', '#101820'),
            ('NYG', 'New York Giants', 'New York', 'NFC', 'East', '#0B2265', '#A71930'),
            ('NYJ', 'New York Jets', 'New York', 'AFC', 'East', '#125740', '#000000'),
            ('PHI', 'Philadelphia Eagles', 'Philadelphia', 'NFC', 'East', '#004C54', '#A5ACAF'),
            ('PIT', 'Pittsburgh Steelers', 'Pittsburgh', 'AFC', 'North', '#FFB612', '#101820'),
            ('SF', 'San Francisco 49ers', 'San Francisco', 'NFC', 'West', '#AA0000', '#B3995D'),
            ('SEA', 'Seattle Seahawks', 'Seattle', 'NFC', 'West', '#002244', '#69BE28'),
            ('TB', 'Tampa Bay Buccaneers', 'Tampa Bay', 'NFC', 'South', '#D50A0A', '#FF7900'),
            ('TEN', 'Tennessee Titans', 'Tennessee', 'AFC', 'South', '#0C2340', '#4B92DB'),
            ('WAS', 'Washington Commanders', 'Washington', 'NFC', 'East', '#5A1414', '#FFB612')
        ]
        
        for team_data in nfl_teams_data:
            cursor.execute('''
                INSERT INTO nfl_teams (abbreviation, full_name, city, conference, division, primary_color, secondary_color)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', team_data)
        
        conn.commit()
        logger.info(f"Populated {len(nfl_teams_data)} NFL teams")

def create_default_users():
    """Create default admin and sample users"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create admin user
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        if cursor.fetchone()[0] == 0:
            admin_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', admin_hash, 'admin@lacasadetodos.com', 'Administrator', True))
            
            # Create admin statistics
            admin_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO user_statistics (user_id) VALUES (?)
            ''', (admin_id,))
            
            logger.info("Created default admin user")
        
        # Create sample family users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        if cursor.fetchone()[0] == 0:
            family_users = [
                ('dad', 'family123', 'dad@family.com', 'Dad Martinez'),
                ('mom', 'family123', 'mom@family.com', 'Mom Martinez'),
                ('son', 'family123', 'son@family.com', 'Son Martinez'),
                ('daughter', 'family123', 'daughter@family.com', 'Daughter Martinez'),
                ('uncle', 'family123', 'uncle@family.com', 'Uncle Martinez'),
                ('cousin', 'family123', 'cousin@family.com', 'Cousin Martinez')
            ]
            
            for username, password, email, full_name in family_users:
                user_hash = generate_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, full_name, is_admin)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, user_hash, email, full_name, False))
                
                # Create user statistics
                user_id = cursor.lastrowid
                cursor.execute('''
                    INSERT INTO user_statistics (user_id) VALUES (?)
                ''', (user_id,))
            
            logger.info(f"Created {len(family_users)} sample family users")
        
        conn.commit()

def initialize_league_settings():
    """Initialize comprehensive league settings"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        settings_data = [
            # General Settings
            ('general', 'league_name', 'La Casa de Todos NFL League', 'string', 'League Name', 'Name of the fantasy league'),
            ('general', 'current_season', str(datetime.now().year), 'integer', 'Current Season', 'Current NFL season year'),
            ('general', 'timezone', 'America/Puerto_Rico', 'string', 'League Timezone', 'Primary timezone for the league'),
            ('general', 'max_participants', '20', 'integer', 'Max Participants', 'Maximum number of league participants'),
            
            # Financial Settings
            ('financial', 'weekly_fee', '20.00', 'decimal', 'Weekly Fee', 'Weekly pool entry fee'),
            ('financial', 'season_fee', '20.00', 'decimal', 'Initial Fee', 'One-time joining fee'),
            ('financial', 'weekly_prize', '400.00', 'decimal', 'Weekly Prize', 'Weekly winner prize amount'),
            ('financial', 'season_prize', '500.00', 'decimal', 'Season Prize', 'Season winner prize amount'),
            
            # Game Rules
            ('rules', 'confidence_scoring', 'true', 'boolean', 'Confidence Scoring', 'Enable confidence point scoring'),
            ('rules', 'monday_night_tiebreaker', 'true', 'boolean', 'Monday Night Tiebreaker', 'Use Monday Night for tiebreaking'),
            ('rules', 'allow_tie_predictions', 'false', 'boolean', 'Allow Tie Predictions', 'Allow users to predict tie games'),
            ('rules', 'perfect_week_bonus', '10', 'integer', 'Perfect Week Bonus', 'Bonus points for perfect week'),
            ('rules', 'exact_score_bonus', '5', 'integer', 'Exact Score Bonus', 'Bonus points for exact score prediction'),
            
            # Deadlines
            ('deadlines', 'thursday_deadline_hours', '2', 'integer', 'Thursday Deadline', 'Hours before TNF to submit picks'),
            ('deadlines', 'sunday_deadline_hours', '1', 'integer', 'Sunday Deadline', 'Hours before first Sunday game'),
            ('deadlines', 'elimination_advance_days', '7', 'integer', 'Elimination Advance', 'Days before Saturday for elimination picks'),
            
            # Features
            ('features', 'notifications_enabled', 'true', 'boolean', 'Notifications', 'Enable push notifications'),
            ('features', 'comments_enabled', 'true', 'boolean', 'Comments', 'Allow user comments on games'),
            ('features', 'live_scores', 'true', 'boolean', 'Live Scores', 'Show live game scores'),
            ('features', 'auto_lock_picks', 'true', 'boolean', 'Auto Lock Picks', 'Auto-lock picks at game time'),
            ('features', 'social_features', 'true', 'boolean', 'Social Features', 'Enable social features and trash talk')
        ]
        
        for category, name, value, setting_type, display_name, description in settings_data:
            cursor.execute('SELECT COUNT(*) FROM league_settings WHERE category = ? AND setting_name = ?', (category, name))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO league_settings (category, setting_name, setting_value, setting_type, display_name, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (category, name, value, setting_type, display_name, description))
        
        conn.commit()
        logger.info(f"Initialized {len(settings_data)} league settings")

def create_current_season():
    """Create current NFL season entry"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        current_year = datetime.now().year
        cursor.execute('SELECT COUNT(*) FROM nfl_seasons WHERE year = ?', (current_year,))
        
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO nfl_seasons (year, name, start_date, end_date, is_current)
                VALUES (?, ?, ?, ?, ?)
            ''', (current_year, f'{current_year} NFL Season',
                  f'{current_year}-09-01', f'{current_year+1}-02-28', True))
            
            logger.info(f"Created {current_year} NFL season")
        
        conn.commit()

def create_sample_games(cursor, year):
    """Create sample NFL games for testing with proper game_status"""
    teams = ['KC', 'BUF', 'DAL', 'SF', 'GB', 'NE', 'PIT', 'BAL', 'DEN', 'LAC', 'MIA', 'NYJ']
    
    for week in range(1, 6):  # Create first 5 weeks
        base_date = datetime(year, 9, 5) + timedelta(weeks=week-1)
        
        # Thursday Night Football (except week 1)
        if week > 1:
            thursday_date = base_date + timedelta(days=3)
            cursor.execute('''
                INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_thursday_night, game_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (week, year, f'tnf_{week}_{year}', teams[0], teams[1], 
                  thursday_date.replace(hour=20, minute=15), True, 'scheduled'))
        
        # Sunday games
        sunday = base_date + timedelta(days=6)
        for i in range(2, min(len(teams), 10), 2):
            if i + 1 < len(teams):
                cursor.execute('''
                    INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, game_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (week, year, f'sun_{week}_{year}_{i//2}', teams[i], teams[i+1], 
                      sunday.replace(hour=13), 'scheduled'))
        
        # Monday Night Football
        monday = base_date + timedelta(days=7)
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_monday_night, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (week, year, f'mnf_{week}_{year}', teams[-2], teams[-1], 
              monday.replace(hour=20, minute=15), True, 'scheduled'))

def setup_complete_database():
    """Main function to setup complete database with clean rebuild"""
    logger.info("🚀 Starting complete database rebuild...")
    
    try:
        # Remove existing database file for clean start
        import os
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            logger.info("Removed existing database for clean rebuild")
        
        # Create all tables with proper schema
        create_all_tables()
        
        # Create performance indexes
        create_indexes()
        
        # Populate reference data
        populate_nfl_teams()
        
        # Create default users
        create_default_users()
        
        # Initialize settings
        initialize_league_settings()
        
        # Create current season
        create_current_season()
        
        # Create sample games
        with get_db_connection() as conn:
            cursor = conn.cursor()
            create_sample_games(cursor, datetime.now().year)
            conn.commit()
        
        logger.info("✅ Complete database rebuild finished successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_complete_database()
