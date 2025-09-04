#!/usr/bin/env python3
"""
NFL Fantasy Leaderboard Scoring System Example
This demonstrates how the point-based scoring system works for determining winners
"""

import sys
import os
from datetime import datetime

def leaderboard_scoring_example():
    """
    Example of how the leaderboard scoring system works
    """
    
    print("🏈 NFL FANTASY LEADERBOARD SCORING SYSTEM")
    print("="*70)
    
    print("\n📊 EXAMPLE SCENARIO:")
    print("-" * 50)
    
    # Example game results
    actual_results = {
        'team_x': 20,  # Team X scored 20 points
        'team_2': 18   # Team 2 scored 18 points (NOT 10 as in your example - fixing the typo)
    }
    
    print(f"🏆 ACTUAL GAME RESULTS:")
    print(f"   Team X: {actual_results['team_x']} points")
    print(f"   Team 2: {actual_results['team_2']} points")
    print(f"   Total Combined: {actual_results['team_x'] + actual_results['team_2']} points")
    print()
    
    # User predictions
    users = [
        {
            'name': 'User 1',
            'predictions': {'team_x': 20, 'team_2': 22},
            'total_predicted': 42
        },
        {
            'name': 'User 2', 
            'predictions': {'team_x': 20, 'team_2': 16},
            'total_predicted': 36
        },
        {
            'name': 'User 3',
            'predictions': {'team_x': 18, 'team_2': 20},
            'total_predicted': 38
        }
    ]
    
    actual_total = actual_results['team_x'] + actual_results['team_2']
    
    print(f"👥 USER PREDICTIONS:")
    for user in users:
        pred_x = user['predictions']['team_x']
        pred_2 = user['predictions']['team_2']
        total_pred = user['total_predicted']
        
        print(f"   {user['name']}: Team X = {pred_x}, Team 2 = {pred_2}")
        print(f"      Predicted Total: {total_pred}")
        print(f"      Difference from actual total ({actual_total}): {abs(total_pred - actual_total)}")
        print()
    
    return users, actual_results

def calculate_user_score(user_predictions, actual_results):
    """
    Calculate user score based on multiple factors:
    1. Exact team predictions (10 points each)
    2. Close predictions (points based on how close)
    3. Total score proximity bonus
    """
    
    score = 0
    breakdown = {
        'exact_predictions': 0,
        'proximity_points': 0,
        'total_proximity_bonus': 0,
        'total_score': 0
    }
    
    # 1. Exact team predictions (10 points each)
    for team in actual_results:
        if user_predictions.get(team) == actual_results[team]:
            breakdown['exact_predictions'] += 10
            score += 10
    
    # 2. Proximity points for each team (closer = more points)
    for team in actual_results:
        predicted = user_predictions.get(team, 0)
        actual = actual_results[team]
        difference = abs(predicted - actual)
        
        # Award points based on proximity (max 5 points per team)
        if difference == 0:
            proximity = 5  # Already counted in exact predictions
        elif difference <= 3:
            proximity = 4
        elif difference <= 5:
            proximity = 3
        elif difference <= 7:
            proximity = 2
        elif difference <= 10:
            proximity = 1
        else:
            proximity = 0
        
        breakdown['proximity_points'] += proximity
        score += proximity
    
    # 3. Total score proximity bonus (comparing combined totals)
    predicted_total = sum(user_predictions.values())
    actual_total = sum(actual_results.values())
    total_difference = abs(predicted_total - actual_total)
    
    # Bonus points for getting close to total combined score
    if total_difference == 0:
        total_bonus = 15  # Perfect total prediction
    elif total_difference <= 2:
        total_bonus = 10
    elif total_difference <= 5:
        total_bonus = 7
    elif total_difference <= 10:
        total_bonus = 5
    elif total_difference <= 15:
        total_bonus = 3
    elif total_difference <= 20:
        total_bonus = 1
    else:
        total_bonus = 0
    
    breakdown['total_proximity_bonus'] = total_bonus
    score += total_bonus
    
    breakdown['total_score'] = score
    return score, breakdown

def demonstrate_scoring():
    """
    Demonstrate the scoring system with the example scenario
    """
    
    users, actual_results = leaderboard_scoring_example()
    
    print("🔢 DETAILED SCORING BREAKDOWN:")
    print("="*70)
    
    user_scores = []
    
    for user in users:
        score, breakdown = calculate_user_score(user['predictions'], actual_results)
        user_scores.append({
            'name': user['name'],
            'score': score,
            'breakdown': breakdown,
            'predictions': user['predictions']
        })
        
        print(f"\n{user['name']} SCORING:")
        print(f"   Predictions: Team X = {user['predictions']['team_x']}, Team 2 = {user['predictions']['team_2']}")
        print(f"   Exact Predictions: {breakdown['exact_predictions']} points")
        print(f"   Proximity Points: {breakdown['proximity_points']} points") 
        print(f"   Total Proximity Bonus: {breakdown['total_proximity_bonus']} points")
        print(f"   TOTAL SCORE: {breakdown['total_score']} points")
    
    # Sort by total score (highest first)
    user_scores.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🏆 FINAL LEADERBOARD:")
    print("="*50)
    for i, user in enumerate(user_scores, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{medal} {user['name']}: {user['score']} points")
        
        # Show why they ranked this way
        pred_total = sum(user['predictions'].values())
        actual_total = sum(actual_results.values())
        diff = abs(pred_total - actual_total)
        print(f"     Predicted total: {pred_total}, Actual: {actual_total}, Diff: {diff}")
    
    return user_scores

def tiebreaker_logic_example():
    """
    Example of tiebreaker logic when users have the same total score
    """
    
    print(f"\n" + "="*70)
    print("🤝 TIEBREAKER LOGIC")
    print("="*70)
    
    print("\nIf users have the same total score, tiebreakers are:")
    print("1. More exact team predictions")
    print("2. Smaller total score difference") 
    print("3. Earlier submission time")
    print("4. Alphabetical order (last resort)")
    
    # Example tiebreaker scenario
    tied_users = [
        {
            'name': 'User A',
            'total_score': 25,
            'exact_predictions': 1,
            'total_difference': 3,
            'submission_time': '2025-09-14 11:30:00'
        },
        {
            'name': 'User B', 
            'total_score': 25,
            'exact_predictions': 0,
            'total_difference': 1,
            'submission_time': '2025-09-14 11:45:00'
        }
    ]
    
    print(f"\n📊 TIEBREAKER EXAMPLE:")
    print(f"Both users have 25 points total")
    print(f"User A: 1 exact prediction, total diff = 3")
    print(f"User B: 0 exact predictions, total diff = 1")
    print(f"WINNER: User A (more exact predictions beats smaller total difference)")

def main():
    """Main demonstration function"""
    
    # Demonstrate the main scoring system
    user_scores = demonstrate_scoring()
    
    # Show tiebreaker logic
    tiebreaker_logic_example()
    
    print(f"\n" + "="*70)
    print("📋 SCORING SUMMARY:")
    print("="*70)
    print("• Exact team score prediction: 10 points each")
    print("• Proximity points: 1-5 points per team (closer = more points)")
    print("• Total score proximity bonus: 1-15 points (closer = more points)")
    print("• Higher combined points = better ranking")
    print("• Tiebreakers: exact predictions > total difference > submission time")
    
    return user_scores

if __name__ == "__main__":
    main()
