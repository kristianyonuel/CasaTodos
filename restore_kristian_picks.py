#!/usr/bin/env python3
"""
Restore KRISTIAN's missing Week 9 picks
"""

import sqlite3

def restore_kristian_week9_picks():
    """Restore KRISTIAN's missing Week 9 picks"""
    print("=" * 60)
    print("RESTORING KRISTIAN'S WEEK 9 PICKS")
    print("=" * 60)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # KRISTIAN's picks based on the original data provided by user
    kristian_picks = [
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
    ]
    
    # Get KRISTIAN's user ID
    cursor.execute("SELECT id FROM users WHERE username = 'kristian'")
    kristian_id = cursor.fetchone()[0]
    print(f"KRISTIAN's user ID: {kristian_id}")
    
    # Get Week 9 games with their IDs
    cursor.execute("""
        SELECT id, away_team, home_team 
        FROM nfl_games 
        WHERE week = 9 AND year = 2025
        ORDER BY game_date
    """)
    week9_games = cursor.fetchall()
    
    print(f"\nFound {len(week9_games)} Week 9 games")
    
    # Create a mapping of game matchups to game IDs
    game_mapping = {}
    for game in week9_games:
        matchup = f"{game[1]} @ {game[2]}"  # away_team @ home_team
        game_mapping[matchup] = game[0]  # game id
        print(f"  Game {game[0]}: {matchup}")
    
    print(f"\n1. Checking KRISTIAN's current Week 9 picks:")
    cursor.execute("""
        SELECT g.id, g.away_team, g.home_team, up.selected_team
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND g.week = 9 AND g.year = 2025
    """, (kristian_id,))
    
    existing_picks = cursor.fetchall()
    existing_game_ids = set()
    
    for pick in existing_picks:
        existing_game_ids.add(pick[0])
        print(f"  ✅ Game {pick[0]}: {pick[1]} @ {pick[2]} -> {pick[3]}")
    
    print(f"\n2. Adding missing picks for KRISTIAN:")
    picks_added = 0
    
    for matchup, selected_team in kristian_picks:
        if matchup in game_mapping:
            game_id = game_mapping[matchup]
            
            # Skip if pick already exists
            if game_id in existing_game_ids:
                print(f"  ⏭️  Game {game_id}: {matchup} -> {selected_team} (already exists)")
                continue
            
            # Insert the pick
            try:
                cursor.execute("""
                    INSERT INTO user_picks (user_id, game_id, selected_team, is_correct, points_earned)
                    VALUES (?, ?, ?, 0, 0)
                """, (kristian_id, game_id, selected_team))
                
                picks_added += 1
                print(f"  ✅ Added Game {game_id}: {matchup} -> {selected_team}")
                
            except Exception as e:
                print(f"  ❌ Error adding Game {game_id}: {matchup} -> {e}")
        else:
            print(f"  ❌ No game found for: {matchup}")
    
    # Commit the changes
    conn.commit()
    
    print(f"\n3. Verification - KRISTIAN's Week 9 picks after restore:")
    cursor.execute("""
        SELECT 
            g.id,
            g.away_team,
            g.home_team,
            up.selected_team,
            up.id as pick_id
        FROM user_picks up
        JOIN nfl_games g ON up.game_id = g.id
        WHERE up.user_id = ? AND g.week = 9 AND g.year = 2025
        ORDER BY g.game_date
    """, (kristian_id,))
    
    final_picks = cursor.fetchall()
    print(f"KRISTIAN now has {len(final_picks)}/14 picks for Week 9:")
    
    for pick in final_picks:
        print(f"  Pick {pick[4]}: Game {pick[0]} - {pick[1]} @ {pick[2]} -> {pick[3]}")
    
    conn.close()
    
    print(f"\n" + "=" * 60)
    print("RESTORE COMPLETE")
    print("=" * 60)
    print(f"Added {picks_added} picks for KRISTIAN")
    print(f"KRISTIAN now has {len(final_picks)}/14 picks for Week 9")
    print(f"Admin interface should now show all {len(final_picks)} picks!")

if __name__ == "__main__":
    restore_kristian_week9_picks()