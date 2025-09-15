#!/usr/bin/env python3
"""
Predictable Winner Analysis for Monday Night Football
Analyzes potential weekly winners based on different game outcomes
"""

import sqlite3
from typing import Dict, List, Tuple, Optional

def analyze_predictable_winners(week: int = 1, year: int = 2025) -> Dict:
    """
    Analyze potential weekly winners based on ALL Monday Night Football outcomes
    Handles multiple Monday games in sequence (TB@HOU, then LAC@LV)
    
    Returns:
        Dict containing analysis of potential winners for each game outcome
    """
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get ALL Monday Night games (in chronological order)
    cursor.execute('''
        SELECT id, home_team, away_team, is_final, game_date
        FROM nfl_games 
        WHERE week = ? AND year = ? 
        AND strftime('%w', game_date) = '1'
        AND is_final = 0
        ORDER BY game_date ASC, id ASC
    ''', (week, year))
    
    monday_games = cursor.fetchall()
    if not monday_games:
        conn.close()
        return {'error': 'No Monday Night games found'}
    
    # Get current weekly standings (before Monday Night games)
    cursor.execute('''
        SELECT u.id, u.username, 
               COUNT(CASE WHEN p.is_correct = 1 THEN 1 END) as correct_picks
        FROM users u
        JOIN user_picks p ON u.id = p.user_id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.week = ? AND g.year = ? AND g.is_final = 1 AND u.is_admin = 0
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC, u.username
    ''', (week, year))
    
    current_standings = cursor.fetchall()
    if not current_standings:
        conn.close()
        return {'error': 'No completed games found for this week'}
    
    # Get picks for ALL Monday games
    monday_game_ids = [game[0] for game in monday_games]
    placeholders = ','.join(['?' for _ in monday_game_ids])
    
    cursor.execute(f'''
        SELECT u.id, u.username, g.id as game_id, g.home_team, g.away_team,
               p.predicted_home_score, p.predicted_away_score, p.selected_team
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        JOIN nfl_games g ON p.game_id = g.id
        WHERE g.id IN ({placeholders}) AND u.is_admin = 0
        ORDER BY g.game_date ASC, u.username
    ''', monday_game_ids)
    
    all_monday_picks = cursor.fetchall()
    
    # Organize picks by game and user
    monday_picks_by_game = {}
    user_standings = {user_id: {'username': username, 'current_wins': wins} 
                     for user_id, username, wins in current_standings}
    
    for user_id, username, game_id, home_team, away_team, pred_home, pred_away, selected_team in all_monday_picks:
        if game_id not in monday_picks_by_game:
            monday_picks_by_game[game_id] = {
                'home_team': home_team,
                'away_team': away_team,
                'picks': {}
            }
        
        # Handle None values in predictions
        safe_home = pred_home if pred_home is not None else 0
        safe_away = pred_away if pred_away is not None else 0
        
        monday_picks_by_game[game_id]['picks'][user_id] = {
            'username': username,
            'predicted_home': safe_home,
            'predicted_away': safe_away,
            'predicted_total': safe_home + safe_away,
            'selected_team': selected_team
        }
    
    # Analyze scenarios for multiple Monday games
    analysis = analyze_monday_scenarios(monday_games, monday_picks_by_game, user_standings)
    
    conn.close()
    return analysis


def analyze_monday_scenarios(monday_games, picks_by_game, user_standings):
    """Analyze all possible outcomes for multiple Monday games"""
    
    if len(monday_games) == 1:
        # Single Monday game - use existing logic
        return analyze_single_monday_game(monday_games[0], picks_by_game, user_standings)
    
    elif len(monday_games) == 2:
        # Two Monday games - analyze TB@HOU first, then LAC@LV
        return analyze_two_monday_games(monday_games, picks_by_game, user_standings)
    
    else:
        # More than 2 games - general case
        return analyze_multiple_monday_games(monday_games, picks_by_game, user_standings)


