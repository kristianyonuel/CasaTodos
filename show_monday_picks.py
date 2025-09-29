#!/usr/bin/env python3
"""
Show actual Week 4 Monday Night picks for winner prediction explanation
"""

import sqlite3

def show_actual_monday_picks():
    print("🏈 ACTUAL WEEK 4 MONDAY NIGHT PICKS")
    print("=" * 50)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get Monday games
    cursor.execute('''
        SELECT id, away_team, home_team 
        FROM nfl_games 
        WHERE week = 4 AND year = 2025 
        AND strftime('%w', game_date) = '1'
        ORDER BY game_date
    ''')
    
    monday_games = cursor.fetchall()
    
    for i, (game_id, away, home) in enumerate(monday_games, 1):
        print(f"\nGame {i}: {away} @ {home}")
        print("-" * 25)
        
        # Get picks for this game
        cursor.execute('''
            SELECT u.username, up.selected_team 
            FROM users u 
            JOIN user_picks up ON u.id = up.user_id 
            WHERE up.game_id = ? AND u.is_admin = 0 
            ORDER BY u.username
        ''', (game_id,))
        
        picks = cursor.fetchall()
        
        # Group by team
        team_picks = {}
        for username, pick in picks:
            if pick not in team_picks:
                team_picks[pick] = []
            team_picks[pick].append(username)
        
        for team, users in team_picks.items():
            user_list = ', '.join(users)
            print(f"  {team}: {user_list}")
    
    print("\n" + "=" * 50)
    print("🎯 WINNER PREDICTION SCENARIOS:")
    print()
    
    # Show how the prediction works with actual data
    if len(monday_games) >= 2:
        game1_away = monday_games[0][1]  # NYJ
        game1_home = monday_games[0][2]  # MIA
        game2_away = monday_games[1][1]  # CIN
        game2_home = monday_games[1][2]  # DEN
        
        print(f"If {game1_home} wins Game 1:")
        print(f"  → Users who picked {game1_home} get +1 win")
        print(f"  → Then Game 2 ({game2_away} @ {game2_home}) matters for tiebreakers")
        print()
        
        print(f"If {game1_away} wins Game 1:")
        print(f"  → Users who picked {game1_away} get +1 win")
        print(f"  → May clinch the week or set up Game 2 scenarios")
        print()
        
        print("MNF Score Tiebreaker (if needed):")
        print("  1️⃣ Closest to total points")
        print("  2️⃣ Closest to winner's score")
        print("  3️⃣ Closest to loser's score")
    
    conn.close()

if __name__ == "__main__":
    show_actual_monday_picks()