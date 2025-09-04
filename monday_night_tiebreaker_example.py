#!/usr/bin/env python3
"""
Monday Night Football Tiebreaker Logic Example
Demonstrates how ties are broken using Monday Night game predictions
"""

def monday_night_tiebreaker_example():
    """
    Example of Monday Night Football tiebreaker logic
    """
    
    print("🏈 MONDAY NIGHT FOOTBALL TIEBREAKER LOGIC")
    print("="*70)
    
    # Example scenario: Multiple users tied with same total points
    print("\n📊 EXAMPLE SCENARIO:")
    print("-" * 50)
    
    # Actual Monday Night game result
    monday_actual = {
        'home_team': 'Chiefs',
        'away_team': 'Raiders', 
        'home_score': 28,
        'away_score': 17
    }
    
    print(f"🏆 MONDAY NIGHT ACTUAL RESULT:")
    print(f"   {monday_actual['home_team']} (Home): {monday_actual['home_score']} points")
    print(f"   {monday_actual['away_team']} (Away): {monday_actual['away_score']} points")
    print(f"   Total Combined: {monday_actual['home_score'] + monday_actual['away_score']} points")
    print()
    
    # Users with tied total scores but different Monday predictions
    tied_users = [
        {
            'name': 'User A',
            'total_weekly_score': 85,  # Same total score
            'monday_prediction': {'home': 30, 'away': 14},  # Total: 44
            'submission_time': '2025-09-14 11:30:00'
        },
        {
            'name': 'User B',
            'total_weekly_score': 85,  # Same total score  
            'monday_prediction': {'home': 24, 'away': 21},  # Total: 45
            'submission_time': '2025-09-14 11:25:00'
        },
        {
            'name': 'User C',
            'total_weekly_score': 85,  # Same total score
            'monday_prediction': {'home': 27, 'away': 20},  # Total: 47
            'submission_time': '2025-09-14 11:35:00'
        }
    ]
    
    print(f"👥 TIED USERS (All have 85 total points):")
    for user in tied_users:
        pred_home = user['monday_prediction']['home']
        pred_away = user['monday_prediction']['away'] 
        pred_total = pred_home + pred_away
        
        print(f"   {user['name']}: {monday_actual['home_team']} = {pred_home}, {monday_actual['away_team']} = {pred_away}")
        print(f"      Predicted Total: {pred_total}")
        print()
    
    return tied_users, monday_actual

def calculate_tiebreakers(tied_users, monday_actual):
    """
    Calculate tiebreaker differences for Monday Night predictions
    """
    
    print("🔢 TIEBREAKER CALCULATIONS:")
    print("="*70)
    
    results = []
    
    for user in tied_users:
        pred_home = user['monday_prediction']['home']
        pred_away = user['monday_prediction']['away']
        actual_home = monday_actual['home_score']
        actual_away = monday_actual['away_score']
        
        # Calculate differences for each tiebreaker level
        home_diff = abs(pred_home - actual_home)
        away_diff = abs(pred_away - actual_away)
        total_diff = abs((pred_home + pred_away) - (actual_home + actual_away))
        
        results.append({
            'name': user['name'],
            'total_score': user['total_weekly_score'],
            'home_difference': home_diff,
            'away_difference': away_diff,
            'total_difference': total_diff,
            'predictions': user['monday_prediction'],
            'submission_time': user['submission_time']
        })
        
        print(f"\n{user['name']} TIEBREAKER DATA:")
        print(f"   Predicted: Home = {pred_home}, Away = {pred_away}")
        print(f"   Actual:    Home = {actual_home}, Away = {actual_away}")
        print(f"   Home Team Difference: |{pred_home} - {actual_home}| = {home_diff}")
        print(f"   Away Team Difference: |{pred_away} - {actual_away}| = {away_diff}")
        print(f"   Total Score Difference: |{pred_home + pred_away} - {actual_home + actual_away}| = {total_diff}")
    
    return results

