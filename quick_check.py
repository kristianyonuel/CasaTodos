import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏆 CURRENT WEEK 9 LEADERBOARD:")
print("=" * 40)

cursor.execute("""
    SELECT u.username, 
           SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
           COUNT(*) as total
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9 AND g.year = 2025
    GROUP BY u.id, u.username
    ORDER BY correct DESC
""")

results = cursor.fetchall()

if results:
    for i, (username, correct, total) in enumerate(results, 1):
        print(f"{i:2d}. {username:12s} - {correct:2d}/{total} correct")
    
    print(f"\n✅ Total: {len(results)} users with picks")
    
    # Check if KRISTIAN is in the results
    kristian_data = [r for r in results if r[0].lower() == 'kristian']
    if kristian_data:
        username, correct, total = kristian_data[0]
        print(f"🎯 KRISTIAN: {correct}/{total} correct")
    else:
        print("❌ KRISTIAN not found in results")
        
else:
    print("❌ No Week 9 data found")

# Check what other weeks have data
print(f"\n📅 OTHER WEEKS WITH PICKS:")
cursor.execute("""
    SELECT g.week, g.year, COUNT(DISTINCT u.username) as users
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games g ON up.game_id = g.game_id
    GROUP BY g.week, g.year
    ORDER BY g.year, g.week
""")

other_weeks = cursor.fetchall()
for week, year, users in other_weeks:
    print(f"   Week {week}, {year}: {users} users")

conn.close()