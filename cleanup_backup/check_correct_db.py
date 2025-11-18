#!/usr/bin/env python3
"""
Check the correct database for games and New England data
"""

import sqlite3

def check_correct_database():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== NFL_FANTASY.DB INVESTIGATION ===")
    
    # Check what weeks exist
    try:
        cursor.execute('SELECT DISTINCT week, year, COUNT(*) FROM nfl_games GROUP BY week, year ORDER BY year DESC, week DESC')
        weeks = cursor.fetchall()
        print('Available weeks:')
        for week, year, count in weeks:
            print(f'  Week {week}, {year}: {count} games')
    except Exception as e:
        print(f'Error checking weeks: {e}')
    
    print()
    print('=== WEEK 4 GAMES ===')
    try:
        cursor.execute('SELECT id, away_team, home_team, is_final, home_score, away_score FROM nfl_games WHERE week = 4 AND year = 2025 ORDER BY id')
        games = cursor.fetchall()
        
        if games:
            print(f'Found {len(games)} Week 4 games:')
            for game in games:
                game_id, away, home, is_final, h_score, a_score = game
                status = 'FINAL' if is_final else 'SCHEDULED'
                if is_final and h_score is not None:
                    score = f'{away} {a_score} - {h_score} {home}'
                else:
                    score = f'{away} @ {home} (TBD)'
                print(f'  {game_id}: {score} ({status})')
        else:
            print('No Week 4 games found')
    except Exception as e:
        print(f'Error: {e}')
    
    print()
    print('=== NEW ENGLAND GAMES ===')
    try:
        cursor.execute('SELECT week, year, id, away_team, home_team, is_final, home_score, away_score FROM nfl_games WHERE away_team = ? OR home_team = ? ORDER BY week, year', ('NE', 'NE'))
        ne_games = cursor.fetchall()
        
        if ne_games:
            print(f'Found {len(ne_games)} New England games:')
            for week, year, game_id, away, home, is_final, h_score, a_score in ne_games:
                status = 'FINAL' if is_final else 'SCHEDULED'
                if is_final and h_score is not None:
                    score = f'{away} {a_score} - {h_score} {home}'
                else:
                    score = f'{away} @ {home}'
                print(f'  Week {week}, {year}: {score} ({status})')
        else:
            print('No New England games found')
    except Exception as e:
        print(f'Error: {e}')
    
    # Check leaderboard availability for Week 4
    print()
    print('=== WEEK 4 LEADERBOARD ANALYSIS ===')
    try:
        cursor.execute('''
            SELECT COUNT(*) as total_games,
                   SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
                   SUM(CASE WHEN game_date < datetime('now') OR is_final = 1 THEN 1 ELSE 0 END) as available_games
            FROM nfl_games 
            WHERE week = 4 AND year = 2025
        ''')
        stats = cursor.fetchone()
        total, final, available = stats
        
        print(f'Total games: {total}')
        print(f'Final games: {final}')
        print(f'Available for leaderboard: {available}')
        print(f'Leaderboard should show: {"YES" if available > 0 else "NO"}')
        
        # Check user picks
        cursor.execute('''
            SELECT COUNT(*) as total_picks,
                   COUNT(DISTINCT u.username) as users_with_picks
            FROM user_picks p
            JOIN nfl_games g ON p.game_id = g.id
            JOIN users u ON p.user_id = u.id
            WHERE g.week = 4 AND g.year = 2025 AND u.is_admin = 0
        ''')
        picks_stats = cursor.fetchone()
        print(f'Total picks made: {picks_stats[0]}')
        print(f'Users with picks: {picks_stats[1]}')
        
    except Exception as e:
        print(f'Error in leaderboard analysis: {e}')
    
    conn.close()

if __name__ == "__main__":
    check_correct_database()