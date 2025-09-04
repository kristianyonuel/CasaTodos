"""
NFL Schedule Generator for 2025-2026 seasons
"""

import datetime
import pytz

# NFL Teams with their abbreviations
NFL_TEAMS = {
    'Arizona Cardinals': 'ARI',
    'Atlanta Falcons': 'ATL',
    'Baltimore Ravens': 'BAL',
    'Buffalo Bills': 'BUF',
    'Carolina Panthers': 'CAR',
    'Chicago Bears': 'CHI',
    'Cincinnati Bengals': 'CIN',
    'Cleveland Browns': 'CLE',
    'Dallas Cowboys': 'DAL',
    'Denver Broncos': 'DEN',
    'Detroit Lions': 'DET',
    'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU',
    'Indianapolis Colts': 'IND',
    'Jacksonville Jaguars': 'JAX',
    'Kansas City Chiefs': 'KC',
    'Las Vegas Raiders': 'LV',
    'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LAR',
    'Miami Dolphins': 'MIA',
    'Minnesota Vikings': 'MIN',
    'New England Patriots': 'NE',
    'New Orleans Saints': 'NO',
    'New York Giants': 'NYG',
    'New York Jets': 'NYJ',
    'Philadelphia Eagles': 'PHI',
    'Pittsburgh Steelers': 'PIT',
    'San Francisco 49ers': 'SF',
    'Seattle Seahawks': 'SEA',
    'Tampa Bay Buccaneers': 'TB',
    'Tennessee Titans': 'TEN',
    'Washington Commanders': 'WAS'
}

def get_current_nfl_week():
    """Get current NFL week based on calendar"""
    now = datetime.datetime.now()
    
    if now.year >= 2025:
        season_start = datetime.datetime(2025, 9, 4)
        season_end = datetime.datetime(2026, 1, 12)
    else:
        season_start = datetime.datetime(2024, 9, 5)
        season_end = datetime.datetime(2025, 1, 8)
    
    if now < season_start:
        return 1
    elif now > season_end:
        return 18
    else:
        days_since_start = (now - season_start).days
        week = min(18, max(1, (days_since_start // 7) + 1))
        return week

def generate_schedule_for_year(year):
    """Generate NFL schedule for a specific year"""
    schedule = {}
    
    if year == 2025:
        season_start = datetime.datetime(2025, 9, 4)
    elif year == 2026:
        season_start = datetime.datetime(2026, 9, 10)
    else:
        season_start = datetime.datetime(year, 9, 7)
    
    teams_list = list(NFL_TEAMS.values())
    
    for week in range(1, 19):
        week_start = season_start + datetime.timedelta(weeks=week-1)
        
        schedule[week] = {
            'thursday_games': [],
            'sunday_games': [],
            'monday_games': []
        }
        
        # Thursday Night Football (weeks 2-17)
        if 2 <= week <= 17:
            thursday = week_start + datetime.timedelta(days=3)
            home_team = teams_list[(week * 2) % len(teams_list)]
            away_team = teams_list[(week * 2 + 1) % len(teams_list)]
            
            schedule[week]['thursday_games'].append({
                'home_team': home_team,
                'away_team': away_team,
                'game_time': thursday.replace(hour=20, minute=15)
            })
        
        # Sunday games
        used_teams = set()
        if schedule[week]['thursday_games']:
            tnf_game = schedule[week]['thursday_games'][0]
            used_teams.update([tnf_game['home_team'], tnf_game['away_team']])
        
        available_teams = [t for t in teams_list if t not in used_teams]
        sunday = week_start + datetime.timedelta(days=6)
        
        # Create Sunday games
        for i in range(0, min(26, len(available_teams)), 2):
            if i + 1 < len(available_teams):
                game_time = sunday.replace(hour=13, minute=0) if i < 16 else sunday.replace(hour=16, minute=25)
                schedule[week]['sunday_games'].append({
                    'home_team': available_teams[i],
                    'away_team': available_teams[i + 1],
                    'game_time': game_time
                })
                used_teams.update([available_teams[i], available_teams[i + 1]])
        
        # Monday Night Football (weeks 1-17)
        if week <= 17:
            remaining_teams = [t for t in teams_list if t not in used_teams]
            if len(remaining_teams) >= 2:
                monday = week_start + datetime.timedelta(days=7)
                schedule[week]['monday_games'].append({
                    'home_team': remaining_teams[0],
                    'away_team': remaining_teams[1],
                    'game_time': monday.replace(hour=20, minute=15)
                })
    
    return schedule
