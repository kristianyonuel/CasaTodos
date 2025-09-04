#!/usr/bin/env python3
"""
Database diagnosis script for La Casa de Todos registration issues
"""
from __future__ import annotations

import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'nfl_fantasy.db'

def diagnose_database():
    """Diagnose database issues that might cause registration failures."""
    print("🔍 Diagnosing database for registration issues...")
    print("=" * 60)
    
    # Check if database file exists
    if not os.path.exists(DATABASE_PATH):
        print("❌ Database file does not exist!")
        print("   Run: python setup_database.py")
        return False
    
    print(f"✅ Database file exists: {DATABASE_PATH}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("❌ Users table does not exist!")
            return False
        
        print("✅ Users table exists")
        
        # Check users table schema
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        
        print("\n📋 Users table schema:")
        required_columns = ['id', 'username', 'password_hash', 'email', 'is_admin', 'created_at']
        found_columns = [col[1] for col in columns]
        
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in found_columns]
        if missing_columns:
            print(f"\n❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        
        # Test basic operations
        print("\n🧪 Testing database operations...")
        
        # Test SELECT
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"✅ Current users count: {user_count}")
        
        # Test INSERT (with rollback)
        test_username = f"test_user_{datetime.now().timestamp()}"
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (test_username, 'test_hash', 'test@test.com', False, datetime.now()))
            
            # Check if insert worked
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (test_username,))
            if cursor.fetchone()[0] == 1:
                print("✅ INSERT operation works")
                
                # Rollback the test
                conn.rollback()
                print("✅ Transaction rollback works")
            else:
                print("❌ INSERT operation failed")
                return False
                
        except sqlite3.Error as e:
            print(f"❌ Database operation error: {e}")
            return False
        
        # Check for foreign key constraints
        cursor.execute("PRAGMA foreign_keys;")
        fk_enabled = cursor.fetchone()[0]
        print(f"ℹ️  Foreign keys: {'Enabled' if fk_enabled else 'Disabled'}")
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check;")
        integrity = cursor.fetchone()[0]
        if integrity == 'ok':
            print("✅ Database integrity check passed")
        else:
            print(f"❌ Database integrity issues: {integrity}")
            return False
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database diagnosis completed successfully!")
        print("The database appears to be properly configured for registration.")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def fix_database_permissions():
    """Fix common database permission issues."""
    print("\n🔧 Checking database permissions...")
    
    if os.path.exists(DATABASE_PATH):
        # Check if file is writable
        if os.access(DATABASE_PATH, os.W_OK):
            print("✅ Database file is writable")
        else:
            print("❌ Database file is not writable!")
            print("   Try: chmod 666 nfl_fantasy.db")
            return False
    
    # Check if directory is writable
    if os.access('.', os.W_OK):
        print("✅ Current directory is writable")
    else:
        print("❌ Current directory is not writable!")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = diagnose_database()
        if success:
            fix_database_permissions()
        else:
            print("\n🔧 Suggested fixes:")
            print("1. Run: python setup_database.py")
            print("2. Check file permissions")
            print("3. Ensure SQLite is properly installed")
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
