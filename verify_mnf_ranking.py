#!/usr/bin/env python3
"""
Verify the exact Monday Night predictions and correct ranking
"""

import sqlite3

def verify_mnf_ranking():
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Monday Night game
    cursor.execute('SELECT * FROM nfl_games WHERE week = 1 AND year = 2025 AND is_monday_night = 1')
    mnf_game = cursor.fetchone()
    
    print(f"Actual Game: {mnf_game['away_team']} {mnf_game['away_score']} - {mnf_game['home_team']} {mnf_game['home_score']}")
    print(f"Format: AWAY (MIN) @ HOME (CHI)")
    
    # Get predictions for coyote, raymond, and vizca
    cursor.execute('''
        SELECT u.username, p.selected_team, p.predicted_away_score, p.predicted_home_score
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = 1 AND g.year = 2025 AND g.is_monday_night = 1
        AND u.username IN ('coyote', 'raymond', 'vizca')
        ORDER BY u.username
    ''')
    
    picks = cursor.fetchall()
    print("\n=== EXACT PREDICTIONS ===")
    
    for pick in picks:
        away_actual = mnf_game['away_score']  # MIN 27
        home_actual = mnf_game['home_score']  # CHI 24
        
        away_diff = abs(pick['predicted_away_score'] - away_actual)
        home_diff = abs(pick['predicted_home_score'] - home_actual)
        total_diff = abs((pick['predicted_away_score'] + pick['predicted_home_score']) - (away_actual + home_actual))
        
        print(f"{pick['username']}:")
        print(f"  Selected: {pick['selected_team']} ({'✅' if pick['selected_team'] == 'MIN' else '❌'})")
        print(f"  Predicted: MIN {pick['predicted_away_score']} - CHI {pick['predicted_home_score']}")
        print(f"  Differences: Away±{away_diff}, Home±{home_diff}, Total±{total_diff}")
        print()
    
    print("=== CORRECT RANKING SHOULD BE ===")
    print("1. Most correct picks (all have 13)")
    print("2. Correct MNF winner (all picked MIN ✅)")
    print("3. Closest to home team (CHI 24)")
    print("4. If tied on home, closest to away team (MIN 27)")
    print("5. If tied on away, closest to total")
    
    # Check if coyote and raymond both predicted CHI 21
    coyote_pick = next(p for p in picks if p['username'] == 'coyote')
    raymond_pick = next(p for p in picks if p['username'] == 'raymond')
    
    if coyote_pick['predicted_home_score'] == raymond_pick['predicted_home_score']:
        print(f"\n✅ CONFIRMED: Both predicted CHI {coyote_pick['predicted_home_score']}")
        coyote_away_diff = abs(coyote_pick['predicted_away_score'] - 27)
        raymond_away_diff = abs(raymond_pick['predicted_away_score'] - 27)
        print(f"Away team tiebreaker: coyote ±{coyote_away_diff} vs raymond ±{raymond_away_diff}")
        
        if coyote_away_diff < raymond_away_diff:
            print("🏆 COYOTE SHOULD RANK HIGHER THAN RAYMOND!")
    
    conn.close()

if __name__ == "__main__":
    verify_mnf_ranking()
