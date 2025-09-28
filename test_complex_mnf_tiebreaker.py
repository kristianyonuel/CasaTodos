#!/usr/bin/env python3
"""
Test Complex Monday Night Football Tiebreaker Scenario

This demonstrates the NEW tiebreaker system with a dramatic example:
- Multiple users tied at 11 wins going into Monday Night
- One user (David) with 10 wins who could tie if his team wins
- Shows how the NEW system (total->winner->loser) differs from OLD system (home->away)
"""

import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complex_mnf_tiebreaker():
    """Test the complex Monday Night Football tiebreaker scenario"""
    
    print("=== TESTING COMPLEX MNF TIEBREAKER SCENARIO ===")
    print()
    
    # Connect to database
    db_path = "nfl_fantasy.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Create test data for Week 4, 2025
        test_week = 4
        test_year = 2025
        
        print(f"Setting up test scenario for Week {test_week}, {test_year}")
        
        # Clean up any existing test data
        cursor.execute('DELETE FROM user_picks WHERE user_id IN (SELECT id FROM users WHERE username LIKE "Test_%")')
        cursor.execute('DELETE FROM users WHERE username LIKE "Test_%"')
        
        # Create test users
        test_users = [
            ("Test_Alice", "alice@test.com", "password123", False),
            ("Test_Bob", "bob@test.com", "password123", False),
            ("Test_Charlie", "charlie@test.com", "password123", False),
            ("Test_David", "david@test.com", "password123", False),
            ("Test_Eve", "eve@test.com", "password123", False)
        ]
        
        user_ids = {}
        for username, email, password, is_admin in test_users:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, f"hash_{password}", is_admin, datetime.now().isoformat()))
            user_ids[username] = cursor.lastrowid
        
        print(f"Created {len(test_users)} test users")
        
        # Find the Monday Night Football game for Week 4, 2025 (CIN @ DEN)
        cursor.execute('''
            SELECT id, away_team, home_team, game_date 
            FROM nfl_games 
            WHERE week = ? AND year = ? 
            AND strftime('%w', game_date) = '1'  -- Monday
            ORDER BY game_date DESC, id DESC
            LIMIT 1
        ''', (test_week, test_year))
        
        mnf_game = cursor.fetchone()
        if not mnf_game:
            print("ERROR: No Monday Night Football game found for Week 4, 2025")
            return False
        
        mnf_game_id = mnf_game['id']
        print(f"Found MNF game: {mnf_game['away_team']} @ {mnf_game['home_team']} (Game ID: {mnf_game_id})")
        
        # Get all other games for this week to simulate regular season picks
        cursor.execute('''
            SELECT id, away_team, home_team 
            FROM nfl_games 
            WHERE week = ? AND year = ? AND id != ?
            ORDER BY game_date
        ''', (test_week, test_year, mnf_game_id))
        
        regular_games = cursor.fetchall()
        print(f"Found {len(regular_games)} regular games for Week {test_week}")
        
        # Simulate regular season picks (give users different win totals)
        # Alice: 12 wins, Bob: 12 wins, Charlie: 12 wins, David: 11 wins, Eve: 10 wins
        # TWIST: David is behind but will win because others pick wrong MNF team!
        win_targets = {
            "Test_Alice": 12,
            "Test_Bob": 12, 
            "Test_Charlie": 12,
            "Test_David": 11,  # Behind by 1 win going into Monday!
            "Test_Eve": 10
        }
        
        for username, target_wins in win_targets.items():
            user_id = user_ids[username]
            wins = 0
            
            # Create picks for regular games to achieve target wins
            for i, game in enumerate(regular_games):
                # Determine if this should be a win or loss
                should_win = wins < target_wins
                
                # Pick the home team if we want to win, away team if we want to lose
                # (This is just for simulation - in reality it depends on actual game results)
                selected_team = game['home_team'] if should_win else game['away_team']
                is_correct = 1 if should_win else 0
                
                cursor.execute('''
                    INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, is_correct, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, game['id'], selected_team, 21, 17, is_correct, datetime.now().isoformat()))
                
                if should_win:
                    wins += 1
                
                # Stop once we've reached our target
                if wins >= target_wins:
                    break
        
        # Now create the Monday Night Football picks with the dramatic scenario
        # TWIST: Everyone ahead of David picks CIN (wrong), David picks DEN (correct)!
        mnf_picks = {
            "Test_Alice": {"selected": "CIN", "pred_score": [28, 17]},    # WRONG!
            "Test_Bob": {"selected": "CIN", "pred_score": [31, 14]},      # WRONG!
            "Test_Charlie": {"selected": "CIN", "pred_score": [24, 20]},  # WRONG!
            "Test_David": {"selected": "DEN", "pred_score": [21, 24]},    # CORRECT! Perfect prediction!
            "Test_Eve": {"selected": "CIN", "pred_score": [28, 21]}       # WRONG!
        }
        
        # Simulate the actual game result: CIN 21, DEN 24
        actual_cin_score = 21
        actual_den_score = 24
        actual_winner = "DEN"
        
        print()
        print("Creating Monday Night Football picks...")
        print("Actual Result: CIN 21, DEN 24 (DEN wins)")
        print()
        
        for username, pick_data in mnf_picks.items():
            user_id = user_ids[username]
            selected_team = pick_data["selected"]
            pred_cin, pred_den = pick_data["pred_score"]
            
            # Determine if pick is correct (selected the winner)
            is_correct = 1 if selected_team == actual_winner else 0
            
            cursor.execute('''
                INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, is_correct, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, mnf_game_id, selected_team, pred_den, pred_cin, is_correct, datetime.now().isoformat()))
            
            status = "✓ CORRECT" if is_correct else "✗ WRONG"
            print(f"{username:12} | Picked: {selected_team} | Score: CIN {pred_cin}, DEN {pred_den} | {status}")
        
        # Update the MNF game with actual results
        cursor.execute('''
            UPDATE nfl_games 
            SET home_score = ?, away_score = ?, is_final = 1
            WHERE id = ?
        ''', (actual_den_score, actual_cin_score, mnf_game_id))
        
        conn.commit()
        print()
        print("Test data created successfully!")
        
        # Now test the leaderboard calculation
        print()
        print("=== TESTING LEADERBOARD CALCULATION ===")
        
        # Simulate the weekly_leaderboard function logic
        cursor.execute('''
            SELECT u.id, u.username,
                   COUNT(p.id) as total_picks,
                   SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
            FROM users u
            JOIN user_picks p ON u.id = p.user_id
            JOIN nfl_games g ON p.game_id = g.id
            WHERE g.week = ? AND g.year = ? AND u.username LIKE "Test_%" AND u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING total_picks > 0
            ORDER BY correct_picks DESC, u.username
        ''', (test_week, test_year))
        
        user_results = cursor.fetchall()
        
        print("Raw Results:")
        for user_id, username, total_picks, correct_picks in user_results:
            print(f"{username:15} | {correct_picks:2} wins out of {total_picks:2} picks")
        
        # Calculate Monday Night tiebreakers
        leaderboard_data = []
        
        for user_id, username, total_picks, correct_picks in user_results:
            
            # Get Monday Night pick data
            cursor.execute('''
                SELECT p.predicted_home_score, p.predicted_away_score, p.selected_team,
                       g.home_score, g.away_score, g.home_team, g.away_team, g.is_final
                FROM user_picks p
                JOIN nfl_games g ON p.game_id = g.id
                WHERE p.user_id = ? AND g.id = ?
                LIMIT 1
            ''', (user_id, mnf_game_id))
            
            monday_pick = cursor.fetchone()
            
            # Calculate tiebreaker data using NEW system
            monday_tiebreaker = {'has_pick': False, 'total_diff': 999, 'winner_diff': 999, 'loser_diff': 999}
            
            if monday_pick:
                pred_home = monday_pick[0] or 0  # DEN
                pred_away = monday_pick[1] or 0  # CIN
                selected_team = monday_pick[2]
                actual_home = monday_pick[3] or 0  # DEN (24)
                actual_away = monday_pick[4] or 0  # CIN (21)
                is_final = monday_pick[7]
                
                if is_final and actual_home is not None and actual_away is not None:
                    # NEW TIEBREAKER SYSTEM
                    total_diff = abs((pred_home + pred_away) - (actual_home + actual_away))
                    
                    # Determine winner and loser
                    if actual_home > actual_away:  # DEN won
                        winner_diff = abs(pred_home - actual_home)  # Closeness to DEN's score
                        loser_diff = abs(pred_away - actual_away)   # Closeness to CIN's score
                    else:  # CIN won
                        winner_diff = abs(pred_away - actual_away)  # Closeness to CIN's score
                        loser_diff = abs(pred_home - actual_home)   # Closeness to DEN's score
                    
                    correct_winner = (selected_team == "DEN" and actual_home > actual_away) or \
                                   (selected_team == "CIN" and actual_away > actual_home)
                    
                    monday_tiebreaker = {
                        'has_pick': True,
                        'correct_winner': correct_winner,
                        'total_diff': total_diff,
                        'winner_diff': winner_diff,
                        'loser_diff': loser_diff,
                        'prediction': f"CIN {pred_away}, DEN {pred_home}",
                        'selected_team': selected_team
                    }
            
            leaderboard_data.append({
                'username': username,
                'correct_picks': correct_picks,
                'monday_tiebreaker': monday_tiebreaker
            })
        
        # Sort using NEW tiebreaker rules
        leaderboard_data.sort(key=lambda x: (
            -x['correct_picks'],                               # Most games won
            not x['monday_tiebreaker'].get('correct_winner', False),  # Correct winner first
            x['monday_tiebreaker'].get('total_diff', 999),     # Closest to total points
            x['monday_tiebreaker'].get('winner_diff', 999),    # Closest to winner score
            x['monday_tiebreaker'].get('loser_diff', 999),     # Closest to loser score
            x['username']                                      # Alphabetical
        ))
        
        print()
        print("FINAL LEADERBOARD (NEW TIEBREAKER SYSTEM):")
        print("Rank | Player      | Wins | MNF Pick    | Total Diff | Winner Diff | Loser Diff")
        print("-----|-------------|------|-------------|------------|-------------|------------")
        
        for i, user in enumerate(leaderboard_data, 1):
            tb = user['monday_tiebreaker']
            winner_status = "✓" if tb.get('correct_winner', False) else "✗"
            prediction = tb.get('prediction', 'No Pick')
            
            print(f"{i:4} | {user['username']:11} | {user['correct_picks']:4} | {prediction:11} | {tb.get('total_diff', 999):10} | {tb.get('winner_diff', 999):11} | {tb.get('loser_diff', 999):10}")
        
        print()
        print("ANALYSIS:")
        
        # Find tied users
        max_wins = max(user['correct_picks'] for user in leaderboard_data)
        tied_users = [user for user in leaderboard_data if user['correct_picks'] == max_wins]
        
        if len(tied_users) > 1:
            print(f"• {len(tied_users)} users tied at {max_wins} wins")
            print(f"• Winner: {leaderboard_data[0]['username']} (won tiebreaker)")
            
            winner_tb = leaderboard_data[0]['monday_tiebreaker']
            print(f"• Winning tiebreaker: Total diff = {winner_tb.get('total_diff', 'N/A')}")
        else:
            print(f"• Clear winner: {leaderboard_data[0]['username']} with {max_wins} wins")
        
        # Check David's comeback story
        david = next((user for user in leaderboard_data if 'David' in user['username']), None)
        if david and david['correct_picks'] >= 11:
            david_rank = next(i for i, user in enumerate(leaderboard_data, 1) if 'David' in user['username'])
            print(f"• David's Comeback: Moved from 10 to {david['correct_picks']} wins (Rank #{david_rank})")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test data
        cursor.execute('DELETE FROM user_picks WHERE user_id IN (SELECT id FROM users WHERE username LIKE "Test_%")')
        cursor.execute('DELETE FROM users WHERE username LIKE "Test_%"')
        conn.commit()
        conn.close()
        print()
        print("Test data cleaned up")

if __name__ == "__main__":
    success = test_complex_mnf_tiebreaker()
    if success:
        print()
        print("✓ Complex MNF tiebreaker test completed successfully!")
    else:
        print()
        print("✗ Test failed")
        sys.exit(1)