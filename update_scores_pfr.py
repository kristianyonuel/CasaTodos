import sqlite3

# Week 10 NFL Scores from Pro Football Reference (November 2025)
week_10_scores = {
    # Nov 6, 2025
    "Las Vegas Raiders @ Denver Broncos": {"away_score": 7, "home_score": 10, "winner": "Denver Broncos"},
    
    # Nov 9, 2025  
    "Atlanta Falcons @ Indianapolis Colts": {"away_score": 25, "home_score": 31, "winner": "Indianapolis Colts", "overtime": True},
    "Buffalo Bills @ Miami Dolphins": {"away_score": 13, "home_score": 30, "winner": "Miami Dolphins"},
    "Jacksonville Jaguars @ Houston Texans": {"away_score": 29, "home_score": 36, "winner": "Houston Texans"},
    "Minnesota Vikings @ Baltimore Ravens": {"away_score": 19, "home_score": 27, "winner": "Baltimore Ravens"},
    "New York Jets @ Cleveland Browns": {"away_score": 27, "home_score": 20, "winner": "New York Jets"},
    "New England Patriots @ Tampa Bay Buccaneers": {"away_score": 28, "home_score": 23, "winner": "New England Patriots"},
    "Carolina Panthers @ New Orleans Saints": {"away_score": 7, "home_score": 17, "winner": "New Orleans Saints"},
    "Arizona Cardinals @ Seattle Seahawks": {"away_score": 22, "home_score": 44, "winner": "Seattle Seahawks"},
    "Los Angeles Rams @ San Francisco 49ers": {"away_score": 42, "home_score": 26, "winner": "Los Angeles Rams"},
    "Detroit Lions @ Washington Commanders": {"away_score": 44, "home_score": 22, "winner": "Detroit Lions"},
    "Chicago Bears @ New York Giants": {"away_score": 24, "home_score": 20, "winner": "Chicago Bears"},
    "Pittsburgh Steelers @ Los Angeles Chargers": {"away_score": 10, "home_score": 25, "winner": "Los Angeles Chargers"}
    # Monday Night (Nov 10) - Eagles @ Packers still needs to be found
}

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏈 UPDATING WEEK 10 SCORES FROM PRO FOOTBALL REFERENCE")
print("=" * 55)

updated_games = 0
total_correct_picks = 0

# Get all Week 10 games
cursor.execute('SELECT id, away_team, home_team FROM nfl_games WHERE week = 10')
games = cursor.fetchall()

for game_id, away_team, home_team in games:
    game_key = f"{away_team} @ {home_team}"
    
    if game_key in week_10_scores:
        score_data = week_10_scores[game_key]
        away_score = score_data["away_score"]
        home_score = score_data["home_score"]
        winner = score_data["winner"]
        
        # Update the game with final scores
        cursor.execute("""
            UPDATE nfl_games 
            SET away_score = ?, home_score = ?, game_status = 'Final', is_final = 1,
                overtime = ?
            WHERE id = ?
        """, (away_score, home_score, score_data.get("overtime", False), game_id))
        
        # Determine winning team for pick validation
        if away_score > home_score:
            winning_team = away_team
        else:
            winning_team = home_team
        
        # Update user picks with correct/incorrect status
        cursor.execute("""
            UPDATE user_picks 
            SET is_correct = CASE 
                WHEN selected_team = ? THEN 1 
                ELSE 0 
            END,
            points_earned = CASE 
                WHEN selected_team = ? THEN 1 
                ELSE 0 
            END
            WHERE game_id = ?
        """, (winning_team, winning_team, game_id))
        
        updated_games += 1
        
        # Count correct picks for this game
        cursor.execute('SELECT COUNT(*) FROM user_picks WHERE game_id = ? AND is_correct = 1', (game_id,))
        correct_count = cursor.fetchone()[0]
        total_correct_picks += correct_count
        
        overtime_note = " (OT)" if score_data.get("overtime") else ""
        print(f"✅ {game_key}: {away_score}-{home_score} → {winner} wins{overtime_note}")
        print(f"   {correct_count} users picked correctly")
    else:
        print(f"❌ {game_key}: Score not found in Pro Football Reference data")

print(f"\nUpdated {updated_games} games with final scores")
print(f"Total correct picks across all updated games: {total_correct_picks}")

# Show current Week 10 leaderboard
print(f"\n📊 CURRENT WEEK 10 LEADERBOARD:")
print("=" * 35)

cursor.execute("""
    SELECT u.username, 
           SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
           COUNT(up.id) as total_picks
    FROM users u 
    LEFT JOIN user_picks up ON u.id = up.user_id 
        AND up.game_id IN (SELECT id FROM nfl_games WHERE week = 10 AND is_final = 1)
    GROUP BY u.id, u.username 
    ORDER BY correct_picks DESC, u.username
""")

leaderboard = cursor.fetchall()
for username, correct, total in leaderboard:
    if total > 0:
        percentage = (correct / total) * 100
        print(f"{username:12}: {correct}/{total} correct ({percentage:.1f}%)")
    else:
        print(f"{username:12}: No picks in completed games")

conn.commit()
conn.close()

print(f"\n✅ Week 10 scores updated from Pro Football Reference!")
print(f"Note: Some games may still need scores (like Monday Night Football)")