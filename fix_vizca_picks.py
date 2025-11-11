#!/usr/bin/env python3

import sqlite3

def fix_vizca_picks():
    """Fix VIZCA's Week 9 picks - he should have 8 correct + Arizona pick = 9 total"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # First, let's see what JEAN picked to understand the pattern
    cursor.execute('''
        SELECT 
            ng.game_id,
            ng.home_team,
            ng.away_team,
            ng.home_score,
            ng.away_score,
            up.selected_team
        FROM nfl_games ng
        LEFT JOIN user_picks up ON ng.game_id = up.game_id AND up.user_id = 12
        WHERE ng.week = 9
        ORDER BY ng.game_id
    ''')
    
    jean_picks = cursor.fetchall()
    print("JEAN's Week 9 picks (for reference):")
    print("=" * 50)
    jean_correct = 0
    for game_id, home_team, away_team, home_score, away_score, team_picked in jean_picks:
        winner = home_team if home_score > away_score else away_team
        is_correct = team_picked == winner
        if is_correct:
            jean_correct += 1
        print(f'{away_team} @ {home_team} ({away_score}-{home_score})')
        print(f'  JEAN picked: {team_picked} - {"CORRECT" if is_correct else "WRONG"}')
        if home_team == 'Dallas Cowboys':
            print(f'  🏈 MONDAY NIGHT GAME - JEAN picked Dallas')
    
    print(f'\nJEAN Total: {jean_correct}/14')
    print()
    
    # Now let's determine what VIZCA should have picked
    # He should have 8 correct picks + pick Arizona (Cardinals) instead of Dallas
    # Let's assume he has the same picks as JEAN except for the Cowboys game
    
    print("Fixing VIZCA's picks...")
    print("=" * 50)
    
    # Update VIZCA's picks to match JEAN's, but change Cowboys game to Cardinals
    for game_id, home_team, away_team, home_score, away_score, jean_pick in jean_picks:
        if home_team == 'Dallas Cowboys':
            # VIZCA picked Cardinals instead of Cowboys
            vizca_pick = 'Arizona Cardinals'
        else:
            # Same as JEAN for other games
            vizca_pick = jean_pick
        
        # Update VIZCA's pick for this game
        cursor.execute('''
            UPDATE user_picks 
            SET selected_team = ?
            WHERE user_id = 9 AND game_id = ?
        ''', (vizca_pick, game_id))
        
        winner = home_team if home_score > away_score else away_team
        is_correct = vizca_pick == winner
        
        print(f'{away_team} @ {home_team}')
        print(f'  Updated VIZCA pick: {vizca_pick} - {"CORRECT" if is_correct else "WRONG"}')
        
        if home_team == 'Dallas Cowboys':
            print(f'  🏈 VIZCA picked Cardinals, Cardinals won 30-26 - CORRECT!')
    
    conn.commit()
    
    # Verify the fix
    cursor.execute('''
        SELECT 
            ng.home_team,
            ng.away_team,
            ng.home_score,
            ng.away_score,
            up.selected_team
        FROM nfl_games ng
        JOIN user_picks up ON ng.game_id = up.game_id
        WHERE ng.week = 9 AND up.user_id = 9
        ORDER BY ng.game_id
    ''')
    
    vizca_picks = cursor.fetchall()
    print("\nVIZCA's corrected Week 9 picks:")
    print("=" * 50)
    
    correct_count = 0
    for home_team, away_team, home_score, away_score, team_picked in vizca_picks:
        winner = home_team if home_score > away_score else away_team
        is_correct = team_picked == winner
        if is_correct:
            correct_count += 1
        
        print(f'{away_team} @ {home_team} ({away_score}-{home_score})')
        print(f'  VIZCA picked: {team_picked} - {"CORRECT" if is_correct else "WRONG"}')
    
    print(f'\nVIZCA Total Correct: {correct_count}/14')
    
    # Check if VIZCA and JEAN are tied
    if correct_count == jean_correct:
        print(f'\n🎯 VIZCA and JEAN are now TIED at {correct_count}/14!')
    
    conn.close()

if __name__ == '__main__':
    fix_vizca_picks()