def analyze_two_monday_games(monday_games, picks_by_game, user_standings):
    """Analyze scenario with exactly 2 Monday games (like TB@HOU, LAC@LV)"""
    
    game1_id, game1_home, game1_away, _, _ = monday_games[0]  # TB@HOU
    game2_id, game2_home, game2_away, _, _ = monday_games[1]  # LAC@LV
    
    game1_info = picks_by_game.get(game1_id, {'home_team': game1_home, 'away_team': game1_away, 'picks': {}})
    game2_info = picks_by_game.get(game2_id, {'home_team': game2_home, 'away_team': game2_away, 'picks': {}})
    
    # Find current leader(s)
    max_wins = max(user['current_wins'] for user in user_standings.values())
    current_leaders = [user for user in user_standings.values() if user['current_wins'] == max_wins]
    
    scenarios = {}
    
    # Scenario 1: Game 1 Home wins (HOU wins), Game 2 Home wins (LV wins)
    scenario_key = f"{game1_home} wins, {game2_home} wins"
    winners_after_both = calculate_winners_after_games(
        user_standings, 
        [(game1_id, game1_home), (game2_id, game2_home)], 
        picks_by_game
    )
    scenarios[scenario_key] = create_scenario_summary(winners_after_both, scenario_key)
    
    # Scenario 2: Game 1 Home wins (HOU), Game 2 Away wins (LAC)
    scenario_key = f"{game1_home} wins, {game2_away} wins"
    winners_after_both = calculate_winners_after_games(
        user_standings,
        [(game1_id, game1_home), (game2_id, game2_away)],
        picks_by_game
    )
    scenarios[scenario_key] = create_scenario_summary(winners_after_both, scenario_key)
    
    # Scenario 3: Game 1 Away wins (TB), Game 2 Home wins (LV)
    scenario_key = f"{game1_away} wins, {game2_home} wins"
    winners_after_both = calculate_winners_after_games(
        user_standings,
        [(game1_id, game1_away), (game2_id, game2_home)],
        picks_by_game
    )
    scenarios[scenario_key] = create_scenario_summary(winners_after_both, scenario_key)
    
    # Scenario 4: Game 1 Away wins (TB), Game 2 Away wins (LAC)
    scenario_key = f"{game1_away} wins, {game2_away} wins"
    winners_after_both = calculate_winners_after_games(
        user_standings,
        [(game1_id, game1_away), (game2_id, game2_away)],
        picks_by_game
    )
    scenarios[scenario_key] = create_scenario_summary(winners_after_both, scenario_key)
    
    return {
        'game_info': {
            'game1': f"{game1_away} @ {game1_home}",
            'game2': f"{game2_away} @ {game2_home}",
            'total_games': 2
        },
        'current_leaders': {
            'max_wins': max_wins,
            'leaders': [user['username'] for user in current_leaders]
        },
        'scenarios': scenarios
    }


def calculate_winners_after_games(user_standings, game_outcomes, picks_by_game):
    """Calculate final standings after specified game outcomes"""
    
    final_standings = {}
    
    for user_id, user_data in user_standings.items():
        username = user_data['username']
        current_wins = user_data['current_wins']
        additional_wins = 0
        
        # Check each game outcome
        for game_id, winning_team in game_outcomes:
            if game_id in picks_by_game and user_id in picks_by_game[game_id]['picks']:
                user_pick = picks_by_game[game_id]['picks'][user_id]
                if user_pick['selected_team'] == winning_team:
                    additional_wins += 1
        
        final_wins = current_wins + additional_wins
        
        if final_wins not in final_standings:
            final_standings[final_wins] = []
        
        final_standings[final_wins].append({
            'username': username,
            'user_id': user_id,
            'final_wins': final_wins,
            'additional_wins': additional_wins
        })
    
    return final_standings


def create_scenario_summary(final_standings, scenario_description):
    """Create a summary of a scenario outcome"""
    
    if not final_standings:
        return {
            'description': scenario_description,
            'winner': 'No users',
            'tied_users': [],
            'tiebreaker_needed': False
        }
    
    # Find the highest score
    max_score = max(final_standings.keys())
    winners = final_standings[max_score]
    
    if len(winners) == 1:
        return {
            'description': scenario_description,
            'winner': winners[0]['username'],
            'tied_users': [],
            'tiebreaker_needed': False,
            'final_score': max_score
        }
    else:
        return {
            'description': scenario_description,
            'winner': 'TIE',
            'tied_users': [user['username'] for user in winners],
            'tiebreaker_needed': True,
            'final_score': max_score,
            'tie_count': len(winners)
        }


