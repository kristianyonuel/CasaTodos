#!/usr/bin/env python3
"""
Database Path Fix Script
========================
This script ensures the Flask app uses the correct database file (nfl_fantasy.db).

Problem: Server is looking for 'nfl_games' table in 'database.db' (empty file)
Solution: Rename/copy the correct database file to match what the server expects

Run this on the server to fix the database path issue.
"""

import os
import shutil
import sqlite3
from datetime import datetime

def check_database_contents(db_path):
    """Check if database has nfl_games table and data"""
    if not os.path.exists(db_path):
        return False, "File does not exist"
    
    if os.path.getsize(db_path) == 0:
        return False, "File is empty (0 bytes)"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if nfl_games table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nfl_games'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            conn.close()
            return False, "No nfl_games table found"
        
        # Check if it has Week 4 data
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 4 AND year = 2025")
        week4_count = cursor.fetchone()[0]
        
        # Check completed games
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 4 AND year = 2025 AND is_final = 1")
        completed_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"✅ Valid database: {week4_count} Week 4 games, {completed_count} completed"
        
    except Exception as e:
        return False, f"Database error: {str(e)}"

def main():
    print("🔍 Database Path Fix Tool")
    print("=" * 40)
    
    # Check current database files
    databases = ['database.db', 'nfl_fantasy.db']
    
    for db in databases:
        print(f"\n📁 Checking {db}:")
        if os.path.exists(db):
            size = os.path.getsize(db)
            print(f"   Size: {size:,} bytes")
            
            is_valid, message = check_database_contents(db)
            print(f"   Status: {message}")
        else:
            print(f"   ❌ File not found")
    
    print("\n" + "=" * 40)
    
    # Determine the fix needed
    nfl_fantasy_exists = os.path.exists('nfl_fantasy.db')
    database_exists = os.path.exists('database.db')
    database_empty = database_exists and os.path.getsize('database.db') == 0
    
    if nfl_fantasy_exists and database_empty:
        print("\n🔧 FIX NEEDED:")
        print("   - nfl_fantasy.db has the data")
        print("   - database.db is empty") 
        print("   - Server error suggests it's looking for database.db")
        
        print("\n💡 RECOMMENDED ACTION:")
        print("   Copy nfl_fantasy.db → database.db")
        
        response = input("\n❓ Apply this fix? [y/N]: ").lower().strip()
        
        if response == 'y':
            try:
                # Backup current database.db if it exists
                if os.path.exists('database.db'):
                    backup_name = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy2('database.db', backup_name)
                    print(f"   📋 Backed up database.db → {backup_name}")
                
                # Copy the working database
                shutil.copy2('nfl_fantasy.db', 'database.db')
                print("   ✅ Copied nfl_fantasy.db → database.db")
                
                # Verify the fix
                is_valid, message = check_database_contents('database.db')
                print(f"   🔍 Verification: {message}")
                
                if is_valid:
                    print("\n🎉 SUCCESS! The server should now find completed games.")
                    print("   Try accessing the weekly leaderboard again.")
                else:
                    print("\n❌ Something went wrong. Check the verification message above.")
                    
            except Exception as e:
                print(f"\n❌ ERROR during fix: {str(e)}")
        else:
            print("\n❌ Fix cancelled by user.")
            
    elif nfl_fantasy_exists and not database_exists:
        print("\n🔧 FIX NEEDED:")
        print("   - nfl_fantasy.db has the data")
        print("   - database.db does not exist")
        print("   - Server might be looking for database.db")
        
        print("\n💡 RECOMMENDED ACTION:")
        print("   Copy nfl_fantasy.db → database.db")
        
        response = input("\n❓ Apply this fix? [y/N]: ").lower().strip()
        
        if response == 'y':
            try:
                shutil.copy2('nfl_fantasy.db', 'database.db')
                print("   ✅ Copied nfl_fantasy.db → database.db")
                
                # Verify the fix
                is_valid, message = check_database_contents('database.db')
                print(f"   🔍 Verification: {message}")
                
                if is_valid:
                    print("\n🎉 SUCCESS! The server should now find completed games.")
                else:
                    print("\n❌ Something went wrong. Check the verification message above.")
                    
            except Exception as e:
                print(f"\n❌ ERROR during fix: {str(e)}")
        else:
            print("\n❌ Fix cancelled by user.")
    else:
        print("\n❓ UNCLEAR SITUATION:")
        print("   Manual investigation needed.")
        print("   Check which database file the app.py is actually trying to use.")

if __name__ == '__main__':
    main()