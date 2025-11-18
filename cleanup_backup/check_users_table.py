import sqlite3

# Check users table schema
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(users)')
columns = cursor.fetchall()
print("users table columns:")
for col in columns:
    print(f"  {col[1]} - {col[2]}")

# Check if favorite_team column exists in users table
favorite_team_exists = any(col[1] == 'favorite_team' for col in columns)
if favorite_team_exists:
    print("✅ favorite_team column exists in users table")
else:
    print("❌ favorite_team column missing from users table")
    print("Adding favorite_team column to users table...")
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN favorite_team TEXT')
        print("✅ favorite_team column added to users table")
        conn.commit()
    except Exception as e:
        print(f"Error adding column: {e}")

conn.close()
print("Users table check complete")
