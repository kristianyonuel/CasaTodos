import sqlite3

# Check user_stats table schema
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check if user_stats table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_stats'")
if cursor.fetchone():
    print("user_stats table exists")
    cursor.execute('PRAGMA table_info(user_stats)')
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")
    
    # Check if favorite_team column exists
    favorite_team_exists = any(col[1] == 'favorite_team' for col in columns)
    if favorite_team_exists:
        print("✅ favorite_team column exists")
    else:
        print("❌ favorite_team column missing")
        print("Adding favorite_team column...")
        cursor.execute('ALTER TABLE user_stats ADD COLUMN favorite_team TEXT')
        print("✅ favorite_team column added")
else:
    print("❌ user_stats table does not exist")

conn.commit()
conn.close()
print("Database check complete")
