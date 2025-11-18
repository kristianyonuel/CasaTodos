import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print("🏈 WEEKLY LEADERBOARD & GAME UPDATE CHECK")
print("=" * 50)

# Check current date and recent games
print(f"📅 Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📅 Yesterday: {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}")

# Check Week 9 games and their status
print(f"\n📊 WEEK 9 GAMES STATUS:")
cursor.execute("""
    SELECT game_id, away_team, home_team, game_date, game_status, 
           away_score, home_score, is_final
    FROM nfl_games 
    WHERE week = 9 
    ORDER BY game_date, game_id
""")

week9_games = cursor.fetchall()
games_played = 0
games_final = 0

for game_id, away, home, date, status, away_score, home_score, is_final in week9_games:
    status_emoji = "🟢" if is_final else "🟡" if status != 'scheduled' else "⏰"
    score_text = f"{away_score}-{home_score}" if away_score is not None and home_score is not None else "No score"
    
    print(f"   {status_emoji} {away} @ {home}")
    print(f"      Date: {date} | Status: {status} | Score: {score_text} | Final: {is_final}")
    
    if status != 'scheduled':
        games_played += 1
    if is_final:
        games_final += 1

print(f"\n📈 GAME PROGRESS:")
print(f"   Total Week 9 games: {len(week9_games)}")
print(f"   Games played: {games_played}")
print(f"   Games finalized: {games_final}")

# Check picks and scoring
print(f"\n🎯 PICKS & SCORING OVERVIEW:")
cursor.execute("""
    SELECT u.username, 
           COUNT(up.id) as total_picks,
           SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
           SUM(up.points_earned) as total_points
    FROM users u
    LEFT JOIN user_picks up ON u.id = up.user_id
    LEFT JOIN nfl_games g ON up.game_id = g.game_id AND g.week = 9
    WHERE u.username IN ('JAVIER', 'VIZCA', 'ROBERT', 'COYOTE', 'JEAN', 'RAMFIS', 'GUILLERMO', 'JONIEL', 'RADA', 'RAYMOND', 'SHORTY', 'KRISTIAN', 'FER', 'MIKITIN')
    GROUP BY u.username
    ORDER BY total_points DESC, correct_picks DESC
""")

leaderboard = cursor.fetchall()
print(f"   {'Rank':<4} {'User':<12} {'Picks':<6} {'Correct':<8} {'Points':<7}")
print(f"   {'-'*4} {'-'*12} {'-'*6} {'-'*8} {'-'*7}")

for rank, (username, picks, correct, points) in enumerate(leaderboard, 1):
    picks = picks or 0
    correct = correct or 0
    points = points or 0
    print(f"   {rank:<4} {username:<12} {picks:<6} {correct:<8} {points:<7}")

# Check if any games from last night need updates
print(f"\n🔍 RECENT GAMES CHECK (Last 24 hours):")
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
cursor.execute("""
    SELECT game_id, away_team, home_team, game_date, game_status, 
           away_score, home_score, is_final
    FROM nfl_games 
    WHERE DATE(game_date) >= ? AND week = 9
    ORDER BY game_date DESC
""", (yesterday,))

recent_games = cursor.fetchall()
if recent_games:
    for game_id, away, home, date, status, away_score, home_score, is_final in recent_games:
        status_icon = "✅" if is_final else "⚠️" if status != 'scheduled' else "⏰"
        score_text = f"{away_score}-{home_score}" if away_score is not None else "TBD"
        print(f"   {status_icon} {away} @ {home} | {date} | {status} | {score_text}")
else:
    print("   No games found in last 24 hours")

# Check for unscored picks
print(f"\n❌ UNSCORED PICKS CHECK:")
cursor.execute("""
    SELECT COUNT(*) as unscored_picks
    FROM user_picks up
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9 AND g.is_final = 1 AND up.is_correct IS NULL
""")

unscored = cursor.fetchone()[0]
print(f"   Games finished but picks not scored: {unscored}")

if unscored > 0:
    cursor.execute("""
        SELECT DISTINCT g.away_team, g.home_team, g.away_score, g.home_score
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.game_id
        WHERE g.week = 9 AND g.is_final = 1 AND up.is_correct IS NULL
        ORDER BY g.game_date
    """)
    
    unscored_games = cursor.fetchall()
    print(f"   Unscored games:")
    for away, home, away_score, home_score in unscored_games:
        print(f"      {away} @ {home} ({away_score}-{home_score})")

# Check when last update happened
print(f"\n⏰ LAST UPDATE TIMESTAMPS:")
cursor.execute("""
    SELECT MAX(updated_at) as last_game_update
    FROM nfl_games 
    WHERE week = 9
""")
last_update = cursor.fetchone()[0]
print(f"   Last game update: {last_update}")

cursor.execute("""
    SELECT MAX(updated_at) as last_pick_update
    FROM user_picks up
    JOIN nfl_games g ON up.game_id = g.game_id
    WHERE g.week = 9
""")
last_pick_update = cursor.fetchone()[0]
print(f"   Last pick update: {last_pick_update}")

conn.close()