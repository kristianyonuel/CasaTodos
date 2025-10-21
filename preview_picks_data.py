import sqlite3
import sys
import os

# Add the current directory to Python path
sys.path.append(os.getcwd())

try:
    from utils.nfl_week_calculator import get_current_nfl_week
    current_week = get_current_nfl_week()
except ImportError:
    # Fallback - assume current week based on date
    current_week = 6  # Based on October 13, 2025

print(f"Current NFL Week: {current_week}")

# Connect to database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Get games for current week
cursor.execute("""
    SELECT id, home_team, away_team, game_date 
    FROM nfl_games 
    WHERE week = ? AND season = 2025 
    ORDER BY game_date
""", (current_week,))

games = cursor.fetchall()
print(f"\nWeek {current_week} Games:")
for i, game in enumerate(games, 1):
    print(f"Game {i} (ID {game[0]}): {game[2]} @ {game[1]} - {game[3]}")

# Get users
cursor.execute("SELECT id, username FROM users ORDER BY username")
users = cursor.fetchall()
print(f"\nUsers in database:")
for user in users:
    print(f"ID {user[0]}: {user[1]}")

# Check existing picks for current week
cursor.execute("""
    SELECT COUNT(*) 
    FROM user_picks up
    JOIN nfl_games ng ON up.game_id = ng.id
    WHERE ng.week = ? AND ng.season = 2025
""", (current_week,))

existing_picks = cursor.fetchone()[0]
print(f"\nExisting picks for Week {current_week}: {existing_picks}")

conn.close()