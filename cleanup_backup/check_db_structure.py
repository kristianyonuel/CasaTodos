import sqlite3

# Connect to database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Check available tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Available tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check if picks or user_picks table exists
for table_name in ['picks', 'user_picks', 'weekly_picks']:
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if columns:
            print(f"\n{table_name} table structure:")
            for col in columns:
                print(f"  {col}")
            
            # Show sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample = cursor.fetchall()
            print(f"\nSample data from {table_name}:")
            for row in sample:
                print(f"  {row}")
    except sqlite3.OperationalError:
        pass

conn.close()