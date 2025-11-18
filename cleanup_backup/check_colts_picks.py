import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏈 COLTS GAME PICK VERIFICATION")
print("=" * 35)

# Game 382: Atlanta Falcons @ Indianapolis Colts
print("Checking picks for Game 382 (Falcons @ Colts):")

cursor.execute("""
    SELECT u.username, up.selected_team 
    FROM users u 
    LEFT JOIN user_picks up ON u.id = up.user_id AND up.game_id = 382 
    WHERE u.username IN ('kristian', 'mikitin') 
    ORDER BY u.id
""")
picks = cursor.fetchall()

for username, pick in picks:
    status = "✓" if pick else "❌ MISSING"
    pick_display = pick if pick else "NO PICK"
    print(f"  {username:8}: {pick_display:10} {status}")

print()
print("Total Week 10 picks verification:")

cursor.execute("""
    SELECT u.username, COUNT(up.id) 
    FROM users u 
    LEFT JOIN user_picks up ON u.id = up.user_id 
        AND up.game_id IN (SELECT id FROM nfl_games WHERE week = 10) 
    WHERE u.username IN ('kristian', 'mikitin') 
    GROUP BY u.username 
    ORDER BY u.id
""")
totals = cursor.fetchall()

for username, count in totals:
    status = "✓" if count == 14 else f"❌ Missing {14-count} picks"
    print(f"  {username:8}: {count}/14 picks {status}")

# Based on user's table: Kristian should have 'colts', Mikitin should be missing
print()
print("USER TABLE VERIFICATION:")
print("According to user's data:")
print("- Kristian (position 12): 'colts' ✓") 
print("- Mikitin (position 14): [EMPTY] ❌")

conn.close()