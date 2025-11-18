#!/usr/bin/env python3

import sqlite3

def check_vizca_picks():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Check the schema of user_picks table
    cursor.execute('PRAGMA table_info(user_picks)')
    columns = cursor.fetchall()
    print('User Picks Table Schema:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    print()
    
    # Check VIZCA's picks (user_id = 9)
    cursor.execute('SELECT * FROM user_picks WHERE user_id = 9 LIMIT 5')
    sample_picks = cursor.fetchall()
    print('Sample VIZCA picks:')
    for pick in sample_picks:
        print(pick)
    
    print()
    
    # Get all VIZCA Week 9 picks
    cursor.execute('''
        SELECT 
            up.*,
            ng.home_team,
            ng.away_team,
            ng.home_score,
            ng.away_score
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE up.user_id = 9 AND ng.week = 9
        ORDER BY ng.game_id
    ''')
    
    picks = cursor.fetchall()
    print(f'VIZCA Week 9 Picks ({len(picks)} total):')
    print('=' * 60)
    
    correct_count = 0
    for pick in picks:
        game_id = pick[2]  # game_id column
        team_picked = pick[3]  # selected_team column
        home_team = pick[17]  # home_team from join
        away_team = pick[18]  # away_team from join  
        home_score = pick[19]  # home_score from join
        away_score = pick[20]  # away_score from join
        
        # Determine winner
        if home_score is not None and away_score is not None:
            winner = home_team if home_score > away_score else away_team
            is_correct = team_picked == winner
            if is_correct:
                correct_count += 1
            
            print(f'Game {game_id}: {away_team} @ {home_team} ({away_score}-{home_score})')
            print(f'  VIZCA picked: {team_picked}')
            print(f'  Winner: {winner} - {"CORRECT" if is_correct else "WRONG"}')
            
            # Special check for Cowboys vs Cardinals
            if home_team == 'Dallas Cowboys' and away_team == 'Arizona Cardinals':
                print(f'  🏈 MONDAY NIGHT FOOTBALL - Cardinals won 30-26')
                if team_picked == 'Arizona Cardinals':
                    print(f'  ✅ VIZCA correctly picked Arizona!')
                else:
                    print(f'  ❌ VIZCA picked {team_picked}, Cardinals won')
            print()
    
    print(f'VIZCA Total Correct: {correct_count}/14')
    
    conn.close()

if __name__ == '__main__':
    check_vizca_picks()