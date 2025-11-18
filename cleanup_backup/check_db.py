import sqlite3
import os

if os.path.exists('nfl_fantasy.db'):
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check users table structure
    cursor.execute('PRAGMA table_info(users)')
    columns = cursor.fetchall()
    print('Users table structure:')
    for col in columns:
        print(f'  {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})')
    
    # Check existing users
    cursor.execute('SELECT id, username, email, is_admin FROM users')
    users = cursor.fetchall()
    print(f'\nExisting users ({len(users)}):')
    for user in users:
        print(f'  ID: {user[0]}, Username: "{user[1]}", Email: {user[2]}, Admin: {user[3]}')
    
    conn.close()
else:
    print('Database not found')
