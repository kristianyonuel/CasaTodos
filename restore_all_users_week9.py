#!/usr/bin/env python3
"""
Check all users' Week 9 picks status and restore missing picks for everyone
"""

import sqlite3

def check_all_users_week9_status():
    """Check which users are missing Week 9 picks"""
    print("=" * 70)
    print("CHECKING ALL USERS' WEEK 9 PICKS STATUS")
    print("=" * 70)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all non-admin users
    cursor.execute("SELECT id, username FROM users WHERE NOT is_admin ORDER BY username")
    all_users = cursor.fetchall()
    
    print(f"\nFound {len(all_users)} non-admin users")
    
    # Check each user's Week 9 pick count
    users_missing_picks = []
    
    print("\nWeek 9 Pick Status by User:")
    print("-" * 50)
    
    for user in all_users:
        cursor.execute("""
            SELECT COUNT(*) as pick_count
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = 9 AND g.year = 2025
        """, (user['id'],))
        
        pick_count = cursor.fetchone()['pick_count']
        
        if pick_count < 14:
            missing = 14 - pick_count
            users_missing_picks.append((user['id'], user['username'], pick_count, missing))
            status = f"❌ MISSING {missing} picks"
        else:
            status = "✅ Complete"
        
        print(f"  {user['username']:12} ({user['id']:2}): {pick_count:2}/14 picks - {status}")
    
    print(f"\n" + "=" * 50)
    print(f"SUMMARY: {len(users_missing_picks)} users need picks restored")
    
    for user_id, username, current, missing in users_missing_picks:
        print(f"  {username}: needs {missing} more picks")
    
    conn.close()
    return users_missing_picks

def restore_all_users_week9_picks():
    """Restore Week 9 picks for all users based on original data"""
    print("\n" + "=" * 70)
    print("RESTORING WEEK 9 PICKS FOR ALL USERS")
    print("=" * 70)
    
    # Original Week 9 picks data provided by user
    week9_picks_data = {
        'jean': [
            ('Baltimore Ravens @ Miami Dolphins', 'Miami Dolphins'),
            ('Chicago Bears @ Cincinnati Bengals', 'Cincinnati Bengals'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Jacksonville Jaguars'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'kristian': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Minnesota Vikings'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Jacksonville Jaguars'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'vizca': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Minnesota Vikings'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Tennessee Titans'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Jacksonville Jaguars'),
            ('New Orleans Saints @ Los Angeles Rams', 'Los Angeles Rams'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'fer': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'javier': [
            ('Baltimore Ravens @ Miami Dolphins', 'Miami Dolphins'),
            ('Chicago Bears @ Cincinnati Bengals', 'Cincinnati Bengals'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Jacksonville Jaguars'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Washington Commanders'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'robert': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'shorty': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Cincinnati Bengals'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Jacksonville Jaguars'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Washington Commanders'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'rada': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'ramfis': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'coyote': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'joniel': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'guillermo': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'raymond': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ],
        'mikitin': [
            ('Baltimore Ravens @ Miami Dolphins', 'Baltimore Ravens'),
            ('Chicago Bears @ Cincinnati Bengals', 'Chicago Bears'),
            ('Minnesota Vikings @ Detroit Lions', 'Detroit Lions'),
            ('Carolina Panthers @ Green Bay Packers', 'Green Bay Packers'),
            ('Los Angeles Chargers @ Tennessee Titans', 'Los Angeles Chargers'),
            ('Atlanta Falcons @ New England Patriots', 'Atlanta Falcons'),
            ('San Francisco 49ers @ New York Giants', 'San Francisco 49ers'),
            ('Indianapolis Colts @ Pittsburgh Steelers', 'Pittsburgh Steelers'),
            ('Denver Broncos @ Houston Texans', 'Denver Broncos'),
            ('Jacksonville Jaguars @ Las Vegas Raiders', 'Las Vegas Raiders'),
            ('New Orleans Saints @ Los Angeles Rams', 'New Orleans Saints'),
            ('Kansas City Chiefs @ Buffalo Bills', 'Kansas City Chiefs'),
            ('Seattle Seahawks @ Washington Commanders', 'Seattle Seahawks'),
            ('Arizona Cardinals @ Dallas Cowboys', 'Dallas Cowboys')
        ]
    }
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get game mapping
    cursor.execute("""
        SELECT id, away_team, home_team 
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    week9_games = cursor.fetchall()
    
    game_mapping = {}
    for game in week9_games:
        matchup = f"{game[1]} @ {game[2]}"  # away_team @ home_team
        game_mapping[matchup] = game[0]  # game id
    
    # Get all users
    cursor.execute("SELECT id, username FROM users WHERE NOT is_admin")
    all_users = cursor.fetchall()
    user_mapping = {user[1]: user[0] for user in all_users}
    
    total_picks_added = 0
    users_processed = 0
    
    for username, picks in week9_picks_data.items():
        if username not in user_mapping:
            print(f"❌ User '{username}' not found in database, skipping...")
            continue
        
        user_id = user_mapping[username]
        print(f"\n📝 Processing {username} (ID: {user_id}):")
        
        # Check existing picks
        cursor.execute("""
            SELECT g.id
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = 9 AND g.year = 2025
        """, (user_id,))
        
        existing_game_ids = set(row[0] for row in cursor.fetchall())
        
        picks_added_for_user = 0
        
        for matchup, selected_team in picks:
            if matchup in game_mapping:
                game_id = game_mapping[matchup]
                
                # Skip if pick already exists
                if game_id in existing_game_ids:
                    print(f"  ⏭️  {matchup} -> {selected_team} (already exists)")
                    continue
                
                # Insert the pick
                try:
                    cursor.execute("""
                        INSERT INTO user_picks (user_id, game_id, selected_team, is_correct, points_earned)
                        VALUES (?, ?, ?, 0, 0)
                    """, (user_id, game_id, selected_team))
                    
                    picks_added_for_user += 1
                    print(f"  ✅ Added: {matchup} -> {selected_team}")
                    
                except Exception as e:
                    print(f"  ❌ Error adding: {matchup} -> {e}")
            else:
                print(f"  ❌ No game found for: {matchup}")
        
        total_picks_added += picks_added_for_user
        users_processed += 1
        print(f"  📊 Added {picks_added_for_user} picks for {username}")
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print(f"\n" + "=" * 70)
    print("BULK RESTORE COMPLETE")
    print("=" * 70)
    print(f"✅ Processed {users_processed} users")
    print(f"✅ Added {total_picks_added} picks total")
    print(f"✅ All users should now have complete Week 9 picks!")

if __name__ == "__main__":
    # First check status
    users_missing = check_all_users_week9_status()
    
    if users_missing:
        print(f"\n🔧 {len(users_missing)} users need picks restored...")
        restore_all_users_week9_picks()
    else:
        print("\n✅ All users already have complete Week 9 picks!")