def determine_winner_with_tiebreakers(results):
    """
    Determine winner using Monday Night tiebreaker logic
    """
    
    print(f"\n🏆 TIEBREAKER RESOLUTION:")
    print("="*70)
    
    # Sort using the Monday Night tiebreaker logic
    # 1. Highest total score (already tied)
    # 2. Closest to home team score
    # 3. Closest to away team score  
    # 4. Closest to total combined score
    # 5. Earlier submission time (if still tied)
    
    sorted_results = sorted(results, key=lambda x: (
        -x['total_score'],           # Highest score first (all tied at 85)
        x['home_difference'],        # Closest to home team score
        x['away_difference'],        # Closest to away team score
        x['total_difference'],       # Closest to total score
        x['submission_time']         # Earlier submission time
    ))
    
    print("STEP 1: Total Weekly Score")
    print("   All users tied at 85 points - move to Monday Night tiebreakers")
    print()
    
    print("STEP 2: Closest to Home Team Score (Chiefs = 28)")
    for user in results:
        print(f"   {user['name']}: Predicted {user['predictions']['home']}, Difference = {user['home_difference']}")
    
    # Find who has the smallest home difference
    best_home_diff = min(results, key=lambda x: x['home_difference'])['home_difference']
    home_winners = [u for u in results if u['home_difference'] == best_home_diff]
    
    if len(home_winners) == 1:
        print(f"   🥇 WINNER: {home_winners[0]['name']} (closest to home team score)")
        return sorted_results
    else:
        print(f"   Still tied: {', '.join([u['name'] for u in home_winners])}")
        print()
        
        print("STEP 3: Closest to Away Team Score (Raiders = 17)")
        for user in home_winners:
            print(f"   {user['name']}: Predicted {user['predictions']['away']}, Difference = {user['away_difference']}")
        
        best_away_diff = min(home_winners, key=lambda x: x['away_difference'])['away_difference']
        away_winners = [u for u in home_winners if u['away_difference'] == best_away_diff]
        
        if len(away_winners) == 1:
            print(f"   🥇 WINNER: {away_winners[0]['name']} (closest to away team score)")
            return sorted_results
        else:
            print(f"   Still tied: {', '.join([u['name'] for u in away_winners])}")
            print()
            
            print("STEP 4: Closest to Total Combined Score (45)")
            for user in away_winners:
                print(f"   {user['name']}: Total Difference = {user['total_difference']}")
            
            print(f"   🥇 FINAL WINNER: {sorted_results[0]['name']}")
    
    return sorted_results

def show_final_ranking(sorted_results):
    """
    Show the final ranking with detailed breakdown
    """
    
    print(f"\n🏁 FINAL RANKING:")
    print("="*70)
    
    for i, user in enumerate(sorted_results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"{medal} {user['name']}")
        print(f"    Total Score: {user['total_score']} points")
        print(f"    Monday Night: Home diff = {user['home_difference']}, Away diff = {user['away_difference']}, Total diff = {user['total_difference']}")
        print()

def main():
    """Main demonstration function"""
    
    # Set up the example scenario
    tied_users, monday_actual = monday_night_tiebreaker_example()
    
    # Calculate tiebreaker differences
    results = calculate_tiebreakers(tied_users, monday_actual)
    
    # Determine winner using tiebreaker logic
    sorted_results = determine_winner_with_tiebreakers(results)
    
    # Show final ranking
    show_final_ranking(sorted_results)
    
    print("📋 SUMMARY:")
    print("="*70)
    print("When users are tied on total weekly points, Monday Night Football")
    print("predictions are used as tiebreakers in this order:")
    print("1. Closest to home team score (either higher or lower)")
    print("2. Closest to away team score")
    print("3. Closest to total combined score")
    print("4. Earlier submission time (if still tied)")
    print()
    print("This ensures that Monday Night predictions matter for ranking")
    print("even when users have identical overall weekly performance.")

if __name__ == "__main__":
    main()
