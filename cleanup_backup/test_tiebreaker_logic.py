#!/usr/bin/env python3
"""
Test the updated Monday Night tiebreaker logic
"""

from scoring_updater import ScoringUpdater

def test_tiebreaker_logic():
    updater = ScoringUpdater()
    
    print("🏈 TESTING UPDATED MONDAY NIGHT TIEBREAKER LOGIC")
    print("=" * 60)
    
    # Get Week 1 results with new logic
    results = updater.get_week_winners(1, 2025)
    
    print("\n📊 WEEK 1 RESULTS WITH NEW TIEBREAKER LOGIC:")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        username = result['username']
        correct_picks = result['correct_picks']
        tiebreaker = result['monday_tiebreaker']
        
        print(f"Rank {i}: {username}")
        print(f"  Correct picks: {correct_picks}")
        print(f"  MNF correct winner: {tiebreaker.get('correct_winner', 'N/A')}")
        print(f"  MNF tiebreaker: Home ±{tiebreaker.get('home_diff', 'N/A')}, "
              f"Away ±{tiebreaker.get('away_diff', 'N/A')}, "
              f"Total ±{tiebreaker.get('total_diff', 'N/A')}")
        print()
    
    # Focus on users with 13 correct picks to see tiebreaker in action
    print("\n🎯 USERS WITH 13 CORRECT PICKS (TIEBREAKER ZONE):")
    print("-" * 60)
    
    top_scorers = [r for r in results if r['correct_picks'] == 13]
    
    for i, result in enumerate(top_scorers, 1):
        username = result['username']
        tiebreaker = result['monday_tiebreaker']
        
        print(f"{i}. {username}")
        print(f"   Correct Winner: {tiebreaker.get('correct_winner', False)}")
        print(f"   Home diff: {tiebreaker.get('home_diff', 999)}")
        print(f"   Away diff: {tiebreaker.get('away_diff', 999)}")
        print(f"   Total diff: {tiebreaker.get('total_diff', 999)}")
        print()
    
    print("🏆 TIEBREAKER PRIORITY ORDER:")
    print("1. Most correct picks")
    print("2. Picked correct MNF winner")
    print("3. Closest to home team score")
    print("4. Closest to away team score") 
    print("5. Closest to total score")
    print("6. Earlier submission time")
    print("7. Alphabetical username")

if __name__ == "__main__":
    test_tiebreaker_logic()
