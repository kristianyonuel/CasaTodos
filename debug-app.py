import sqlite3
import os
from werkzeug.security import check_password_hash

def debug_application():
    print("La Casa de Todos - Application Debug")
    print("=" * 40)
    
    # Check if database exists
    if not os.path.exists('nfl_fantasy.db'):
        print("❌ Database does not exist!")
        print("Run: python create-database.py")
        return
    
    print("✓ Database file exists")
    
    # Check database contents
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check users
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"✓ Users in database: {user_count}")
        
        # List all users
        cursor.execute('SELECT id, username, is_admin FROM users')
        users = cursor.fetchall()
        for user in users:
            print(f"  - ID: {user[0]}, Username: {user[1]}, Admin: {bool(user[2])}")
        
        # Test admin login
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        if admin_user:
            password_valid = check_password_hash(admin_user[0], 'admin123')
            print(f"✓ Admin password test: {'PASS' if password_valid else 'FAIL'}")
        
        # Check games
        cursor.execute('SELECT COUNT(*) FROM nfl_games')
        game_count = cursor.fetchone()[0]
        print(f"✓ Games in database: {game_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Check templates
    template_files = ['index.html', 'login.html', 'games.html']
    for template in template_files:
        template_path = f'templates/{template}'
        if os.path.exists(template_path):
            print(f"✓ Template exists: {template}")
        else:
            print(f"❌ Missing template: {template}")
    
    # Check static files
    static_files = ['style.css']
    for static_file in static_files:
        static_path = f'static/{static_file}'
        if os.path.exists(static_path):
            print(f"✓ Static file exists: {static_file}")
        else:
            print(f"❌ Missing static file: {static_file}")

if __name__ == "__main__":
    debug_application()
