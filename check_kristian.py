import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🔍 CHECKING KRISTIAN'S WEEK 9 PICKS")
print("=" * 50)

# Get KRISTIAN's detailed picks
cursor.execute("""
    SELECT g.game_id, g.away_team, g.home_team, g.away_score, g.home_score,
           up.selected_team, up.is_correct, up.points_earned
    FROM user_picks up
    JOIN users u ON up.user_id = u.id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE u.username = 'kristian' AND g.week = 9 AND g.year = 2025
    ORDER BY g.game_id
""")

picks = cursor.fetchall()

if picks:
    print(f"KRISTIAN's picks for Week 9:")
    print("Game | Away Team vs Home Team | Score | Pick | Result")
    print("-" * 70)
    
    correct_count = 0
    for i, (game_id, away, home, away_score, home_score, pick, is_correct, points) in enumerate(picks, 1):
        result = "✅ CORRECT" if is_correct else "❌ WRONG"
        winner = away if away_score > home_score else home
        print(f"{i:2d}   | {away[:12]} vs {home[:12]} | {away_score}-{home_score} | {pick[:12]} | {result}")
        if is_correct:
            correct_count += 1
    
    print(f"\n🎯 KRISTIAN'S SUMMARY:")
    print(f"   Total picks: {len(picks)}")
    print(f"   Correct: {correct_count}")
    print(f"   Wrong: {len(picks) - correct_count}")
    print(f"   Score: {correct_count}/{len(picks)}")
    
    # Check if this matches what we expect (8/14)
    if correct_count == 8 and len(picks) == 14:
        print("✅ KRISTIAN's data is correct (8/14)")
    else:
        print(f"⚠️  KRISTIAN's data seems wrong: {correct_count}/{len(picks)} (expected 8/14)")
        
else:
    print("❌ No picks found for KRISTIAN in Week 9")

# Double-check KRISTIAN exists in users table
cursor.execute("SELECT id, username FROM users WHERE username ILIKE '%kristian%'")
kristian_users = cursor.fetchall()

if kristian_users:
    print(f"\n👤 KRISTIAN in users table:")
    for user_id, username in kristian_users:
        print(f"   ID: {user_id}, Username: '{username}'")
else:
    print("\n❌ KRISTIAN not found in users table")

# Check weekly_results for KRISTIAN
cursor.execute("""
    SELECT weekly_rank, correct_picks, total_points, total_picks
    FROM weekly_results wr
    JOIN users u ON wr.user_id = u.id
    WHERE u.username = 'kristian' AND wr.week = 9 AND wr.year = 2025
""")

weekly_result = cursor.fetchone()

if weekly_result:
    rank, correct, points, total = weekly_result
    print(f"\n📊 KRISTIAN's weekly_results entry:")
    print(f"   Rank: {rank}")
    print(f"   Correct picks: {correct}")
    print(f"   Total points: {points}")
    print(f"   Total picks: {total}")
else:
    print("\n❌ KRISTIAN not found in weekly_results for Week 9")

conn.close()