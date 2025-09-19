#!/usr/bin/env python3
"""
Quick script to check Buffalo game scoring issue
"""
import sqlite3

def check_buffalo_game():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== BUFFALO GAME ANALYSIS ===")
    
    # Check the Buffalo game details
    cursor.execute('SELECT id, game_id, away_team, home_team, away_score, home_score, is_final FROM nfl_games WHERE id = 167')
    game = cursor.fetchone()
    
    if game:
        print(f'Game 167: {game}')
        print(f'  Game ID: {game[1]}')
        print(f'  Matchup: {game[2]} @ {game[3]}')
        print(f'  Score: {game[2]} {game[4]} - {game[5]} {game[3]}')
        print(f'  Final: {game[6]}')
        
        # Determine the actual winner
        away_team, home_team, away_score, home_score = game[2], game[3], game[4], game[5]
        if home_score > away_score:
            actual_winner = home_team
        elif away_score > home_score:
            actual_winner = away_team
        else:
            actual_winner = "TIE"
        
        print(f'  Actual Winner: {actual_winner}')
    else:
        print('Game 167 not found!')
        return
    
    print("\n=== USER PICKS FOR GAME 167 ===")
    
    # Check all user picks for this game
    cursor.execute('''
        SELECT up.user_id, u.username, up.selected_team, up.is_correct 
        FROM user_picks up
        JOIN users u ON up.user_id = u.id
        WHERE up.game_id = 167
        ORDER BY u.username
    ''')
    picks = cursor.fetchall()
    
    print(f'Total picks for game 167: {len(picks)}')
    
    for pick in picks:
        user_id, username, selected_team, is_correct = pick
        # Check if their pick matches the actual winner
        should_be_correct = (selected_team == actual_winner)
        status = "✓" if is_correct == 1 else "✗" if is_correct == 0 else "?"
        
        print(f'  {username}: picked {selected_team}, marked {status} (is_correct={is_correct})')
        
        if should_be_correct and is_correct != 1:
            print(f'    ❌ ERROR: Should be CORRECT but marked as {is_correct}')
        elif not should_be_correct and is_correct == 1:
            print(f'    ❌ ERROR: Should be INCORRECT but marked as {is_correct}')
        elif should_be_correct and is_correct == 1:
            print(f'    ✅ CORRECT: Properly marked')
        else:
            print(f'    ✅ INCORRECT: Properly marked')
    
    print(f'\n=== SUMMARY ===')
    print(f'Game: {away_team} {away_score} - {home_score} {home_team}')
    print(f'Winner: {actual_winner}')
    
    # Count correct/incorrect picks
    correct_count = len([p for p in picks if p[3] == 1])
    incorrect_count = len([p for p in picks if p[3] == 0])
    unknown_count = len([p for p in picks if p[3] is None])
    
    print(f'Picks marked correct: {correct_count}')
    print(f'Picks marked incorrect: {incorrect_count}')
    print(f'Picks unmarked: {unknown_count}')
    
    # Check if everyone who picked the winner is marked correct
    winner_picks = [p for p in picks if p[2] == actual_winner]
    loser_picks = [p for p in picks if p[2] != actual_winner]
    
    print(f'Users who picked {actual_winner}: {len(winner_picks)}')
    print(f'Users who picked wrong: {len(loser_picks)}')
    
    conn.close()

if __name__ == '__main__':
    check_buffalo_game()
