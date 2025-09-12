import sqlite3

# This is a test update to mark the WSH @ GB game as final
# You mentioned it was completed yesterday, so let's mark it as final
# with some example scores to test the leaderboard

conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== Updating WSH @ GB Game to Final ===')

# First, show current status
cursor.execute('''
    SELECT id, away_team, home_team, game_date, is_final, home_score, away_score
    FROM nfl_games 
    WHERE (away_team = 'WSH' AND home_team = 'GB') OR (away_team = 'GB' AND home_team = 'WSH')
    AND week = 2 AND year = 2025
''')

game = cursor.fetchone()
if game:
    game_id, away_team, home_team, game_date, is_final, home_score, away_score = game
    print(f'Found game: {away_team} @ {home_team} - {game_date}')
    print(f'Current status: {"FINAL" if is_final else "NOT FINAL"}')
    print(f'Current scores: {away_team} {away_score or "?"} - {home_team} {home_score or "?"}')
    
    # Ask for confirmation before updating
    print('\n!!! WARNING !!!')
    print('This will mark the game as FINAL with example scores.')
    print('You should replace this with actual game scores from the real game.')
    print('Example scores will be: WSH 24 - GB 21')
    
    response = input('\nDo you want to proceed? (y/N): ')
    if response.lower() == 'y':
        # Update with example scores (WSH wins 24-21)
        cursor.execute('''
            UPDATE nfl_games 
            SET is_final = 1, away_score = 24, home_score = 21
            WHERE id = ?
        ''', (game_id,))
        
        conn.commit()
        print('✅ Game updated as FINAL with example scores!')
        print('✅ Weekly leaderboard should now show for Week 2')
        
        # Now update user picks to mark them as correct/incorrect
        print('\n=== Updating Pick Results ===')
        cursor.execute('''
            UPDATE user_picks 
            SET is_correct = CASE 
                WHEN selected_team = 'WSH' THEN 1  -- WSH won in our example
                WHEN selected_team = 'GB' THEN 0   -- GB lost in our example
                ELSE is_correct  -- Keep existing value if no selection
            END
            WHERE game_id = ?
        ''', (game_id,))
        
        affected_picks = cursor.rowcount
        conn.commit()
        print(f'✅ Updated {affected_picks} user picks with correct/incorrect results')
        
        print('\n=== Final Status ===')
        cursor.execute('''
            SELECT away_team, home_team, is_final, away_score, home_score
            FROM nfl_games WHERE id = ?
        ''', (game_id,))
        
        final_game = cursor.fetchone()
        away, home, final, away_sc, home_sc = final_game
        print(f'Game: {away} {away_sc} @ {home} {home_sc} - {"FINAL" if final else "NOT FINAL"}')
        
    else:
        print('Update cancelled.')
        
else:
    print('❌ WSH @ GB game not found in Week 2')

conn.close()
