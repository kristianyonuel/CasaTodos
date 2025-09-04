import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def debug_database():
    """Debug the database and admin user"""
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table does not exist")
            return
        
        print("✓ Users table exists")
        
        # Check all users
        cursor.execute('SELECT id, username, is_admin FROM users')
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Admin: {bool(user[2])}")
        
        # Check admin user specifically
        cursor.execute('SELECT id, username, password_hash, is_admin FROM users WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        
        if admin_user:
            print(f"✓ Admin user found: ID {admin_user[0]}")
            print(f"  Username: {admin_user[1]}")
            print(f"  Is Admin: {bool(admin_user[3])}")
            
            # Test password
            test_password = 'admin123'
            if check_password_hash(admin_user[2], test_password):
                print(f"✓ Password 'admin123' is correct")
            else:
                print(f"❌ Password 'admin123' is incorrect")
        else:
            print("❌ Admin user not found")
            print("Creating admin user...")
            
            admin_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_hash, 'admin@localhost.com', 1))
            conn.commit()
            print("✓ Admin user created")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("La Casa de Todos - Database Debug")
    print("=================================")
    debug_database()
