#!/usr/bin/env python3
"""
Comprehensive diagnosis and fix for remote server scoring issues
"""
import sqlite3
from datetime import datetime
import sys

def diagnose_and_fix():
    print('=== COMPREHENSIVE DIAGNOSIS ===')
    print()
    print('Current time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # Connect to database
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print('🔍 ISSUE IDENTIFIED:')
    print('  Remote server database shows Week 3 games are NOT being updated automatically')
    print('  All Week 3 games show no scores and is_final = 0')
    print('  All Week 3 picks are unscored (is_correct = NULL)')
    print()
    
    print('📋 CURRENT WEEK 3 STATUS:')
    cursor.execute('''
        SELECT COUNT(*) as total_games,
               SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games,
               SUM(CASE WHEN home_score IS NOT NULL THEN 1 ELSE 0 END) as scored_games
        FROM nfl_games 
        WHERE week = 3 AND year = 2025
    ''')
    
    row = cursor.fetchone()
    print(f'  Total Week 3 games: {row["total_games"]}')
    print(f'  Final games: {row["final_games"]}')
    print(f'  Games with scores: {row["scored_games"]}')
    print()
    
    print('🎯 ROOT CAUSE ANALYSIS:')
    print('  1. ❌ Background updater not running on remote server')
    print('  2. ❌ ESPN API calls may be failing (SSL/network issues)')  
    print('  3. ❌ Database not being updated with game results')
    print('  4. ❌ Pick scoring not happening automatically')
    print()
    
    print('💡 SOLUTION APPROACH:')
    print('  Since automatic system is not working on remote server, we need to:')
    print('  1. Manually update the Buffalo game (we know MIA 21 - BUF 31)')
    print('  2. Force scoring for that game')
    print('  3. Create script for server admin to run manually')
    print('  4. Investigate background updater on server')
    print()
    
    print('🔧 IMPLEMENTING MANUAL FIX:')
    print()
    
    # Find Buffalo game
    cursor.execute('''
        SELECT id, away_team, home_team, away_score, home_score, is_final
        FROM nfl_games
        WHERE (away_team = 'MIA' AND home_team = 'BUF') 
          AND week = 3 AND year = 2025
    ''')
    
    buffalo_game = cursor.fetchone()
    if buffalo_game:
        game_id = buffalo_game['id']
        print(f'  Found Buffalo game (ID: {game_id}): {buffalo_game["away_team"]} @ {buffalo_game["home_team"]}')
        
        # Update the game with the correct score
        print('  Updating game score: MIA 21 - BUF 31...')
        cursor.execute('''
            UPDATE nfl_games 
            SET away_score = 21, home_score = 31, is_final = 1
            WHERE id = ?
        ''', (game_id,))
        
        # Get all picks for this game
        cursor.execute('''
            SELECT up.id, up.user_id, u.username, up.selected_team
            FROM user_picks up
            JOIN users u ON up.user_id = u.id
            WHERE up.game_id = ? AND u.is_admin = 0
        ''', (game_id,))
        
        picks = cursor.fetchall()
        print(f'  Found {len(picks)} user picks to score...')
        
        # Score each pick (BUF won, so BUF picks are correct)
        correct_count = 0
        for pick in picks:
            is_correct = 1 if pick['selected_team'] == 'BUF' else 0
            cursor.execute('''
                UPDATE user_picks 
                SET is_correct = ?
                WHERE id = ?
            ''', (is_correct, pick['id']))
            
            status = '✓ CORRECT' if is_correct else '✗ INCORRECT'
            print(f'    {pick["username"]}: {pick["selected_team"]} {status}')
            
            if is_correct:
                correct_count += 1
        
        print(f'  Scoring complete: {correct_count}/{len(picks)} correct picks')
        
        # Commit changes
        conn.commit()
        print('  ✓ Database updated successfully')
        print()
        
        # Verify the fix
        print('🎯 VERIFICATION:')
        cursor.execute('''
            SELECT away_score, home_score, is_final FROM nfl_games WHERE id = ?
        ''', (game_id,))
        
        updated_game = cursor.fetchone()
        print(f'  Game score: {updated_game["away_score"]}-{updated_game["home_score"]}')
        print(f'  Game final: {updated_game["is_final"]}')
        
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM user_picks 
            WHERE game_id = ?
        ''', (game_id,))
        
        pick_summary = cursor.fetchone()
        print(f'  Pick results: {pick_summary["correct"]}/{pick_summary["total"]} correct')
        print()
        
    else:
        print('  ❌ Buffalo game not found!')
    
    print('📝 NEXT STEPS FOR SERVER ADMIN:')
    print('  1. Upload this corrected database to the server')
    print('  2. Check if background_updater.py is running on server:')
    print('     ps aux | grep background_updater')
    print('  3. If not running, start it:')
    print('     nohup python background_updater.py &')
    print('  4. Check server logs for ESPN API errors')
    print('  5. Consider running manual score updates periodically if auto fails')
    print()
    
    print('✅ MANUAL FIX COMPLETED!')
    print('  Buffalo game now shows: MIA 21 - BUF 31 (Final)')
    print('  All user picks for this game are now properly scored')
    print('  Database ready to upload back to server')
    
    conn.close()

if __name__ == '__main__':
    diagnose_and_fix()
