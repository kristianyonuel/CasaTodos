import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('🏈 Adding Mikitin Colts pick...')

# Get Mikitin ID
cursor.execute('SELECT id FROM users WHERE username = ?', ('mikitin',))
mikitin_id = cursor.fetchone()[0]

# Add Mikitin's Colts pick (Indianapolis Colts)
cursor.execute("""
    INSERT INTO user_picks 
    (user_id, game_id, selected_team, selected_team_id, created_at) 
    VALUES (?, 382, 'Indianapolis Colts', 18, datetime('now'))
""", (mikitin_id,))

conn.commit()
print(f'Added Colts pick for Mikitin (ID: {mikitin_id})')

# Verify both users now
cursor.execute("""
    SELECT u.username, up.selected_team 
    FROM users u 
    LEFT JOIN user_picks up ON u.id = up.user_id AND up.game_id = 382 
    WHERE u.username IN ('kristian', 'mikitin') 
    ORDER BY u.id
""")

picks = cursor.fetchall()
print()
print('Final Colts game picks:')
for username, pick in picks:
    if username == 'kristian':
        status = '❌ MISSING (has X)' if not pick else '✓'
    else:
        status = '✓' if pick else '❌ MISSING'
    print(f'  {username}: {pick or "NO PICK"} {status}')

# Final verification of Week 10 totals
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
print('Final Week 10 totals:')
for username, count in totals:
    if username == 'kristian':
        print(f'  {username}: {count}/14 picks ❌ Missing Colts (X)')
    else:
        print(f'  {username}: {count}/14 picks ✓ Complete')

conn.close()