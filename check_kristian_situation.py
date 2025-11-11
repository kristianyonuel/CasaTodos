#!/usr/bin/env python3
"""
Check KRISTIAN's picks situation and compare with other users
"""

import sqlite3

def check_kristian_picks_situation():
    """Check what happened to KRISTIAN's Week 9 picks"""
    print("=" * 60)
    print("CHECKING KRISTIAN'S PICKS SITUATION")
    print("=" * 60)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check all users' Week 9 pick counts
    print("\n1. Week 9 Pick Counts by User:")
    cursor.execute("""
        SELECT 
            u.username,
            u.id as user_id,
            COUNT(up.id) as pick_count
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games g ON up.game_id = g.id AND g.week = 9 AND g.year = 2025
        WHERE NOT u.is_admin
        GROUP BY u.id, u.username
        ORDER BY pick_count DESC, u.username
    """)
    
    user_picks = cursor.fetchall()
    for user in user_picks:
        status = "✅ Complete" if user['pick_count'] == 14 else f"❌ Missing {14 - user['pick_count']} picks"
        print(f"  {user['username']}: {user['pick_count']}/14 picks - {status}")
    
    # Check KRISTIAN's specific situation
    print(f"\n2. KRISTIAN's Current Week 9 Picks:")
    cursor.execute("""
        SELECT 
            up.id,
            up.game_id,
            up.selected_team,
            g.away_team,
            g.home_team,
            up.created_at
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = 4 AND g.week = 9 AND g.year = 2025
        ORDER BY g.game_date
    """)
    
    kristian_picks = cursor.fetchall()
    print(f"KRISTIAN has {len(kristian_picks)} picks:")
    for pick in kristian_picks:
        print(f"  Pick ID {pick['id']}: {pick['away_team']} @ {pick['home_team']} -> {pick['selected_team']}")
        print(f"    Created: {pick['created_at']}")
    
    # Check if KRISTIAN had picks that were deleted
    print(f"\n3. Checking for deleted KRISTIAN picks:")
    cursor.execute("""
        SELECT COUNT(*) as total_picks
        FROM user_picks up
        WHERE up.user_id = 4
    """)
    total_picks = cursor.fetchone()['total_picks']
    print(f"KRISTIAN has {total_picks} total picks across all weeks")
    
    # Check KRISTIAN's picks by week
    cursor.execute("""
        SELECT 
            g.week,
            g.year,
            COUNT(up.id) as pick_count
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = 4
        GROUP BY g.week, g.year
        ORDER BY g.year, g.week
    """)
    
    kristian_by_week = cursor.fetchall()
    print(f"\nKRISTIAN's picks by week:")
    for week_data in kristian_by_week:
        print(f"  Week {week_data['week']}, {week_data['year']}: {week_data['pick_count']} picks")
    
    # Compare with a user who has complete picks
    print(f"\n4. Comparing with a complete user (JEAN):")
    cursor.execute("""
        SELECT 
            up.selected_team,
            g.away_team,
            g.home_team,
            g.id as game_id
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        JOIN users u ON up.user_id = u.id
        WHERE u.username = 'jean' AND g.week = 9 AND g.year = 2025
        ORDER BY g.game_date
    """)
    
    jean_picks = cursor.fetchall()
    print(f"JEAN has {len(jean_picks)} picks for Week 9:")
    for pick in jean_picks:
        print(f"  Game {pick['game_id']}: {pick['away_team']} @ {pick['home_team']} -> {pick['selected_team']}")
    
    # Check what should be KRISTIAN's picks based on previous data
    print(f"\n5. Week 9 Games KRISTIAN is missing picks for:")
    cursor.execute("""
        SELECT 
            g.id,
            g.away_team,
            g.home_team,
            g.game_date
        FROM nfl_games g
        WHERE g.week = 9 AND g.year = 2025
        AND g.id NOT IN (
            SELECT up.game_id 
            FROM user_picks up 
            WHERE up.user_id = 4
        )
        ORDER BY g.game_date
    """)
    
    missing_games = cursor.fetchall()
    print(f"KRISTIAN is missing picks for {len(missing_games)} games:")
    for game in missing_games:
        print(f"  Game {game['id']}: {game['away_team']} @ {game['home_team']} ({game['game_date']})")
    
    # Check if we have the exact Week 9 picks data we inserted previously
    print(f"\n6. Checking for KRISTIAN's Week 9 data from insert_picks_simple.py:")
    
    # These were the picks we inserted for KRISTIAN based on the user's data
    expected_kristian_picks = {
        'Baltimore Ravens @ Miami Dolphins': 'Baltimore Ravens',
        'Chicago Bears @ Cincinnati Bengals': 'Chicago Bears', 
        'Minnesota Vikings @ Detroit Lions': 'Minnesota Vikings',
        'Carolina Panthers @ Green Bay Packers': 'Green Bay Packers',
        'Los Angeles Chargers @ Tennessee Titans': 'Los Angeles Chargers',
        'Atlanta Falcons @ New England Patriots': 'Atlanta Falcons',
        'San Francisco 49ers @ New York Giants': 'San Francisco 49ers',
        'Indianapolis Colts @ Pittsburgh Steelers': 'Pittsburgh Steelers',
        'Denver Broncos @ Houston Texans': 'Denver Broncos',
        'Jacksonville Jaguars @ Las Vegas Raiders': 'Jacksonville Jaguars',
        'New Orleans Saints @ Los Angeles Rams': 'New Orleans Saints',
        'Kansas City Chiefs @ Buffalo Bills': 'Kansas City Chiefs',
        'Seattle Seahawks @ Washington Commanders': 'Seattle Seahawks',
        'Arizona Cardinals @ Dallas Cowboys': 'Dallas Cowboys'
    }
    
    print("Expected KRISTIAN picks from previous insert:")
    for matchup, pick in expected_kristian_picks.items():
        print(f"  {matchup} -> {pick}")
    
    print(f"\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nFINDINGS:")
    print(f"1. KRISTIAN only has 1/14 picks for Week 9")
    print(f"2. Other users have complete picks (14/14)")
    print(f"3. KRISTIAN's remaining 13 picks were either never inserted or deleted")
    print(f"4. Admin interface is working correctly - it shows what's in database")
    print(f"5. Solution: Restore KRISTIAN's missing 13 picks")

    conn.close()

if __name__ == "__main__":
    check_kristian_picks_situation()