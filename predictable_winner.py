#!/usr/bin/env python3
"""
Predictable Winner Analysis for Monday Night Football
Analyzes potential weekly winners based on different game outcomes
"""

import sqlite3
from typing import Dict, List, Tuple, Optional

def analyze_predictable_winners(week: int = 1, year: int = 2025) -> Dict:
    """
    Analyze potential weekly winners based on Monday Night Football outcomes
    
    Returns:
        Dict containing analysis of potential winners for each game outcome
    """
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get Monday Night game
    cursor.execute('''
        SELECT id, home_team, away_team, is_final 
        FROM nfl_games 
        WHERE week = ? AND year = ? AND is_monday_night = 1
        LIMIT 1
    ''', (week, year))
    
    mnf_game = cursor.fetchone()
    if not mnf_game:
        conn.close()
        return {'error': 'No Monday Night game found'}
    
    game_id, home_team, away_team, is_final = mnf_game
    
    if is_final:
        conn.close()
        return {'error': 'Monday Night game is already final'}
    
    # Get current weekly standings (before Monday Night)
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
    
    max_wins = current_standings[0][2]
    
    # Only consider users who can mathematically still win
    # They need to be able to reach max_wins + 1 with Monday Night game
    contenders = []
    eliminated = []
    
    for user_id, username, wins in current_standings:
        max_possible = wins + 1  # +1 if they get Monday Night correct
        if max_possible >= max_wins + 1:  # Can tie or beat current leader
            contenders.append((user_id, username, wins))
        else:
            eliminated.append((user_id, username, wins, max_possible))
    
    if not contenders:
        conn.close()
        return {'error': 'No users can mathematically win this week'}
    
    # Get Monday Night picks
    cursor.execute('''
        SELECT u.id, u.username, p.predicted_home_score, p.predicted_away_score, p.selected_team
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        WHERE p.game_id = ? AND u.is_admin = 0
        ORDER BY u.username
    ''', (game_id,))
    
    mnf_picks = cursor.fetchall()
    
    # Categorize picks by team choice using selected_team field
    home_pickers = []  # Users who picked home team to win
    away_pickers = []  # Users who picked away team to win
    
    for user_id, username, pred_home, pred_away, selected_team in mnf_picks:
        pick_data = {
            'user_id': user_id,
            'username': username,
            'predicted_home': pred_home,
            'predicted_away': pred_away,
            'predicted_total': pred_home + pred_away,
            'selected_team': selected_team
        }
        
        if selected_team == home_team:
            home_pickers.append(pick_data)
        else:
            away_pickers.append(pick_data)
    
    # Analysis for each outcome
    analysis = {
        'game_info': {
            'home_team': home_team,
            'away_team': away_team,
            'total_picks': len(mnf_picks)
        },
        'current_leaders': {
            'max_wins': max_wins,
            'contenders_count': len(contenders),
            'contenders': [{'username': username, 'wins': wins} for _, username, wins in contenders],
            'eliminated_count': len(eliminated),
            'eliminated': [{'username': username, 'wins': wins, 'max_possible': max_poss} 
                          for _, username, wins, max_poss in eliminated]
        },
        'pick_distribution': {
            'home_team': {
                'team': home_team,
                'count': len(home_pickers),
                'users': [p['username'] for p in home_pickers],
                'contenders': [p['username'] for p in home_pickers 
                              if any(p['username'] == c[1] for c in contenders)]
            },
            'away_team': {
                'team': away_team,
                'count': len(away_pickers),
                'users': [p['username'] for p in away_pickers],
                'contenders': [p['username'] for p in away_pickers 
                              if any(p['username'] == c[1] for c in contenders)]
            }
        },
        'scenarios': {}
    }
    
    # Scenario 1: Home team wins
    if home_pickers:
        # Only consider contenders who picked home team
        home_contender_winners = []
        for picker in home_pickers:
            # Check if this picker is a contender
            contender_data = next((c for c in contenders if c[1] == picker['username']), None)
            if contender_data:
                user_id, username, current_wins = contender_data
                new_wins = current_wins + 1
                home_contender_winners.append({
                    'username': username,
                    'current_wins': current_wins,
                    'new_wins': new_wins,
                    'predicted_total': picker['predicted_total'],
                    'predicted_home': picker['predicted_home'],
                    'predicted_away': picker['predicted_away']
                })
        
        # Sort by new wins, then by predicted total for tiebreaking
        home_contender_winners.sort(key=lambda x: (-x['new_wins'], x['predicted_total']))
        
        analysis['scenarios']['home_wins'] = {
            'outcome': f'{home_team} wins',
            'total_correct': len(home_pickers),
            'contender_winners': home_contender_winners,
            'can_win': len(home_contender_winners) > 0,
            'winner_decided': len(home_contender_winners) == 1,
            'tiebreaker_needed': len(home_contender_winners) > 1
        }
    
    # Scenario 2: Away team wins
    if away_pickers:
        # Only consider contenders who picked away team
        away_contender_winners = []
        for picker in away_pickers:
            contender_data = next((c for c in contenders if c[1] == picker['username']), None)
            if contender_data:
                user_id, username, current_wins = contender_data
                new_wins = current_wins + 1
                away_contender_winners.append({
                    'username': username,
                    'current_wins': current_wins,
                    'new_wins': new_wins,
                    'predicted_total': picker['predicted_total'],
                    'predicted_home': picker['predicted_home'],
                    'predicted_away': picker['predicted_away']
                })
        
        away_contender_winners.sort(key=lambda x: (-x['new_wins'], x['predicted_total']))
        
        analysis['scenarios']['away_wins'] = {
            'outcome': f'{away_team} wins',
            'total_correct': len(away_pickers),
            'contender_winners': away_contender_winners,
            'can_win': len(away_contender_winners) > 0,
            'winner_decided': len(away_contender_winners) == 1,
            'tiebreaker_needed': len(away_contender_winners) > 1
        }
    
    # Special case: Everyone picked the same team
    if len(home_pickers) == 0 or len(away_pickers) == 0:
        # Count how many contenders picked each team
        home_contenders = [p for p in home_pickers if any(p['username'] == c[1] for c in contenders)]
        away_contenders = [p for p in away_pickers if any(p['username'] == c[1] for c in contenders)]
        
        if len(home_pickers) == len(mnf_picks):
            # Everyone picked home team
            analysis['special_case'] = {
                'type': 'unanimous_home',
                'description': f'ALL {len(mnf_picks)} users picked {home_team} to win',
                'contenders_with_pick': len(home_contenders),
                'if_correct': 'Winner decided by Monday Night total score tiebreaker among leaders',
                'if_wrong': f'All {len(contenders)} contenders stay at {max_wins} wins - tied for 1st!'
            }
        else:
            # Everyone picked away team
            analysis['special_case'] = {
                'type': 'unanimous_away',
                'description': f'ALL {len(mnf_picks)} users picked {away_team} to win',
                'contenders_with_pick': len(away_contenders),
                'if_correct': 'Winner decided by Monday Night total score tiebreaker among leaders',
                'if_wrong': f'All {len(contenders)} contenders stay at {max_wins} wins - tied for 1st!'
            }
    
    conn.close()
    return analysis

