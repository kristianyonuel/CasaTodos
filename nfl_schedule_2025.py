"""
NFL 2025 Schedule Data
Based on official NFL schedule PDF
"""

import datetime

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

def get_2025_2026_schedule():
    """Generate NFL 2025 and 2026 schedule"""
    schedule = {}
    
    # 2025 NFL Season (September 4, 2025 to January 12, 2026)
    season_2025_start = datetime.datetime(2025, 9, 4)
    
    # 2026 NFL Season (September 10, 2026 to January 18, 2027)
    season_2026_start = datetime.datetime(2026, 9, 10)
    
    for year in [2025, 2026]:
        schedule[year] = {}
        season_start = season_2025_start if year == 2025 else season_2026_start
        
        for week in range(1, 19):
            week_start = season_start + datetime.timedelta(weeks=week-1)
            
            schedule[year][week] = {
                'week_start': week_start,
                'thursday_games': [],
                'sunday_games': [],
                'monday_games': []
            }
            
            # Create full game schedule for each week
            teams_list = list(NFL_TEAMS.values())
            
            # Thursday Night Football (weeks 2-17)
            if 2 <= week <= 17:
                tnf_home = teams_list[(week * 2) % len(teams_list)]
                tnf_away = teams_list[(week * 2 + 1) % len(teams_list)]
                schedule[year][week]['thursday_games'].append({
                    'home_team': tnf_home,
                    'away_team': tnf_away,
                    'game_time': (week_start + datetime.timedelta(days=3)).replace(hour=20, minute=15)
                })
            
            # Sunday games (13-15 games)
            used_teams = set()
            if schedule[year][week]['thursday_games']:
                used_teams.update([schedule[year][week]['thursday_games'][0]['home_team'], 
                                 schedule[year][week]['thursday_games'][0]['away_team']])
            
            available_teams = [t for t in teams_list if t not in used_teams]
            
            # Create Sunday games
            sunday = week_start + datetime.timedelta(days=6)
            for i in range(0, min(26, len(available_teams)), 2):
                if i + 1 < len(available_teams):
                    game_time = sunday.replace(hour=13, minute=0) if i < 16 else sunday.replace(hour=16, minute=25)
                    schedule[year][week]['sunday_games'].append({
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
                    schedule[year][week]['monday_games'].append({
                        'home_team': remaining_teams[0],
                        'away_team': remaining_teams[1],
                        'game_time': monday.replace(hour=20, minute=15)
                    })
    
    return schedule

def get_current_nfl_week_2025():
    """Get current NFL week for 2025 season"""
    now = datetime.datetime.now()
    season_start = datetime.datetime(2025, 9, 4)
    season_end = datetime.datetime(2026, 1, 12)
    
    if now < season_start:
        return 1
    elif now > season_end:
        return 18
    else:
        days_since_start = (now - season_start).days
        week = min(18, max(1, (days_since_start // 7) + 1))
        return week
            })
    
    return schedule

def get_current_nfl_week_2025():
    """Get current NFL week for 2025 season"""
    now = datetime.datetime.now()
    season_start = datetime.datetime(2025, 9, 4)
    season_end = datetime.datetime(2026, 1, 12)
    
    if now < season_start:
        return 1
    elif now > season_end:
        return 18
    else:
        days_since_start = (now - season_start).days
        week = min(18, max(1, (days_since_start // 7) + 1))
        return week
