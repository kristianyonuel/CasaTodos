"""
Complete Example: Monday Night Football Tiebreaker Logic Implementation
This demonstrates the exact scoring system you requested
"""

def comprehensive_monday_night_example():
    """
    Complete example showing Monday Night Football tiebreaker logic
    """
    
    print("🏈 MONDAY NIGHT FOOTBALL TIEBREAKER LOGIC")
    print("=" * 70)
    print("Logic: Closest to home team score → away team score → total combined score")
    print("=" * 70)
    
    # Example Monday Night Football game
    monday_night_result = {
        'home_team': 'Chiefs',
        'away_team': 'Raiders',
        'home_score': 28,
        'away_score': 17,
        'total_score': 45
    }
    
    print(f"\n🏆 MONDAY NIGHT ACTUAL RESULT:")
    print(f"   {monday_night_result['home_team']} (Home): {monday_night_result['home_score']} points")
    print(f"   {monday_night_result['away_team']} (Away): {monday_night_result['away_score']} points")
    print(f"   Combined Total: {monday_night_result['total_score']} points")
    
    # Example tied users (same weekly total score)
    tied_users = [
        {
            'name': 'User A',
            'weekly_total': 95,
            'monday_picks': {'home': 30, 'away': 14},  # Total: 44
            'submission_time': '2025-09-14 11:30:00'
        },
        {
            'name': 'User B', 
            'weekly_total': 95,
            'monday_picks': {'home': 24, 'away': 21},  # Total: 45
            'submission_time': '2025-09-14 11:25:00'
        },
        {
            'name': 'User C',
            'weekly_total': 95,
            'monday_picks': {'home': 27, 'away': 20},  # Total: 47
            'submission_time': '2025-09-14 11:35:00'
        },
        {
            'name': 'User D',
            'weekly_total': 95,
            'monday_picks': {'home': 26, 'away': 19},  # Total: 45
            'submission_time': '2025-09-14 11:40:00'
        }
    ]
    
    print(f"\n👥 TIED USERS (All have {tied_users[0]['weekly_total']} weekly points):")
    for user in tied_users:
        predicted_home = user['monday_picks']['home']
        predicted_away = user['monday_picks']['away']
        predicted_total = predicted_home + predicted_away
        
        print(f"   {user['name']}: {monday_night_result['home_team']} = {predicted_home}, {monday_night_result['away_team']} = {predicted_away} (Total: {predicted_total})")
    
    return tied_users, monday_night_result

def calculate_monday_tiebreakers(users, actual_result):
    """
    Calculate tiebreaker data for each user
    """
    
    print(f"\n🔢 TIEBREAKER CALCULATIONS:")
    print("=" * 70)
    
    tiebreaker_data = []
    
    for user in users:
        pred_home = user['monday_picks']['home']
        pred_away = user['monday_picks']['away']
        pred_total = pred_home + pred_away
        
        actual_home = actual_result['home_score']
        actual_away = actual_result['away_score']
        actual_total = actual_result['total_score']
        
        # Calculate differences (absolute values - closer is better)
        home_diff = abs(pred_home - actual_home)
        away_diff = abs(pred_away - actual_away)
        total_diff = abs(pred_total - actual_total)
        
        tiebreaker_data.append({
            'name': user['name'],
            'weekly_total': user['weekly_total'],
            'predicted': {'home': pred_home, 'away': pred_away, 'total': pred_total},
            'differences': {
                'home': home_diff,
                'away': away_diff, 
                'total': total_diff
            },
            'submission_time': user['submission_time']
        })
        
        print(f"\n{user['name']}:")
        print(f"   Predicted: Home = {pred_home}, Away = {pred_away}, Total = {pred_total}")
        print(f"   Actual:    Home = {actual_home}, Away = {actual_away}, Total = {actual_total}")
        print(f"   Differences:")
        print(f"      Home Team: |{pred_home} - {actual_home}| = {home_diff}")
        print(f"      Away Team: |{pred_away} - {actual_away}| = {away_diff}")
        print(f"      Total:     |{pred_total} - {actual_total}| = {total_diff}")
    
    return tiebreaker_data

