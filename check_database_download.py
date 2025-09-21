#!/usr/bin/env python3
"""
Check database status after downloading from server
"""
import sqlite3
from datetime import datetime

def check_database_status():
    print('=== DATABASE STATUS AFTER SERVER DOWNLOAD ===')
    print()
    
    # Connect to database
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print('Current time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Check what tables exist
    print('AVAILABLE TABLES:')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_names = [table['name'] for table in tables]
    for table in table_names:
        print(f'  - {table}')
    print()
    
    # Determine correct games table name
    games_table = None
    if 'nfl_games' in table_names:
        games_table = 'nfl_games'
    elif 'games' in table_names:
        games_table = 'games'
    else:
        print("❌ No games table found!")
        conn.close()
        return
    
    print(f"Using games table: {games_table}")
    print()
    
    # Check games status
    print('GAMES STATUS:')
    cursor.execute(f'''
        SELECT week, year, COUNT(*) as total_games,
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
               SUM(CASE WHEN home_score IS NOT NULL AND away_score IS NOT NULL THEN 1 ELSE 0 END) as games_with_scores
        FROM {games_table}
        WHERE year = 2025
        GROUP BY week, year
        ORDER BY week
    ''')
    
    for row in cursor.fetchall():
        print(f'  Week {row["week"]}: {row["total_games"]} games, {row["final_games"]} final, {row["games_with_scores"]} with scores')
    
    print()
    
    # Check specific games for Week 3
    print('WEEK 3 GAMES DETAIL:')
    cursor.execute(f'''
        SELECT away_team, home_team, away_score, home_score, is_final, game_date
        FROM {games_table}
        WHERE week = 3 AND year = 2025
        ORDER BY game_date
    ''')
    
    for row in cursor.fetchall():
        final_status = '✓ FINAL' if row['is_final'] else '⏳ PENDING'
        scores = f'{row["away_score"]}-{row["home_score"]}' if row['away_score'] is not None and row['home_score'] is not None else 'No Score'
        print(f'  {row["away_team"]} @ {row["home_team"]}: {scores} {final_status}')
    
    print()
    
    # Check picks status
    print('PICKS STATUS:')
    cursor.execute(f'''
        SELECT COUNT(*) as total_picks,
               SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
               SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as incorrect_picks,
               SUM(CASE WHEN is_correct IS NULL THEN 1 ELSE 0 END) as unscored_picks
        FROM user_picks up
        JOIN {games_table} g ON up.game_id = g.id
        WHERE g.week = 3 AND g.year = 2025
    ''')
    
    row = cursor.fetchone()
    print(f'  Total picks: {row["total_picks"]}')
    print(f'  Correct: {row["correct_picks"]}')
    print(f'  Incorrect: {row["incorrect_picks"]}')
    print(f'  Unscored: {row["unscored_picks"]}')
    
    print()
    
    # Check Buffalo game specifically
    print('BUFFALO GAME VERIFICATION:')
    cursor.execute(f'''
        SELECT away_team, home_team, away_score, home_score, is_final, id
        FROM {games_table}
        WHERE ((away_team = 'MIA' AND home_team = 'BUF') OR (away_team = 'BUF' AND home_team = 'MIA'))
          AND week = 3 AND year = 2025
    ''')
    
    buffalo_game = cursor.fetchone()
    if buffalo_game:
        print(f'  Game: {buffalo_game["away_team"]} @ {buffalo_game["home_team"]}')
        print(f'  Score: {buffalo_game["away_score"]}-{buffalo_game["home_score"]}')
        print(f'  Final: {buffalo_game["is_final"]}')
        
        # Check picks for this game
        cursor.execute('''
            SELECT u.username, up.selected_team, up.is_correct
            FROM user_picks up
            JOIN users u ON up.user_id = u.id
            WHERE up.game_id = ? AND u.is_admin = 0
            ORDER BY u.username
        ''', (buffalo_game["id"],))
        
        picks = cursor.fetchall()
        print(f'  User picks ({len(picks)} total):')
        for pick in picks:
            status = '✓' if pick['is_correct'] == 1 else '✗' if pick['is_correct'] == 0 else '?'
            print(f'    {pick["username"]}: {pick["selected_team"]} {status}')
    else:
        print('  Buffalo game not found!')
    
    print()
    
    # Check if background updater has been running
    print('RECENT UPDATE ACTIVITY:')
    try:
        cursor.execute(f'''
            SELECT MAX(game_date) as latest_game,
                   COUNT(*) as total_final_games
            FROM {games_table}
            WHERE is_final = 1 AND year = 2025
        ''')
        
        row = cursor.fetchone()
        print(f'  Total final games: {row["total_final_games"]}')
        print(f'  Latest final game: {row["latest_game"]}')
        
        # Check when picks were last updated
        cursor.execute('''
            SELECT MAX(created_at) as last_pick_update
            FROM user_picks
        ''')
        
        row = cursor.fetchone()
        print(f'  Last pick update: {row["last_pick_update"]}')
        
    except Exception as e:
        print(f'  Error checking update activity: {e}')
    
    conn.close()

if __name__ == '__main__':
    check_database_status()
