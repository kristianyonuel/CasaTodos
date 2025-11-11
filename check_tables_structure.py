import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("DATABASE TABLES:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  {table[0]}")

# Check if weekly_results table exists and its structure
print("\nWEEKLY_RESULTS table structure:")
try:
    cursor.execute("PRAGMA table_info(weekly_results)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
except:
    print("  Table doesn't exist")

print("\nSample data from weekly_results:")
try:
    cursor.execute("SELECT * FROM weekly_results LIMIT 3")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")
except:
    print("  No data or table doesn't exist")

conn.close()