def resolve_tiebreakers(tiebreaker_data):
    """
    Resolve tiebreakers using Monday Night logic
    """
    
    print(f"\n🏆 TIEBREAKER RESOLUTION:")
    print("=" * 70)
    
    # Sort using the Monday Night tiebreaker rules:
    # 1. Weekly total (already tied)
    # 2. Closest to home team score
    # 3. Closest to away team score
    # 4. Closest to total combined score
    # 5. Earlier submission time
    
    sorted_users = sorted(tiebreaker_data, key=lambda x: (
        -x['weekly_total'],                    # Highest weekly score first (tied)
        x['differences']['home'],              # Closest to home team
        x['differences']['away'],              # Closest to away team
        x['differences']['total'],             # Closest to total
        x['submission_time']                   # Earlier submission
    ))
    
    print("STEP 1: Weekly Total Score")
    print(f"   All users tied at {tiebreaker_data[0]['weekly_total']} points")
    print("   → Move to Monday Night tiebreakers")
    
    print(f"\nSTEP 2: Closest to Home Team Score ({tiebreaker_data[0]['predicted']['home']} actual)")
    home_diffs = [(user['name'], user['differences']['home']) for user in tiebreaker_data]
    home_diffs.sort(key=lambda x: x[1])
    
    for name, diff in home_diffs:
        print(f"   {name}: {diff} point difference")
    
    # Check if home team resolves the tie
    best_home_diff = min(user['differences']['home'] for user in tiebreaker_data)
    home_winners = [user for user in tiebreaker_data if user['differences']['home'] == best_home_diff]
    
    if len(home_winners) == 1:
        print(f"   🥇 WINNER: {home_winners[0]['name']} (closest to home team score)")
        return sorted_users
    
    print(f"   Still tied: {', '.join([user['name'] for user in home_winners])}")
    
    print(f"\nSTEP 3: Closest to Away Team Score ({tiebreaker_data[0]['predicted']['away']} actual)")
    for user in home_winners:
        print(f"   {user['name']}: {user['differences']['away']} point difference")
    
    # Check if away team resolves the tie
    best_away_diff = min(user['differences']['away'] for user in home_winners)
    away_winners = [user for user in home_winners if user['differences']['away'] == best_away_diff]
    
    if len(away_winners) == 1:
        print(f"   🥇 WINNER: {away_winners[0]['name']} (closest to away team score)")
        return sorted_users
    
    print(f"   Still tied: {', '.join([user['name'] for user in away_winners])}")
    
    print(f"\nSTEP 4: Closest to Total Combined Score")
    for user in away_winners:
        print(f"   {user['name']}: {user['differences']['total']} point difference")
    
    # Final winner
    print(f"   🥇 FINAL WINNER: {sorted_users[0]['name']}")
    
    return sorted_users

def show_final_results(sorted_users):
    """
    Display final ranking with complete breakdown
    """
    
    print(f"\n🏁 FINAL RANKING:")
    print("=" * 70)
    
    for i, user in enumerate(sorted_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        print(f"{medal} {user['name']}")
        print(f"    Weekly Score: {user['weekly_total']} points")
        print(f"    Monday Prediction: {user['predicted']['home']}-{user['predicted']['away']} (Total: {user['predicted']['total']})")
        print(f"    Tiebreaker Diffs: Home={user['differences']['home']}, Away={user['differences']['away']}, Total={user['differences']['total']}")
        print(f"    Submitted: {user['submission_time']}")
        print()

def main():
    """
    Main demonstration of Monday Night tiebreaker logic
    """
    
    # Set up example scenario
    tied_users, monday_result = comprehensive_monday_night_example()
    
    # Calculate tiebreaker data
    tiebreaker_data = calculate_monday_tiebreakers(tied_users, monday_result)
    
    # Resolve tiebreakers
    final_ranking = resolve_tiebreakers(tiebreaker_data)
    
    # Show final results
    show_final_results(final_ranking)
    
    # Summary
    print("📋 TIEBREAKER SUMMARY:")
    print("=" * 70)
    print("When users have identical weekly scores, Monday Night Football")
    print("predictions break ties in this exact order:")
    print()
    print("1️⃣ CLOSEST TO HOME TEAM SCORE (either higher or lower)")
    print("2️⃣ CLOSEST TO AWAY TEAM SCORE") 
    print("3️⃣ CLOSEST TO TOTAL COMBINED SCORE")
    print("4️⃣ EARLIER SUBMISSION TIME")
    print()
    print("This makes Monday Night predictions strategically important")
    print("for final weekly rankings, not just overall scoring!")

if __name__ == "__main__":
    main()
