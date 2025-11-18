import sqlite3

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏆 ACTUAL CORRECT PICKS IN DATABASE")
print("=" * 50)

# Get all correct picks for Week 9
cursor.execute("""
    SELECT u.username, g.away_team, g.home_team, g.away_score, g.home_score,
           up.selected_team, up.is_correct, up.points_earned
    FROM users u
    JOIN user_picks up ON u.id = up.user_id
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9 AND up.is_correct = 1
    ORDER BY u.username, g.game_date
""")

correct_picks = cursor.fetchall()
print(f"📊 Total correct picks: {len(correct_picks)}")

current_user = None
for username, away, home, away_score, home_score, selected, correct, points in correct_picks:
    if username != current_user:
        if current_user is not None:
            print()
        print(f"🎯 {username.upper()}:")
        current_user = username
    
    winner = home if home_score > away_score else away
    print(f"   ✅ {away} @ {home} ({away_score}-{home_score}) → Picked: {selected} (Winner: {winner})")

print(f"\n🔧 WEB INTERFACE ISSUE:")
print("The database shows correct scoring, but the web interface shows all ✗")
print("This indicates:")
print("1. Browser cache issue")
print("2. Flask app needs restart")
print("3. Frontend not reading updated database")

print(f"\n💡 SOLUTIONS:")
print("1. Clear browser cache and refresh")
print("2. Restart Flask app: sudo systemctl restart lacasadetodos.service")
print("3. Force refresh: Ctrl+F5 or Shift+Reload")

conn.close()