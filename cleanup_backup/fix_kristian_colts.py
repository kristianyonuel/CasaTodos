import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('🚨 EMERGENCY CORRECTION: Kristian has X, not Colts pick!')
print('=' * 50)

# Get user IDs
cursor.execute('SELECT id FROM users WHERE username = ?', ('kristian',))
kristian_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('mikitin',))  
mikitin_id = cursor.fetchone()[0]

print(f'Kristian ID: {kristian_id}')
print(f'Mikitin ID: {mikitin_id}')

# Game 382 is the Colts game
colts_game_id = 382

# DELETE Kristian's incorrect Colts pick
cursor.execute('DELETE FROM user_picks WHERE user_id = ? AND game_id = ?', 
               (kristian_id, colts_game_id))
deleted_rows = cursor.rowcount

# Check if Mikitin has Colts pick (should have it)
cursor.execute('SELECT selected_team FROM user_picks WHERE user_id = ? AND game_id = ?', 
               (mikitin_id, colts_game_id))
mikitin_pick = cursor.fetchone()

print(f'Deleted Kristian Colts pick: {deleted_rows} rows')
mikitin_has_pick = "YES" if mikitin_pick else "NO"
mikitin_team = mikitin_pick[0] if mikitin_pick else "NONE"
print(f'Mikitin has Colts pick: {mikitin_has_pick} ({mikitin_team})')

# Verify final state
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

print()
print('Corrected Week 10 totals:')
for username, count in totals:
    status = "✓" if count == 14 else f"❌ Missing {14-count}"
    print(f'  {username}: {count}/14 picks {status}')

conn.commit()
conn.close()

print()
print('✅ CORRECTED: Kristian now missing Colts (has X), Mikitin has Colts pick')