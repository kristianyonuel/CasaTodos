import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔧 ADDING VIZCA'S WEEK 9 PICKS")
print("=" * 30)

# Get VIZCA's user ID
cursor.execute("SELECT id FROM users WHERE username = 'vizca'")
vizca_user = cursor.fetchone()

if not vizca_user:
    print("❌ VIZCA not found!")
    exit()

vizca_id = vizca_user[0]
print(f"✅ Found VIZCA (ID: {vizca_id})")

# Get Week 9 games in order
cursor.execute("""
    SELECT game_id, away_team, home_team 
    FROM nfl_games 
    WHERE week = 9 
    ORDER BY game_date, game_id
""")
games = cursor.fetchall()

print(f"📅 Found {len(games)} Week 9 games")

# VIZCA's picks (2nd column from your data)
vizca_picks = [
    'Baltimore Ravens',    # ravens
    'Chicago Bears',       # Bears 
    'Detroit Lions',       # Lions
    'Green Bay Packers',   # Gb
    'Los Angeles Chargers', # Chargers
    'New England Patriots', # Pats
    'San Francisco 49ers',  # 49ers
    'Indianapolis Colts',   # Colts
    'Houston Texans',      # Texans
    'Jacksonville Jaguars', # Jax
    'Los Angeles Rams',    # Rams
    'Buffalo Bills',       # Bills
    'Seattle Seahawks',    # Seattle
    'Arizona Cardinals'    # Arizona
]

# Map to actual game order (games are ordered by date)
game_picks_mapping = {
    0: 'Baltimore Ravens',     # Ravens @ Dolphins (10/30)
    1: 'New England Patriots', # Falcons @ Patriots (11/2)
    2: 'Buffalo Bills',        # Chiefs @ Bills (11/2)
    3: 'Jacksonville Jaguars', # Jaguars @ Raiders (11/2)
    4: 'Houston Texans',       # Broncos @ Texans (11/2)
    5: 'Green Bay Packers',    # Panthers @ Packers (11/2)
    6: 'Los Angeles Rams',     # Saints @ Rams (11/2)
    7: 'Chicago Bears',        # Bears @ Bengals (11/2)
    8: 'Detroit Lions',        # Vikings @ Lions (11/2)
    9: 'Seattle Seahawks',     # Seahawks @ Commanders (11/2)
    10: 'San Francisco 49ers', # 49ers @ Giants (11/2)
    11: 'Los Angeles Chargers', # Chargers @ Titans (11/2)
    12: 'Indianapolis Colts',  # Colts @ Steelers (11/2)
    13: 'Arizona Cardinals'    # Cardinals @ Cowboys (11/3)
}

picks_added = 0

for i, (game_id, away, home) in enumerate(games):
    if i in game_picks_mapping:
        selected_team = game_picks_mapping[i]
        
        # Check if pick already exists
        cursor.execute("""
            SELECT COUNT(*) FROM user_picks 
            WHERE user_id = ? AND game_id = ?
        """, (vizca_id, game_id))
        
        if cursor.fetchone()[0] == 0:
            # Add the pick
            cursor.execute("""
                INSERT INTO user_picks (user_id, game_id, selected_team) 
                VALUES (?, ?, ?)
            """, (vizca_id, game_id, selected_team))
            picks_added += 1
            print(f"   ✅ Game {i+1}: {away} @ {home} -> {selected_team}")

# Add tiebreaker for Monday Night (34-31)
monday_game_id = games[13][0]
cursor.execute("""
    UPDATE user_picks 
    SET predicted_away_score = 34, predicted_home_score = 31
    WHERE user_id = ? AND game_id = ?
""", (vizca_id, monday_game_id))

conn.commit()
print(f"\n✅ Added {picks_added} picks for VIZCA")
print("✅ Added tiebreaker: 34-31")

# Verify
cursor.execute("""
    SELECT COUNT(*) FROM user_picks up 
    JOIN nfl_games g ON up.game_id = g.game_id 
    WHERE up.user_id = ? AND g.week = 9
""", (vizca_id,))

total = cursor.fetchone()[0]
print(f"🔍 VIZCA now has {total} Week 9 picks")

conn.close()