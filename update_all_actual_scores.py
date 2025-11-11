#!/usr/bin/env python3

import sqlite3

def update_all_week9_actual_scores():
    """Update all Week 9 games with the actual final scores provided"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print('🏈 UPDATING ALL WEEK 9 SCORES WITH ACTUAL RESULTS')
    print('=' * 55)
    
    # Actual final scores from the data provided
    actual_scores = {
        ('Baltimore Ravens', 'Miami Dolphins'): (28, 6),           # Ravens won
        ('Denver Broncos', 'Houston Texans'): (18, 15),           # Broncos won
        ('Indianapolis Colts', 'Pittsburgh Steelers'): (20, 27),  # Steelers won
        ('San Francisco 49ers', 'New York Giants'): (34, 24),     # 49ers won
        ('Atlanta Falcons', 'New England Patriots'): (23, 24),    # Patriots won
        ('Los Angeles Chargers', 'Tennessee Titans'): (27, 20),   # Chargers won
        ('Carolina Panthers', 'Green Bay Packers'): (16, 13),     # Panthers won
        ('Minnesota Vikings', 'Detroit Lions'): (27, 24),         # Vikings won
        ('Chicago Bears', 'Cincinnati Bengals'): (47, 42),        # Bears won
        ('New Orleans Saints', 'Los Angeles Rams'): (10, 34),     # Rams won
        ('Jacksonville Jaguars', 'Las Vegas Raiders'): (30, 29),  # Jaguars won (OT)
        ('Kansas City Chiefs', 'Buffalo Bills'): (21, 28),        # Bills won
        ('Seattle Seahawks', 'Washington Commanders'): (38, 14),  # Seahawks won
        ('Arizona Cardinals', 'Dallas Cowboys'): (27, 17)         # Cardinals won
    }
    
    print('Updating game scores...')
    
    # Update each game with correct scores
    for (away_team, home_team), (away_score, home_score) in actual_scores.items():
        cursor.execute("""
            UPDATE nfl_games 
            SET away_score = ?, home_score = ?, game_status = 'Final', is_final = 1
            WHERE away_team = ? AND home_team = ? AND week = 9
        """, (away_score, home_score, away_team, home_team))
        
        winner = away_team if away_score > home_score else home_team
        print(f'✅ {away_team} {away_score} - {home_team} {home_score} (Winner: {winner})')
    
    conn.commit()
    
    # Recalculate ALL pick correctness for Week 9
    print('\n🔄 Recalculating all pick correctness...')
    
    cursor.execute("""
        SELECT 
            up.id,
            up.selected_team,
            ng.home_team,
            ng.away_team,
            ng.home_score,
            ng.away_score
        FROM user_picks up
        JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE ng.week = 9
    """)
    
    all_picks = cursor.fetchall()
    
    for pick_id, selected_team, home_team, away_team, home_score, away_score in all_picks:
        # Determine winner
        winner = away_team if away_score > home_score else home_team
        
        # Check if pick is correct
        is_correct = 1 if selected_team == winner else 0
        
        # Update pick correctness
        cursor.execute("""
            UPDATE user_picks 
            SET is_correct = ?
            WHERE id = ?
        """, (is_correct, pick_id))
    
    conn.commit()
    
    # Generate final corrected leaderboard
    cursor.execute("""
        SELECT 
            u.username,
            COUNT(CASE WHEN up.is_correct = 1 THEN 1 END) as correct_picks
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE ng.week = 9
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, u.username
    """)
    
    leaderboard = cursor.fetchall()
    
    print('\n🏆 FINAL CORRECTED WEEK 9 LEADERBOARD')
    print('=' * 40)
    
    for i, (username, correct) in enumerate(leaderboard, 1):
        print(f'{i:2d}. {username.upper():10s}: {correct:2d}/14')
    
    # Check specific users - VIZCA, JEAN, RADA
    print('\n🎯 KEY PLAYERS BEFORE/AFTER MNF:')
    print('=' * 35)
    
    for username in ['VIZCA', 'JEAN', 'RADA']:
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE UPPER(username) = UPPER(?)", (username,))
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
            
            # Before MNF (excluding Cardinals vs Cowboys)
            cursor.execute("""
                SELECT COUNT(CASE WHEN up.is_correct = 1 THEN 1 END)
                FROM user_picks up
                JOIN nfl_games ng ON up.game_id = ng.game_id
                WHERE up.user_id = ? AND ng.week = 9 
                AND NOT (ng.home_team = 'Dallas Cowboys' AND ng.away_team = 'Arizona Cardinals')
            """, (user_id,))
            
            before_mnf = cursor.fetchone()[0]
            
            # MNF pick and result
            cursor.execute("""
                SELECT up.selected_team, up.is_correct
                FROM user_picks up
                JOIN nfl_games ng ON up.game_id = ng.game_id
                WHERE up.user_id = ? AND ng.home_team = 'Dallas Cowboys' AND ng.week = 9
            """, (user_id,))
            
            mnf_result = cursor.fetchone()
            if mnf_result:
                mnf_pick, mnf_correct = mnf_result
                total_score = before_mnf + (1 if mnf_correct else 0)
                
                print(f'{username}:')
                print(f'  Before MNF: {before_mnf}/13')
                print(f'  MNF pick: {mnf_pick} - {"WON" if mnf_correct else "LOST"}')
                print(f'  Final: {total_score}/14')
                print()
    
    print('✅ All Week 9 scores updated with actual NFL results!')
    
    conn.close()

if __name__ == '__main__':
    update_all_week9_actual_scores()