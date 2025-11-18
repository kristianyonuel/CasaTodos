import sqlite3

# Connect to database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Get Week 6 games with more detail
current_week = 6
cursor.execute("""
    SELECT id, home_team, away_team, game_date, is_monday_night, is_thursday_night
    FROM nfl_games 
    WHERE week = ? AND year = 2025 
    ORDER BY game_date
""", (current_week,))

games = cursor.fetchall()
print(f"Week {current_week} Games - Full Details:")
for i, game in enumerate(games, 1):
    game_day = "THU" if game[5] else ("MON" if game[4] else "SUN")
    print(f"Game {i:2d} (ID {game[0]}): {game[2]:3s} @ {game[1]:3s} - {game_day} - {game[3]}")

# Check if there are any other weeks that might match the picks better
print("\n=== Checking other weeks for better match ===")

# Check teams mentioned in picks vs actual games
picks_teams = ['PHI', 'NYG', 'DEN', 'NYJ', 'LAR', 'BAL', 'DAL', 'CAR', 
              'IND', 'JAX', 'SEA', 'LAC', 'MIA', 'PIT', 'CLE', 'NE', 'NO',
              'TEN', 'LV', 'GB', 'CIN', 'SF', 'TB', 'DET', 'KC', 'BUF', 'ATL', 'WSH', 'CHI']

week6_teams = set()
for game in games:
    week6_teams.add(game[1])  # home team
    week6_teams.add(game[2])  # away team

print(f"\nTeams in Week 6: {sorted(week6_teams)}")

missing_from_week6 = set(picks_teams) - week6_teams
print(f"Teams in picks but NOT in Week 6: {sorted(missing_from_week6)}")

teams_only_in_week6 = week6_teams - set(picks_teams)
print(f"Teams in Week 6 but NOT in picks: {sorted(teams_only_in_week6)}")

conn.close()

print("\n=== ANALYSIS ===")
print("The picks data appears to have some misalignments.")
print("Let me suggest the correct mapping based on actual games:")

# Raw picks data as provided
users_raw = ["JAVIER", "VIZCA", "ROBERT", "COYOTE", "JEAN", "RAMFIS", "GUILLERMO", "JONIEL", "RADA", "RAYMOND", "SHORTY", "KRISTIAN", "FER"]

# Actual game matchups for Week 6
actual_games = [
    ("PHI @ NYG", "eagles/giants"),
    ("DEN @ NYJ", "Denver/Jets"), 
    ("LAR @ BAL", "Rams/Ravens"),
    ("DAL @ CAR", "Dallas/Panthers"),
    ("SEA @ JAX", "Seattle/Jax"),  # This should match the SEA/Jax picks
    ("ARI @ IND", "Cardinals/Colts"),  # This could match the Colts picks
    ("LAC @ MIA", "Chargers/Miami"),
    ("CLE @ PIT", "Browns/Pitt"),
    ("SF @ TB", "49ers/Bucs"),  # This should match 49ers/Bucs picks
    ("TEN @ LV", "Titans/Raiders"),
    ("NE @ NO", "Pats/Saints"),  # This should match Pats picks  
    ("CIN @ GB", "Bengals/Gb"),  # This should match Gb picks
    ("DET @ KC", "Lions/Kc"),
    ("BUF @ ATL", "Bills/Falcons"),
    ("CHI @ WSH", "Bears/Wash")
]

print("\nSuggested correct alignment:")
for i, (game, teams) in enumerate(actual_games, 1):
    print(f"Row {i:2d}: {game:12s} - Pick teams: {teams}")