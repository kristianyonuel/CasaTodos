import sqlite3

# Raw picks data from user
users_raw = ["JAVIER", "VIZCA", "ROBERT", "COYOTE", "JEAN", "RAMFIS", "GUILLERMO", "JONIEL", "RADA", "RAYMOND", "SHORTY", "KRISTIAN", "FER"]

picks_raw = [
    "eagles eagles eagles eagles eagles eagles eagles eagles eagles giants eagles eagles eagles",
    "Denver Denver Denver Denver X Denver Denver Denver Denver Denver Denver Denver X",
    "Rams Rams Rams Rams Rams Rams Ravens Rams Rams Rams Rams Rams Rams",
    "Dallas Dallas Dallas Dallas Dallas Dallas Panthers Dallas Dallas Dallas Dallas Dallas Dallas",
    "Colts Colts Colts Colts Colts Colts Colts Colts Colts Colts Colts Colts Colts",
    "Jax Seattle Jax Jax Jax Seattle Jax Jax Jax Jax Jax Seattle Jax",
    "Chargers Miami Chargers Chargers Chargers Chargers Miami Chargers Chargers Chargers Chargers Chargers Chargers",
    "Pitt Pitt Pitt Pitt Pitt Pitt Pitt Pitt Pitt Pitt Pitt Pitt Pitt",
    "Pats Pats Pats Pats Pats Pats Pats Pats Pats Pats Pats Pats Pats",
    "Titans Raiders Raiders Raiders Raiders Raiders Raiders Raiders Raiders Raiders Raiders Raiders Titans",
    "Gb Gb Gb Gb Gb Gb Gb Gb Gb Gb Gb Gb Gb",
    "49ers Bucs Bucs Bucs X Bucs 49ers Bucs Bucs Bucs 49ers Bucs 49ers",
    "Lions Lions Lions Kc Lions Kc Lions Lions Kc Lions Lions Kc Kc",
    "Bills Bills Bills Bills Bills Bills Bills Bills Bills Bills Bills Bills Bills",
    "Wash Wash Bears Wash Wash Wash Wash Wash Wash Wash Wash Wash Wash"
]

tiebreakers_raw = "20-17 27-23 27-21 27-14 30-14 27-17 24-18 31-24 27-15 27-23 34-24 21-13 21-17"

# Team name mappings
team_mappings = {
    'eagles': 'PHI',
    'giants': 'NYG',
    'denver': 'DEN',
    'rams': 'LAR',
    'ravens': 'BAL',
    'dallas': 'DAL',
    'panthers': 'CAR',
    'colts': 'IND',
    'jax': 'JAX',
    'seattle': 'SEA',
    'chargers': 'LAC',
    'miami': 'MIA',
    'pitt': 'PIT',
    'pats': 'NE',
    'titans': 'TEN',
    'raiders': 'LV',
    'gb': 'GB',
    '49ers': 'SF',
    'bucs': 'TB',
    'lions': 'DET',
    'kc': 'KC',
    'bills': 'BUF',
    'wash': 'WSH',
    'bears': 'CHI'
}

# Connect to database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Get Week 6 games (current week)
current_week = 6
cursor.execute("""
    SELECT id, home_team, away_team, game_date, is_monday_night 
    FROM nfl_games 
    WHERE week = ? AND year = 2025 
    ORDER BY game_date
""", (current_week,))

games = cursor.fetchall()
print(f"Week {current_week} Games:")
for i, game in enumerate(games):
    print(f"Game {i+1} (ID {game[0]}): {game[2]} @ {game[1]} - {game[3]} {'(MNF)' if game[4] else ''}")

print(f"\nTotal games: {len(games)}")
print(f"Total pick rows: {len(picks_raw)}")

# Get users from database
cursor.execute("SELECT id, username FROM users ORDER BY username")
db_users = cursor.fetchall()
print(f"\nUsers in database:")
for user in db_users:
    print(f"ID {user[0]}: {user[1]}")

# Process picks data
print(f"\n=== PREVIEW OF PICKS DATA ===")
print(f"Number of users: {len(users_raw)}")
print(f"Number of games: {len(picks_raw)}")

# Parse tiebreakers
tiebreakers = tiebreakers_raw.split()
print(f"Number of tiebreakers: {len(tiebreakers)}")

# Parse each game's picks
for game_idx, pick_line in enumerate(picks_raw):
    picks = pick_line.split()
    print(f"\nGame {game_idx + 1} picks:")
    
    if game_idx < len(games):
        game_info = games[game_idx]
        print(f"  Game: {game_info[2]} @ {game_info[1]} (ID: {game_info[0]})")
    
    for user_idx, pick in enumerate(picks):
        if user_idx < len(users_raw):
            username = users_raw[user_idx]
            if pick.lower() in team_mappings:
                team_code = team_mappings[pick.lower()]
                print(f"    {username}: {pick} -> {team_code}")
            elif pick == 'X':
                print(f"    {username}: NO PICK (X)")
            else:
                print(f"    {username}: {pick} -> UNKNOWN TEAM")

print(f"\nTiebreakers:")
for i, tb in enumerate(tiebreakers):
    if i < len(users_raw):
        username = users_raw[i]
        print(f"  {username}: {tb}")

# Check for Monday Night game
monday_games = [g for g in games if g[4]]  # is_monday_night = True
if monday_games:
    print(f"\nMonday Night Football game found: {monday_games[0][2]} @ {monday_games[0][1]}")
    print("This will be used for tiebreaker score predictions.")

conn.close()

print(f"\n=== SUMMARY ===")
print(f"✓ {len(users_raw)} users to process")
print(f"✓ {len(picks_raw)} games with picks")
print(f"✓ {len(tiebreakers)} tiebreaker predictions")
print(f"✓ Week {current_week} games in database: {len(games)}")

if len(picks_raw) != len(games):
    print(f"⚠️  WARNING: Mismatch between pick rows ({len(picks_raw)}) and games ({len(games)})")
    
if len(tiebreakers) != len(users_raw):
    print(f"⚠️  WARNING: Mismatch between tiebreakers ({len(tiebreakers)}) and users ({len(users_raw)})")