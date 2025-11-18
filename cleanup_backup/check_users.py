#!/usr/bin/env python3
"""
Check user permissions
"""

import sqlite3

def check_users():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()

    print('=== USER PERMISSIONS CHECK ===')
    cursor.execute('SELECT username, is_admin FROM users ORDER BY username')
    users = cursor.fetchall()

    print('All users and their admin status:')
    for username, is_admin in users:
        admin_status = 'ADMIN' if is_admin else 'USER'
        print(f'  {username}: {admin_status}')

    print('\nSpecific check for kristian:')
    cursor.execute('SELECT id, username, is_admin, is_active FROM users WHERE username = "kristian"')
    kristian = cursor.fetchone()
    if kristian:
        user_id, username, is_admin, is_active = kristian
        print(f'  ID: {user_id}')
        print(f'  Username: {username}')
        print(f'  Is Admin: {is_admin}')
        print(f'  Is Active: {is_active}')
    else:
        print('  kristian not found!')

    conn.close()

if __name__ == "__main__":
    check_users()
