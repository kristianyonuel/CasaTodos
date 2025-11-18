import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔍 INVESTIGATING PICK SCORING DISCREPANCY")
print("=" * 50)

# Check a specific game to see the issue
print("📝 RAVENS @ DOLPHINS EXAMPLE:")
cursor.execute("""
    SELECT g.away_team, g.home_team, g.away_score, g.home_score,
           u.username, up.selected_team, up.is_correct, up.points_earned
    FROM nfl_games g
    JOIN user_picks up ON g.game_id = up.game_id  
    JOIN users u ON up.user_id = u.id
    WHERE g.away_team = 'Baltimore Ravens' AND g.home_team = 'Miami Dolphins'
    ORDER BY u.username
    LIMIT 5
""")

ravens_game = cursor.fetchall()
for away, home, away_score, home_score, user, pick, correct, points in ravens_game:
    winner = home if home_score > away_score else away
    print(f"   Game: {away} {away_score} - {home_score} {home}")
    print(f"   Winner should be: {winner}")
    print(f"   {user} picked: '{pick}' | Correct: {correct} | Points: {points}")
    print(f"   Match check: '{pick}' == '{winner}' = {pick == winner}")
    print()

# Check for potential team name mismatches
print("🔍 TEAM NAME COMPARISON:")
cursor.execute("""
    SELECT DISTINCT g.away_team, g.home_team, up.selected_team
    FROM nfl_games g
    JOIN user_picks up ON g.game_id = up.game_id
    WHERE g.week = 9 AND g.away_team = 'Baltimore Ravens'
    LIMIT 3
""")

for away, home, selected in cursor.fetchall():
    print(f"   Game teams: '{away}' vs '{home}'")
    print(f"   User selected: '{selected}'")
    print(f"   Exact match home: '{selected}' == '{home}' = {selected == home}")
    print(f"   Exact match away: '{selected}' == '{away}' = {selected == away}")
    print()

# Check what winners were actually set
print("🏆 ACTUAL WINNERS SET IN DATABASE:")
cursor.execute("""
    SELECT away_team, home_team, away_score, home_score,
           CASE WHEN home_score > away_score THEN home_team 
                WHEN away_score > home_score THEN away_team 
                ELSE 'TIE' END as calculated_winner
    FROM nfl_games 
    WHERE week = 9 AND is_final = 1
    ORDER BY game_date
    LIMIT 5
""")

for away, home, away_score, home_score, winner in cursor.fetchall():
    print(f"   {away} {away_score} - {home_score} {home} → Winner: {winner}")

conn.close()