def get_winner_prediction_summary(week: int = 1, year: int = 2025) -> str:
    """
    Get a concise summary for displaying on the weekly dashboard
    """
    analysis = analyze_predictable_winners(week, year)
    
    if 'error' in analysis:
        return analysis['error']
    
    game = analysis['game_info']
    leaders = analysis['current_leaders']
    
    if 'special_case' in analysis:
        case = analysis['special_case']
        
        if case['type'] == 'unanimous_home':
            return (f"🎯 ALL users picked {game['home_team']}! "
                   f"Only {leaders['contenders_count']} can win: "
                   f"If {game['home_team']} wins → tiebreaker, "
                   f"If {game['away_team']} wins → {leaders['contenders_count']}-way tie!")
        else:
            return (f"🎯 ALL users picked {game['away_team']}! "
                   f"Only {leaders['contenders_count']} can win: "
                   f"If {game['away_team']} wins → tiebreaker, "
                   f"If {game['home_team']} wins → {leaders['contenders_count']}-way tie!")
    
    scenarios = analysis['scenarios']
    summary_parts = []
    
    for scenario_key, scenario in scenarios.items():
        if scenario['winner_decided'] and scenario['can_win']:
            winner = scenario['contender_winners'][0]['username']
            summary_parts.append(f"If {scenario['outcome']} → {winner} wins!")
        elif scenario['can_win']:
            count = len(scenario['contender_winners'])
            summary_parts.append(f"If {scenario['outcome']} → {count} contenders, tiebreaker needed")
        else:
            summary_parts.append(f"If {scenario['outcome']} → No change in leaders")
    
    return " | ".join(summary_parts) if summary_parts else "No clear prediction available"

if __name__ == "__main__":
    # Run analysis for current week
    result = analyze_predictable_winners()
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print("🏈 MONDAY NIGHT PREDICTABLE WINNER ANALYSIS")
        print("=" * 50)
        
        game = result['game_info']
        print(f"Game: {game['away_team']} @ {game['home_team']}")
        
        leaders = result['current_leaders']
        print(f"Current Leaders: {leaders['contenders_count']} contenders with {leaders['max_wins']} wins")
        print(f"  Contenders: {', '.join([c['username'] for c in leaders['contenders']])}")
        print(f"  Eliminated: {leaders['eliminated_count']} users")
        
        picks = result['pick_distribution']
        print(f"Pick Distribution:")
        print(f"  {picks['home_team']['team']}: {picks['home_team']['count']} users")
        print(f"    Contenders who picked {picks['home_team']['team']}: {picks['home_team']['contenders']}")
        print(f"  {picks['away_team']['team']}: {picks['away_team']['count']} users")
        print(f"    Contenders who picked {picks['away_team']['team']}: {picks['away_team']['contenders']}")
        
        if 'special_case' in result:
            case = result['special_case']
            print(f"\n🎯 SPECIAL CASE: {case['description']}")
            print(f"  Contenders with this pick: {case['contenders_with_pick']}")
            print(f"  If correct: {case['if_correct']}")
            print(f"  If wrong: {case['if_wrong']}")
        
        print(f"\n📝 Dashboard Summary:")
        print(get_winner_prediction_summary())
