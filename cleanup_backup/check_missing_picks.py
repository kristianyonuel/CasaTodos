import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔍 CHECKING MISSING GAMES FOR COYOTE, RAYMOND, RADA")
print("=" * 55)

# Get all Week 9 games
cursor.execute("""
    SELECT game_id, away_team, home_team, game_date
    FROM nfl_games 
    WHERE week = 9 
    ORDER BY game_date, game_id
""")
all_games = cursor.fetchall()

print(f"📅 Total Week 9 games: {len(all_games)}")

# Check each user's picks
users_to_check = ['coyote', 'raymond', 'rada']

for username in users_to_check:
    print(f"\n🔍 {username.upper()}:")
    
    # Get user's picks
    cursor.execute("""
        SELECT g.game_id, g.away_team, g.home_team, up.selected_team
        FROM nfl_games g
        LEFT JOIN user_picks up ON g.game_id = up.game_id 
        LEFT JOIN users u ON up.user_id = u.id AND u.username = ?
        WHERE g.week = 9
        ORDER BY g.game_date, g.game_id
    """, (username,))
    
    user_picks = cursor.fetchall()
    
    has_picks = 0
    missing_games = []
    
    for game_id, away, home, selected in user_picks:
        if selected:
            has_picks += 1
            print(f"   ✅ {away} @ {home} -> {selected}")
        else:
            missing_games.append(f"{away} @ {home}")
            print(f"   ❌ {away} @ {home} -> MISSING")
    
    print(f"   📊 Has {has_picks} picks, Missing {len(missing_games)} games")
    
    if missing_games:
        print(f"   🚨 Missing games:")
        for game in missing_games:
            print(f"      - {game}")

# Total picks per user
print(f"\n📊 PICK COUNTS:")
cursor.execute("""
    SELECT u.username, COUNT(up.id) as pick_count
    FROM users u
    LEFT JOIN user_picks up ON u.id = up.user_id
    LEFT JOIN nfl_games g ON up.game_id = g.game_id AND g.week = 9
    WHERE u.username IN ('coyote', 'raymond', 'rada')
    GROUP BY u.username
    ORDER BY u.username
""")

for username, count in cursor.fetchall():
    print(f"   {username}: {count} picks")

conn.close()