def analyze_single_monday_game(monday_game, picks_by_game, user_standings):
    """Handle single Monday game (fallback to original logic)"""
    
    game_id, home_team, away_team, _, _ = monday_game
    game_info = picks_by_game.get(game_id, {'home_team': home_team, 'away_team': away_team, 'picks': {}})
    
    return {
        'game_info': {
            'home_team': home_team,
            'away_team': away_team,
            'total_games': 1
        },
        'simple_analysis': 'Single Monday game analysis (legacy mode)'
    }


def analyze_multiple_monday_games(monday_games, picks_by_game, user_standings):
    """Handle 3+ Monday games (future expansion)"""
    
    return {
        'game_info': {
            'total_games': len(monday_games),
            'games': [f"{game[2]} @ {game[1]}" for game in monday_games]
        },
        'complex_analysis': f'Multiple Monday games analysis ({len(monday_games)} games)'
    }


def get_winner_prediction_summary(week: int = 1, year: int = 2025) -> str:
    """
    Get a concise summary for displaying on the weekly dashboard
    Updated to show progressive tiebreaker scenarios
    """
    analysis = analyze_predictable_winners(week, year)
    
    if 'error' in analysis:
        return analysis['error']
    
    game_info = analysis['game_info']
    
    # Handle two Monday games case with progressive analysis
    if 'game1' in game_info and 'game2' in game_info:
        game1 = game_info['game1']  # TB@HOU
        game2 = game_info['game2']  # LAC@LV
        
        # Get current standings
        try:
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            # Get current leader
            cursor.execute('''
                SELECT u.username, COUNT(CASE WHEN g.is_final = 1 AND p.is_correct = 1 THEN 1 END) as wins
                FROM users u
                JOIN user_picks p ON u.id = p.user_id  
                JOIN nfl_games g ON p.game_id = g.id
                WHERE g.week = ? AND g.year = ? AND u.is_admin = 0
                GROUP BY u.id, u.username
                ORDER BY wins DESC, u.username
                LIMIT 1
            ''', (week, year))
            
            leader_data = cursor.fetchone()
            if leader_data:
                current_leader, current_wins = leader_data
                
                # Check who has Houston pick
                cursor.execute('''
                    SELECT u.username FROM users u
                    JOIN user_picks p ON u.id = p.user_id
                    JOIN nfl_games g ON p.game_id = g.id
                    WHERE g.week = ? AND g.year = ? AND g.home_team = 'HOU' 
                    AND p.selected_team = 'HOU' AND u.is_admin = 0
                ''', (week, year))
                
                houston_pickers = [row[0] for row in cursor.fetchall()]
                
                conn.close()
                
                # Create progressive summary
                if houston_pickers:
                    houston_names = ', '.join(houston_pickers[:2])
                    if len(houston_pickers) > 2:
                        houston_names += f" +{len(houston_pickers)-2}"
                    
                    return (f"🎯 {current_leader} leads with {current_wins} wins → "
                           f"If HOU wins: {houston_names} catch up → "
                           f"Then {game2} + score predictions decide winner")
                
            conn.close()
        except Exception as e:
            pass
        
        # Fallback to scenario analysis
        scenarios = analysis.get('scenarios', {})
        if scenarios:
            return f"🎯 {game1} then {game2}: Multiple tiebreaker scenarios in play"
        else:
            return f"📊 Analyzing {game1} & {game2} scenarios..."
    
    # Single Monday game case
    elif 'home_team' in game_info:
        return f"📊 Monday: {game_info['away_team']} @ {game_info['home_team']} - Single game analysis"
    
    # Fallback
    return "📊 Monday Night analysis available"


if __name__ == "__main__":
    # Run analysis for current week
    result = analyze_predictable_winners(2, 2025)  # Test with Week 2
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print("� MONDAY NIGHT PREDICTABLE WINNER ANALYSIS")
        print("=" * 50)
        
        game_info = result['game_info']
        if 'game1' in game_info:
            print(f"Game 1: {game_info['game1']}")
            print(f"Game 2: {game_info['game2']}")
            
            scenarios = result.get('scenarios', {})
            for scenario_key, scenario in scenarios.items():
                print(f"\n{scenario_key}:")
                if scenario['tiebreaker_needed']:
                    tied = ', '.join(scenario['tied_users'])
                    print(f"  → {tied} tied with {scenario['final_score']} wins")
                else:
                    print(f"  → {scenario['winner']} wins with {scenario['final_score']} wins")
        
        print("\nSummary:")
        summary = get_winner_prediction_summary(2, 2025)
        print(summary)
        print("=" * 50)
