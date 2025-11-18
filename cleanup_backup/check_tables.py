import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("Available tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    print(f"  {t[0]}")

conn.close()
