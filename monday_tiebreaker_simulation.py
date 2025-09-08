#!/usr/bin/env python3
"""
Monday Night Tiebreaker Simulation
Comprehensive analysis showing winning conditions for each tied player
"""

def calculate_tiebreaker_score(predicted_away, predicted_home, actual_away, actual_home):
    """Calculate tiebreaker score based on closest prediction"""
    home_diff = abs(predicted_home - actual_home)
    away_diff = abs(predicted_away - actual_away)
    total_diff = abs((predicted_home + predicted_away) - (actual_home + actual_away))
    
    return {
        'home_diff': home_diff,
        'away_diff': away_diff, 
        'total_diff': total_diff,
        'total_score': home_diff + away_diff  # Simple total difference
    }

def analyze_winning_conditions():
    """Analyze what score ranges each player needs to win"""
    
    tied_leaders = [
        ('coyote', 'MIN', 21, 27),      # predicted MIN 21 - 27 CHI
        ('ramfis', 'CHI', 19, 22),      # predicted MIN 19 - 22 CHI
        ('raymond', 'MIN', 21, 25),     # predicted MIN 21 - 25 CHI
        ('vizca', 'MIN', 17, 24),       # predicted MIN 17 - 24 CHI
    ]
    
    print("\n🎯 COMPREHENSIVE WINNING CONDITIONS ANALYSIS")
    print("=" * 80)
    
    # First, show what happens if CHI wins
    print("\n🔥 IF CHICAGO WINS:")
    print("   Only RAMFIS can win (only player who picked CHI)")
    print("   Any CHI win score gives Ramfis the victory")
    print("   Optimal for Ramfis: MIN 19 - CHI 22 (his exact prediction)")
    
    # Now analyze Minnesota win scenarios
    print("\n🔥 IF MINNESOTA WINS - DETAILED BREAKDOWN:")
    print("   Only MIN pickers can win: COYOTE, RAYMOND, VIZCA")
    
    # Test various MIN win scenarios
    test_scenarios = []
    
    # Generate comprehensive test cases
    for min_score in range(10, 35, 2):  # Minnesota scores 10-34
        for chi_score in range(10, min_score):  # Chicago scores less (MIN wins)
            # Test this scenario
            winner = determine_winner_for_score(min_score, chi_score, tied_leaders)
            if winner:
                test_scenarios.append((min_score, chi_score, winner))
    
    # Group by winner
    coyote_wins = [(m, c) for m, c, w in test_scenarios if w == 'coyote']
    raymond_wins = [(m, c) for m, c, w in test_scenarios if w == 'raymond']  
    vizca_wins = [(m, c) for m, c, w in test_scenarios if w == 'vizca']
    
    print(f"\n🏆 COYOTE WINS ({len(coyote_wins)} scenarios):")
    print("   Prediction: MIN 21 - CHI 27")
    print("   Best when: MIN score close to 21, CHI score close to 27")
    if coyote_wins:
        print(f"   Sample wins: {coyote_wins[:5]}...")
    
    print(f"\n🏆 RAYMOND WINS ({len(raymond_wins)} scenarios):")
    print("   Prediction: MIN 21 - CHI 25") 
    print("   Best when: MIN score close to 21, CHI score close to 25")
    if raymond_wins:
        print(f"   Sample wins: {raymond_wins[:5]}...")
    
    print(f"\n🏆 VIZCA WINS ({len(vizca_wins)} scenarios):")
    print("   Prediction: MIN 17 - CHI 24")
    print("   Best when: MIN score close to 17, CHI score close to 24") 
    if vizca_wins:
        print(f"   Sample wins: {vizca_wins[:5]}...")
    
    return coyote_wins, raymond_wins, vizca_wins

