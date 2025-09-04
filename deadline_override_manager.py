"""
Admin deadline override functionality
Allows administrators to extend or modify deadlines for specific users or globally
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytz

class DeadlineOverrideManager:
    """Manages admin deadline overrides"""
    
    def __init__(self, db_path: str = 'nfl_fantasy.db'):
        self.db_path = db_path
        self.ast_tz = pytz.timezone('America/Puerto_Rico')
        self._ensure_override_table()
    
    def _ensure_override_table(self):
        """Create deadline override table if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deadline_overrides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    user_id INTEGER NULL,  -- NULL means global override
                    deadline_type TEXT NOT NULL,  -- 'thursday', 'sunday', 'monday'
                    new_deadline TIMESTAMP NOT NULL,
                    reason TEXT,
                    created_by INTEGER NOT NULL,  -- admin user id
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error creating deadline override table: {e}")
    
    def create_override(self, week: int, year: int, deadline_type: str, 
                       new_deadline: datetime, admin_id: int, user_id: Optional[int] = None, 
                       reason: str = "") -> bool:
        """Create a deadline override"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Deactivate existing overrides for same criteria
            cursor.execute('''
                UPDATE deadline_overrides 
                SET is_active = FALSE 
                WHERE week = ? AND year = ? AND deadline_type = ? 
                AND (user_id = ? OR (user_id IS NULL AND ? IS NULL))
                AND is_active = TRUE
            ''', (week, year, deadline_type, user_id, user_id))
            
            # Create new override
            cursor.execute('''
                INSERT INTO deadline_overrides 
                (week, year, user_id, deadline_type, new_deadline, reason, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (week, year, user_id, deadline_type, new_deadline.isoformat(), reason, admin_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error creating deadline override: {e}")
            return False
    
    def get_user_deadline(self, week: int, year: int, deadline_type: str, 
                         user_id: int, default_deadline: datetime) -> datetime:
        """Get effective deadline for a user (considering overrides)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for user-specific override first
            cursor.execute('''
                SELECT new_deadline FROM deadline_overrides
                WHERE week = ? AND year = ? AND deadline_type = ? 
                AND user_id = ? AND is_active = TRUE
                ORDER BY created_at DESC LIMIT 1
            ''', (week, year, deadline_type, user_id))
            
            result = cursor.fetchone()
            if result:
                conn.close()
                return datetime.fromisoformat(result[0])
            
            # Check for global override
            cursor.execute('''
                SELECT new_deadline FROM deadline_overrides
                WHERE week = ? AND year = ? AND deadline_type = ? 
                AND user_id IS NULL AND is_active = TRUE
                ORDER BY created_at DESC LIMIT 1
            ''', (week, year, deadline_type))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return datetime.fromisoformat(result[0])
            
            return default_deadline
            
        except Exception as e:
            print(f"Error getting user deadline: {e}")
            return default_deadline
    
    def get_active_overrides(self, week: int, year: int) -> List[Dict]:
        """Get all active overrides for a week"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT do.*, u.username as affected_user, a.username as created_by_user
                FROM deadline_overrides do
                LEFT JOIN users u ON do.user_id = u.id
                JOIN users a ON do.created_by = a.id
                WHERE do.week = ? AND do.year = ? AND do.is_active = TRUE
                ORDER BY do.created_at DESC
            ''', (week, year))
            
            overrides = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return overrides
            
        except Exception as e:
            print(f"Error getting active overrides: {e}")
            return []
    
    def remove_override(self, override_id: int, admin_id: int) -> bool:
        """Remove/deactivate an override"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE deadline_overrides 
                SET is_active = FALSE 
                WHERE id = ?
            ''', (override_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error removing override: {e}")
            return False
