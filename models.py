"""
Database models for NFL Fantasy League
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    is_admin: bool = False
    created_at: Optional[datetime] = None
    password_hash: str = ""
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

@dataclass
class NFLGame:
    id: Optional[int] = None
    week: int = 1
    year: int = 2025
    game_id: str = ""
    home_team: str = ""
    away_team: str = ""
    game_date: Optional[datetime] = None
    is_monday_night: bool = False
    is_thursday_night: bool = False
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    is_final: bool = False

@dataclass
class UserPick:
    id: Optional[int] = None
    user_id: int = 0
    game_id: int = 0
    selected_team: str = ""
    predicted_home_score: Optional[int] = None
    predicted_away_score: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class WeeklyResult:
    id: Optional[int] = None
    user_id: int = 0
    week: int = 1
    year: int = 2025
    correct_picks: int = 0
    total_picks: int = 0
    monday_score_diff: Optional[int] = None
    is_winner: bool = False
    points: int = 0

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
    
    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

class UserRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_user(self, user: User) -> int:
        query = '''
            INSERT INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        '''
        return self.db.execute_insert(query, (user.username, user.password_hash, user.email, user.is_admin))
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        query = 'SELECT * FROM users WHERE username = ?'
        rows = self.db.execute_query(query, (username,))
        if rows:
            row = rows[0]
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                is_admin=bool(row['is_admin']),
                created_at=row['created_at'],
                password_hash=row['password_hash']
            )
        return None
    
    def get_all_users(self) -> List[User]:
        query = 'SELECT * FROM users ORDER BY username'
        rows = self.db.execute_query(query)
        return [User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            is_admin=bool(row['is_admin']),
            created_at=row['created_at'],
            password_hash=row['password_hash']
        ) for row in rows]
    
    def update_user(self, user: User) -> bool:
        query = '''
            UPDATE users 
            SET username = ?, email = ?, is_admin = ?, password_hash = ?
            WHERE id = ?
        '''
        rows_affected = self.db.execute_update(query, (
            user.username, user.email, user.is_admin, user.password_hash, user.id
        ))
        return rows_affected > 0

class GameRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_game(self, game: NFLGame) -> int:
        query = '''
            INSERT OR REPLACE INTO nfl_games 
            (game_id, week, year, home_team, away_team, game_date, 
             is_monday_night, is_thursday_night, home_score, away_score, is_final)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.db.execute_insert(query, (
            game.game_id, game.week, game.year, game.home_team, game.away_team,
            game.game_date.isoformat() if game.game_date else None,
            game.is_monday_night, game.is_thursday_night,
            game.home_score, game.away_score, game.is_final
        ))
    
    def get_games_by_week(self, week: int, year: int) -> List[NFLGame]:
        query = '''
            SELECT * FROM nfl_games 
            WHERE week = ? AND year = ? 
            ORDER BY 
                CASE 
                    WHEN is_thursday_night = 1 THEN 1
                    WHEN is_monday_night = 1 THEN 3
                    ELSE 2
                END, 
                datetime(game_date)
        '''
        rows = self.db.execute_query(query, (week, year))
        return [self._row_to_game(row) for row in rows]
    
    def get_available_weeks(self, year: int) -> List[int]:
        query = 'SELECT DISTINCT week FROM nfl_games WHERE year = ? ORDER BY week'
        rows = self.db.execute_query(query, (year,))
        return [row['week'] for row in rows]
    
    def _row_to_game(self, row: sqlite3.Row) -> NFLGame:
        game_date = None
        if row['game_date']:
            try:
                game_date = datetime.fromisoformat(row['game_date'])
            except:
                game_date = datetime.now()
        
        return NFLGame(
            id=row['id'],
            week=row['week'],
            year=row['year'],
            game_id=row['game_id'],
            home_team=row['home_team'],
            away_team=row['away_team'],
            game_date=game_date,
            is_monday_night=bool(row['is_monday_night']),
            is_thursday_night=bool(row['is_thursday_night']),
            home_score=row['home_score'],
            away_score=row['away_score'],
            is_final=bool(row['is_final'])
        )

class PickRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_or_update_pick(self, pick: UserPick) -> int:
        # Check if pick exists
        query = 'SELECT id FROM user_picks WHERE user_id = ? AND game_id = ?'
        rows = self.db.execute_query(query, (pick.user_id, pick.game_id))
        
        if rows:
            # Update existing pick
            update_query = '''
                UPDATE user_picks 
                SET selected_team = ?, predicted_home_score = ?, predicted_away_score = ?
                WHERE user_id = ? AND game_id = ?
            '''
            self.db.execute_update(update_query, (
                pick.selected_team, pick.predicted_home_score, pick.predicted_away_score,
                pick.user_id, pick.game_id
            ))
            return rows[0]['id']
        else:
            # Create new pick
            insert_query = '''
                INSERT INTO user_picks 
                (user_id, game_id, selected_team, predicted_home_score, predicted_away_score)
                VALUES (?, ?, ?, ?, ?)
            '''
            return self.db.execute_insert(insert_query, (
                pick.user_id, pick.game_id, pick.selected_team,
                pick.predicted_home_score, pick.predicted_away_score
            ))
    
    def get_user_picks_for_week(self, user_id: int, week: int, year: int) -> Dict[int, UserPick]:
        query = '''
            SELECT up.*, g.id as game_db_id
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = ? AND g.year = ?
        '''
        rows = self.db.execute_query(query, (user_id, week, year))
        return {row['game_db_id']: UserPick(
            id=row['id'],
            user_id=row['user_id'],
            game_id=row['game_id'],
            selected_team=row['selected_team'],
            predicted_home_score=row['predicted_home_score'],
            predicted_away_score=row['predicted_away_score'],
            created_at=row['created_at']
        ) for row in rows}