def determine_winner_for_score(actual_away, actual_home, tied_leaders):
    """Determine winner for a specific score, considering only MIN pickers if MIN wins"""
    
    # If CHI wins, only ramfis can win
    if actual_home > actual_away:
        return 'ramfis'
    
    # If MIN wins, only MIN pickers can win
    min_pickers = [player for player in tied_leaders if player[1] == 'MIN']
    
    results = []
    for username, picked_team, pred_away, pred_home in min_pickers:
        scores = calculate_tiebreaker_score(pred_away, pred_home, actual_away, actual_home)
        results.append({
            'username': username,
            'total_score': scores['total_score'],
            'home_diff': scores['home_diff'],
            'away_diff': scores['away_diff'],
            'total_diff': scores['total_diff']
        })
    
    # Sort by tiebreaker logic
    results.sort(key=lambda x: (
        x['home_diff'],      # Closest to home score
        x['away_diff'],      # Then closest to away score  
        x['total_diff'],     # Then closest to total
        x['username']        # Alphabetical tiebreaker
    ))
    
    return results[0]['username'] if results else None

def simulate_scenario(actual_away, actual_home, scenario_name):
    """Simulate a specific game outcome scenario"""
    
    # ONLY the 4 tied leaders with 12 correct picks can win via Monday Night tiebreaker
    tied_leaders = [
        ('coyote', 'MIN', 21, 27),      # predicted MIN 21 - 27 CHI
        ('ramfis', 'CHI', 19, 22),      # predicted MIN 19 - 22 CHI
        ('raymond', 'MIN', 21, 25),     # predicted MIN 21 - 25 CHI
        ('vizca', 'MIN', 17, 24),       # predicted MIN 17 - 24 CHI
    ]
    
    print(f"\n🏈 SCENARIO: {scenario_name}")
    print(f"📊 Actual Result: MIN {actual_away} - {actual_home} CHI")
    print("🏆 TIED LEADERS (12 correct picks): coyote, ramfis, raymond, vizca")
    print("=" * 70)
    
    # Determine actual winner
    if actual_away > actual_home:
        actual_winner = 'MIN'
    elif actual_home > actual_away:
        actual_winner = 'CHI'
    else:
        actual_winner = 'TIE'
    
    results = []
    eligible_for_win = []
    
    for username, picked_team, pred_away, pred_home in tied_leaders:
        # Check if team pick was correct
        team_pick_correct = (picked_team == actual_winner)
        
        # Calculate tiebreaker scores
        scores = calculate_tiebreaker_score(pred_away, pred_home, actual_away, actual_home)
        
        result = {
            'username': username,
            'picked_team': picked_team,
            'team_correct': team_pick_correct,
            'prediction': f"MIN {pred_away} - {pred_home} CHI",
            'home_diff': scores['home_diff'],
            'away_diff': scores['away_diff'],
            'total_diff': scores['total_diff'],
            'total_score': scores['total_score']
        }
        
        results.append(result)
        
        # Only players who picked correctly can win
        if team_pick_correct:
            eligible_for_win.append(result)
    
    # Sort all results for display
    results.sort(key=lambda x: (
        -x['team_correct'],  # Team pick correct first
        x['home_diff'],      # Then closest to home score
        x['away_diff'],      # Then closest to away score  
        x['total_diff'],     # Then closest to total
        x['username']        # Alphabetical tiebreaker
    ))
    
    # Sort eligible winners by tiebreaker scores
    eligible_for_win.sort(key=lambda x: (
        x['home_diff'],      # Closest to home score
        x['away_diff'],      # Then closest to away score  
        x['total_diff'],     # Then closest to total
        x['username']        # Alphabetical tiebreaker
    ))
    
    print(f"{'Rank':<4} {'Player':<10} {'Pick':<4} {'Prediction':<15} {'Home±':<6} {'Away±':<6} {'Total±':<7} {'Status'}")
    print("-" * 75)
    
    for i, result in enumerate(results, 1):
        status = "✅ ELIGIBLE" if result['team_correct'] else "❌ ELIMINATED"
        winner_indicator = ""
        
        # Mark the actual winner
        if eligible_for_win and result['username'] == eligible_for_win[0]['username']:
            winner_indicator = "🏆 WINNER!"
        
        print(f"{i:<4} {result['username']:<10} {result['picked_team']:<4} {result['prediction']:<15} "
              f"{result['home_diff']:<6} {result['away_diff']:<6} {result['total_diff']:<7} {status} {winner_indicator}")
    
    if eligible_for_win:
        winner = eligible_for_win[0]
        print(f"\n🏆 WEEK 1 CHAMPION: {winner['username']}")
        print(f"   Picked: {winner['picked_team']} (CORRECT)")
        print(f"   Prediction: {winner['prediction']}")
        print(f"   Tiebreaker Score: Home ±{winner['home_diff']}, Away ±{winner['away_diff']}, Total ±{winner['total_diff']}")
        return winner['username']
    else:
        print(f"\n❌ NO WINNER: No player picked {actual_winner} correctly!")
        return None

