#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def update_actual_game_score():
    """Update the actual Green Bay vs Washington game score"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🏈 Updating Actual Game Score: Green Bay 27, Washington 18")
    print("=" * 50)
    
    # Find the WSH @ GB game
    cursor.execute('''
        SELECT id, away_team, home_team, game_date, home_score, away_score, is_final
        FROM nfl_games 
        WHERE week = 2 AND year = 2025 
        AND away_team = 'WSH' AND home_team = 'GB'
    ''')
    
    game = cursor.fetchone()
    
    if game:
        print(f"Found game: {game['away_team']} @ {game['home_team']}")
        print(f"Current status: Final={game['is_final']}, Score={game['away_score']}-{game['home_score']}")
        
        # Update with actual scores: Green Bay 27, Washington 18
        cursor.execute('''
            UPDATE nfl_games 
            SET home_score = 27, away_score = 18, is_final = 1
            WHERE id = ?
        ''', (game['id'],))
        
        print("✅ Updated to actual scores: Washington 18, Green Bay 27")
        
        # Update pick correctness for all users
        cursor.execute('''
            SELECT up.id, u.username, up.selected_team
            FROM user_picks up
            JOIN users u ON up.user_id = u.id
            WHERE up.game_id = ?
        ''', (game['id'],))
        
        picks = cursor.fetchall()
        
        print(f"\n📊 Updating {len(picks)} user picks:")
        
        for pick in picks:
            # Green Bay won (27 > 18), so correct picks are those who selected 'GB'
            is_correct = 1 if pick['selected_team'] == 'GB' else 0
            
            cursor.execute('''
                UPDATE user_picks 
                SET is_correct = ?
                WHERE id = ?
            ''', (is_correct, pick['id']))
            
            result = "✅ CORRECT" if is_correct else "❌ WRONG"
            print(f"  {pick['username']}: picked {pick['selected_team']} → {result}")
        
        conn.commit()
        print("\n🎉 Game updated with actual scores!")
        
    else:
        print("❌ Game not found!")
    
    conn.close()

if __name__ == '__main__':
    update_actual_game_score()
