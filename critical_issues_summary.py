import sqlite3
from datetime import datetime

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🚨 CRITICAL ISSUES FOUND!")
print("=" * 40)

print("1. 📊 LEADERBOARD SHOWING EMPTY:")
print("   - No picks are being counted in leaderboard query")
print("   - Users showing 0 picks, 0 correct, 0 points")

print("\n2. 🎮 GAMES NOT UPDATING:")
print("   - Only 2 games show as 'Final' out of 10+ that played")
print("   - San Francisco 49ers @ New York Giants: 23-3 ✅")
print("   - Los Angeles Chargers @ Tennessee Titans: 14-38 ✅")
print("   - 12 other games still show 'scheduled' despite being played")

print("\n3. 🎯 SCORING PROBLEM:")
print("   - 28 unscored picks found")
print("   - Games are final but picks aren't being scored")

print("\n4. ⏰ UPDATE TIMING:")
print("   - Last game update: 2025-10-29 (4 days ago!)")
print("   - No automatic updates happening")

print("\n🔧 IMMEDIATE ACTIONS NEEDED:")
print("1. Fix the background updater/game fetcher")
print("2. Update game scores for 10+ games from last night") 
print("3. Score all picks for completed games")
print("4. Fix leaderboard calculation")

# Check if background updater is running
print(f"\n📋 CHECKING BACKGROUND PROCESSES:")
try:
    # Check what processes might be updating games
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE game_status = 'in_progress'")
    in_progress = cursor.fetchone()[0]
    print(f"   Games currently in progress: {in_progress}")
    
    cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE game_status = 'final'")
    final_games = cursor.fetchone()[0]
    print(f"   Total final games in database: {final_games}")
    
    # Check for any recent activity
    cursor.execute("SELECT MAX(created_at) FROM user_picks")
    last_pick = cursor.fetchone()[0]
    print(f"   Last pick created: {last_pick}")
    
except Exception as e:
    print(f"   Error checking: {e}")

# Simple leaderboard fix test
print(f"\n🧪 TESTING LEADERBOARD QUERY:")
cursor.execute("""
    SELECT u.username, COUNT(up.id) as picks
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9
    GROUP BY u.username
    LIMIT 5
""")

test_results = cursor.fetchall()
print(f"   Sample results: {test_results}")

conn.close()

print(f"\n🎯 NEXT STEPS:")
print("1. Run background updater manually")
print("2. Update game scores from ESPN/NFL API")
print("3. Score picks for completed games")
print("4. Verify leaderboard calculations")