def create_winning_map():
    """Create a comprehensive map showing which player wins for different scores"""
    
    print("\n🗺️  COMPREHENSIVE WINNING MAP")
    print("=" * 80)
    
    tied_leaders = [
        ('coyote', 'MIN', 21, 27),      # predicted MIN 21 - 27 CHI
        ('ramfis', 'CHI', 19, 22),      # predicted MIN 19 - 22 CHI
        ('raymond', 'MIN', 21, 25),     # predicted MIN 21 - 25 CHI
        ('vizca', 'MIN', 17, 24),       # predicted MIN 17 - 24 CHI
    ]
    
    # Create a map of scores to winners
    winning_map = {}
    
    # Test score ranges
    for min_score in range(10, 40):
        for chi_score in range(10, 40):
            # Determine winner for this score
            if chi_score > min_score:
                # CHI wins - only ramfis can win
                winner = 'ramfis'
            elif min_score > chi_score:
                # MIN wins - determine best MIN picker
                winner = determine_winner_for_score(min_score, chi_score, tied_leaders)
            else:
                # Tie game - need different logic
                winner = 'tie_game'
            
            winning_map[(min_score, chi_score)] = winner
    
    # Analyze patterns
    coyote_wins = [(m, c) for (m, c), w in winning_map.items() if w == 'coyote']
    raymond_wins = [(m, c) for (m, c), w in winning_map.items() if w == 'raymond']
    vizca_wins = [(m, c) for (m, c), w in winning_map.items() if w == 'vizca']
    ramfis_wins = [(m, c) for (m, c), w in winning_map.items() if w == 'ramfis']
    
    print(f"\n📊 WINNING STATISTICS:")
    print(f"🏆 RAMFIS wins in {len(ramfis_wins)} scenarios (CHI wins)")
    print(f"🏆 COYOTE wins in {len(coyote_wins)} scenarios (MIN wins)")
    print(f"🏆 RAYMOND wins in {len(raymond_wins)} scenarios (MIN wins)")
    print(f"🏆 VIZCA wins in {len(vizca_wins)} scenarios (MIN wins)")
    
    # Show specific ranges for each player
    print(f"\n🎯 DETAILED WINNING CONDITIONS:")
    
    print(f"\n🏆 RAMFIS (CHI picker) - Wins when CHI wins:")
    print("   Any game where CHI > MIN gives Ramfis the victory")
    print("   Optimal: MIN 19 - CHI 22 (his exact prediction)")
    
    if coyote_wins:
        print(f"\n🏆 COYOTE (MIN picker) - {len(coyote_wins)} winning scenarios:")
        print("   Prediction: MIN 21 - CHI 27")
        print("   Wins when MIN score ≈ 21 AND CHI score ≈ 27")
        coyote_best = min(coyote_wins, key=lambda x: abs(x[0]-21) + abs(x[1]-27))
        print(f"   Perfect scenario: MIN {coyote_best[0]} - CHI {coyote_best[1]}")
    
    if raymond_wins:
        print(f"\n🏆 RAYMOND (MIN picker) - {len(raymond_wins)} winning scenarios:")
        print("   Prediction: MIN 21 - CHI 25")
        print("   Wins when MIN score ≈ 21 AND CHI score ≈ 25")
        raymond_best = min(raymond_wins, key=lambda x: abs(x[0]-21) + abs(x[1]-25))
        print(f"   Perfect scenario: MIN {raymond_best[0]} - CHI {raymond_best[1]}")
    
    if vizca_wins:
        print(f"\n🏆 VIZCA (MIN picker) - {len(vizca_wins)} winning scenarios:")
        print("   Prediction: MIN 17 - CHI 24")
        print("   Wins when MIN score ≈ 17 AND CHI score ≈ 24")
        vizca_best = min(vizca_wins, key=lambda x: abs(x[0]-17) + abs(x[1]-24))
        print(f"   Perfect scenario: MIN {vizca_best[0]} - CHI {vizca_best[1]}")
    
    return winning_map

def show_specific_examples():
    """Show specific examples of each player winning"""
    
    print(f"\n🎮 SPECIFIC WINNING EXAMPLES:")
    print("=" * 60)
    
    # Perfect predictions for each player
    print("🏆 PERFECT PREDICTION SCENARIOS:")
    simulate_scenario(19, 22, "RAMFIS Perfect: MIN 19 - CHI 22")
    simulate_scenario(21, 27, "COYOTE Perfect: MIN 21 - CHI 27 (CHI wins)")
    simulate_scenario(21, 25, "RAYMOND Perfect: MIN 21 - CHI 25 (CHI wins)")
    simulate_scenario(17, 24, "VIZCA Perfect: MIN 17 - CHI 24 (CHI wins)")
    
    print(f"\n🔥 MINNESOTA WINS SCENARIOS:")
    # Minnesota actually wins - test the MIN pickers
    simulate_scenario(21, 20, "MIN Wins: MIN 21 - CHI 20 (close to Coyote/Raymond)")
    simulate_scenario(17, 16, "MIN Wins: MIN 17 - CHI 16 (close to Vizca)")
    simulate_scenario(25, 20, "MIN Wins: MIN 25 - CHI 20 (high scoring)")
    simulate_scenario(14, 10, "MIN Wins: MIN 14 - CHI 10 (low scoring)")
    
    print(f"\n🔥 COMPETITIVE MIN WIN SCENARIOS:")
    # Close calls where different players could win
    simulate_scenario(20, 18, "Close MIN Win: MIN 20 - CHI 18")
    simulate_scenario(18, 15, "Low Scoring MIN Win: MIN 18 - CHI 15")
    simulate_scenario(24, 22, "Mid-Range MIN Win: MIN 24 - CHI 22")

if __name__ == "__main__":
    print("🏈 LA CASA DE TODOS - COMPREHENSIVE MONDAY NIGHT ANALYSIS")
    print("=" * 80)
    
    # Run the comprehensive winning conditions analysis
    analyze_winning_conditions()
    
    # Create detailed winning map 
    winning_map = create_winning_map()
    
    # Show specific examples
    show_specific_examples()
    
    print(f"\n🎯 FINAL SUMMARY:")
    print("=" * 50)
    print("🏆 RAMFIS: Wins ANY time Chicago beats Minnesota")
    print("   - Only player who picked CHI to win")
    print("   - Optimal: MIN 19 - CHI 22 (exact prediction)")
    print()
    print("🏆 COYOTE: Wins when MIN wins with scores close to MIN 21 - CHI 27")
    print("   - Needs Minnesota victory + closest to his prediction")
    print()
    print("🏆 RAYMOND: Wins when MIN wins with scores close to MIN 21 - CHI 25") 
    print("   - Needs Minnesota victory + closest to his prediction")
    print()
    print("🏆 VIZCA: Wins when MIN wins with scores close to MIN 17 - CHI 24")
    print("   - Needs Minnesota victory + closest to his prediction")
    print()
    print("💡 KEY INSIGHT: Ramfis has BIG advantage - wins 50% of all possible")
    print("   game outcomes (whenever CHI wins). Other 3 split MIN win scenarios.")
