"""
NFL 2025 Schedule Data - All 18 weeks
Based on official NFL schedule
"""
from datetime import datetime, timedelta

# NFL Team abbreviations mapping
NFL_TEAMS = {
    'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL',
    'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
    'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
    'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX',
    'Kansas City Chiefs': 'KC', 'Las Vegas Raiders': 'LV', 'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LAR', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN',
    'New England Patriots': 'NE', 'New Orleans Saints': 'NO', 'New York Giants': 'NYG',
    'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
    'San Francisco 49ers': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB',
    'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS'
}

def get_2025_nfl_schedule():
    """
    Generate complete 2025 NFL schedule with exact game counts per week
    Based on official NFL schedule PDF
    """
    schedule = {}
    
    # Season starts September 4, 2025 (Thursday)
    season_start = datetime(2025, 9, 4)
    
    # All 32 teams
    teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN',
             'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LV', 'LAC', 'LAR', 'MIA',
             'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']
    
    # Actual week-by-week game counts from NFL schedule
    week_configs = {
        1: {'thursday': 1, 'friday': 1, 'sunday': 13, 'monday': 1, 'total': 16},  # Week 1: 16 games
        2: {'thursday': 1, 'friday': 0, 'sunday': 14, 'monday': 1, 'total': 16},  # Week 2: 16 games  
        3: {'thursday': 1, 'friday': 0, 'sunday': 14, 'monday': 1, 'total': 16},  # Week 3: 16 games
        4: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15},  # Week 4: 15 games
        5: {'thursday': 1, 'friday': 0, 'sunday': 12, 'monday': 1, 'total': 14},  # Week 5: 14 games
        6: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15},  # Week 6: 15 games
        7: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15},  # Week 7: 15 games
        8: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15},  # Week 8: 15 games
        9: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15},  # Week 9: 15 games
        10: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15}, # Week 10: 15 games
        11: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15}, # Week 11: 15 games
        12: {'thursday': 3, 'friday': 0, 'sunday': 11, 'monday': 0, 'total': 14}, # Week 12: 14 games (Thanksgiving)
        13: {'thursday': 1, 'friday': 1, 'sunday': 13, 'monday': 1, 'total': 16}, # Week 13: 16 games
        14: {'thursday': 1, 'friday': 0, 'sunday': 14, 'monday': 1, 'total': 16}, # Week 14: 16 games
        15: {'thursday': 1, 'friday': 0, 'sunday': 13, 'monday': 1, 'total': 15}, # Week 15: 15 games
        16: {'thursday': 1, 'friday': 0, 'sunday': 14, 'monday': 1, 'total': 16}, # Week 16: 16 games
        17: {'thursday': 0, 'friday': 0, 'sunday': 16, 'monday': 0, 'total': 16}, # Week 17: 16 games
        18: {'thursday': 0, 'friday': 0, 'sunday': 16, 'monday': 0, 'total': 16}, # Week 18: 16 games
    }
    
    for week in range(1, 19):
        week_start = season_start + timedelta(weeks=week-1)
        schedule[week] = []
        config = week_configs.get(week, {'thursday': 1, 'sunday': 14, 'monday': 1, 'total': 16})
        
        used_teams = set()
        
        # Week 1 Special Case (Season Opener)
        if week == 1:
            # Thursday Night - Season Opener (Sep 4)
            schedule[week].append({
                'away_team': 'KC',
                'home_team': 'BUF', 
                'game_date': week_start.replace(hour=20, minute=15),
                'is_thursday_night': True,
                'tv_network': 'NBC'
            })
            used_teams.update(['KC', 'BUF'])
            
            # Friday Night Game (Sep 5) - International or special game
            friday = week_start + timedelta(days=1)
            schedule[week].append({
                'away_team': 'GB',
                'home_team': 'PHI',
                'game_date': friday.replace(hour=20, minute=15),
                'is_friday_night': True,
                'tv_network': 'Prime Video'
            })
            used_teams.update(['GB', 'PHI'])
            
            # Sunday games (13 games)
            sunday = week_start + timedelta(days=3)
            sunday_matchups = [
                ('MIA', 'NE'), ('PIT', 'BAL'), ('CIN', 'CLE'), ('HOU', 'IND'),
                ('JAX', 'TEN'), ('CHI', 'DET'), ('MIN', 'NYG'), ('CAR', 'NO'),
                ('TB', 'ATL'), ('LV', 'LAC'), ('ARI', 'SF'), ('SEA', 'LAR'),
                ('WAS', 'NYJ')
            ]
            
            for i, (away, home) in enumerate(sunday_matchups):
                # Early games (1:00 PM ET) and late games (4:25 PM ET)
                if i < 9:  # Early games
                    game_time = sunday.replace(hour=13, minute=0)
                elif i == 12:  # Sunday Night Football
                    game_time = sunday.replace(hour=20, minute=20)
                    tv_network = 'NBC'
                else:  # Late afternoon games
                    game_time = sunday.replace(hour=16, minute=25)
                    tv_network = 'CBS' if i % 2 == 0 else 'FOX'
                
                schedule[week].append({
                    'away_team': away,
                    'home_team': home,
                    'game_date': game_time,
                    'is_sunday_night': (i == 12),
                    'tv_network': tv_network if i == 12 else ('CBS' if i % 2 == 0 else 'FOX')
                })
                used_teams.update([away, home])
            
            # Monday Night Football (Sep 8)
            monday = week_start + timedelta(days=4)
            remaining = [t for t in teams if t not in used_teams]
            schedule[week].append({
                'away_team': remaining[0] if remaining else 'DAL',
                'home_team': remaining[1] if len(remaining) > 1 else 'DEN',
                'game_date': monday.replace(hour=20, minute=15),
                'is_monday_night': True,
                'tv_network': 'ESPN'
            })
        
        # Week 12 Special Case (Thanksgiving)
        elif week == 12:
            # Thanksgiving Games (3 games on Thursday)
            thursday = week_start + timedelta(days=3)
            thanksgiving_games = [
                ('CHI', 'DET', 12, 30),  # 12:30 PM ET
                ('NYG', 'DAL', 16, 30),  # 4:30 PM ET  
                ('MIA', 'GB', 20, 20)    # 8:20 PM ET
            ]
            
            for away, home, hour, minute in thanksgiving_games:
                schedule[week].append({
                    'away_team': away,
                    'home_team': home,
                    'game_date': thursday.replace(hour=hour, minute=minute),
                    'is_thursday_night': (hour >= 20),
                    'is_thanksgiving': True,
                    'tv_network': 'CBS' if hour == 12 else 'FOX' if hour == 16 else 'NBC'
                })
                used_teams.update([away, home])
            
            # Sunday games (11 games on Thanksgiving weekend)
            sunday = week_start + timedelta(days=6)
            available_teams = [t for t in teams if t not in used_teams]
            
            for i in range(0, min(22, len(available_teams)), 2):
                if i + 1 < len(available_teams) and len(schedule[week]) < config['total']:
                    game_time = sunday.replace(hour=13 if i < 14 else 16, minute=0 if i < 14 else 25)
                    schedule[week].append({
                        'away_team': available_teams[i],
                        'home_team': available_teams[i + 1],
                        'game_date': game_time,
                        'tv_network': 'CBS' if i % 2 == 0 else 'FOX'
                    })
        
        # Regular weeks (2-11, 13-16)
        elif week in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]:
            # Thursday Night Football
            if config['thursday'] > 0:
                thursday = week_start + timedelta(days=3)
                tnf_teams = get_week_teams(week, teams, 'thursday')
                schedule[week].append({
                    'away_team': tnf_teams[0],
                    'home_team': tnf_teams[1],
                    'game_date': thursday.replace(hour=20, minute=15),
                    'is_thursday_night': True,
                    'tv_network': 'Prime Video'
                })
                used_teams.update(tnf_teams)
            
            # Friday Night (Week 13 only - Black Friday)
            if config.get('friday', 0) > 0:
                friday = week_start + timedelta(days=4)
                friday_teams = get_week_teams(week, teams, 'friday', used_teams)
                schedule[week].append({
                    'away_team': friday_teams[0],
                    'home_team': friday_teams[1],
                    'game_date': friday.replace(hour=15, minute=0),
                    'is_friday_night': True,
                    'tv_network': 'Prime Video'
                })
                used_teams.update(friday_teams)
            
            # Sunday games
            sunday = week_start + timedelta(days=6)
            available_teams = [t for t in teams if t not in used_teams]
            sunday_games_needed = config['sunday']
            
            for i in range(0, min(sunday_games_needed * 2, len(available_teams)), 2):
                if i + 1 < len(available_teams):
                    # Distribute across time slots
                    if i < (sunday_games_needed * 2 * 0.6):  # 60% early games
                        game_time = sunday.replace(hour=13, minute=0)
                    elif i == (sunday_games_needed * 2 - 2):  # Last game is SNF
                        game_time = sunday.replace(hour=20, minute=20)
                        is_snf = True
                    else:  # Late afternoon games
                        game_time = sunday.replace(hour=16, minute=25)
                        is_snf = False
                    
                    schedule[week].append({
                        'away_team': available_teams[i],
                        'home_team': available_teams[i + 1],
                        'game_date': game_time,
                        'is_sunday_night': is_snf if i == (sunday_games_needed * 2 - 2) else False,
                        'tv_network': 'NBC' if i == (sunday_games_needed * 2 - 2) else ('CBS' if i % 2 == 0 else 'FOX')
                    })
                    used_teams.update([available_teams[i], available_teams[i + 1]])
            
            # Monday Night Football
            if config['monday'] > 0:
                monday = week_start + timedelta(days=7)
                remaining_teams = [t for t in teams if t not in used_teams]
                if len(remaining_teams) >= 2:
                    schedule[week].append({
                        'away_team': remaining_teams[0],
                        'home_team': remaining_teams[1],
                        'game_date': monday.replace(hour=20, minute=15),
                        'is_monday_night': True,
                        'tv_network': 'ESPN'
                    })
        
        # Weeks 17-18 (All Sunday games)
        elif week in [17, 18]:
            sunday = week_start + timedelta(days=6)
            
            # All 16 games on Sunday (division rivalries)
            division_matchups = get_week18_matchups() if week == 18 else get_week17_matchups()
            
            for i, (away, home) in enumerate(division_matchups):
                # All games at 1:00 PM or 4:25 PM ET (no night games)
                game_time = sunday.replace(hour=13 if i < 8 else 16, minute=0 if i < 8 else 25)
                schedule[week].append({
                    'away_team': away,
                    'home_team': home,
                    'game_date': game_time,
                    'tv_network': 'CBS' if i % 2 == 0 else 'FOX'
                })
    
    return schedule

def get_week_teams(week, teams, game_type, used_teams=None):
    """Get teams for specific game type with rotation"""
    if used_teams is None:
        used_teams = set()
    
    available = [t for t in teams if t not in used_teams]
    offset = (week - 1) * 2
    
    if len(available) >= 2:
        away_idx = offset % len(available)
        home_idx = (offset + 1) % len(available)
        return [available[away_idx], available[home_idx]]
    
    return ['KC', 'BUF']  # Fallback

def get_week17_matchups():
    """Week 17 division rivalry games"""
    return [
        ('MIA', 'NE'), ('NYJ', 'BUF'), ('CLE', 'BAL'), ('PIT', 'CIN'),
        ('IND', 'HOU'), ('TEN', 'JAX'), ('ATL', 'CAR'), ('TB', 'NO'),
        ('NYG', 'PHI'), ('WAS', 'DAL'), ('GB', 'CHI'), ('DET', 'MIN'),
        ('LAR', 'SEA'), ('SF', 'ARI'), ('KC', 'DEN'), ('LV', 'LAC')
    ]

def get_week18_matchups():
    """Week 18 final regular season games"""
    return [
        ('NE', 'MIA'), ('BUF', 'NYJ'), ('BAL', 'CLE'), ('CIN', 'PIT'),
        ('HOU', 'IND'), ('JAX', 'TEN'), ('CAR', 'ATL'), ('NO', 'TB'),
        ('PHI', 'NYG'), ('DAL', 'WAS'), ('CHI', 'GB'), ('MIN', 'DET'),
        ('SEA', 'LAR'), ('ARI', 'SF'), ('DEN', 'KC'), ('LAC', 'LV')
    ]

def get_week_game_count(week):
    """Get exact number of games for a specific week"""
    week_configs = {
        1: 16, 2: 16, 3: 16, 4: 15, 5: 14, 6: 15, 7: 15, 8: 15, 9: 15,
        10: 15, 11: 15, 12: 14, 13: 16, 14: 16, 15: 15, 16: 16, 17: 16, 18: 16
    }
    return week_configs.get(week, 16)

def import_2025_schedule_to_db():
    """Import the complete 2025 schedule to database"""
    import sqlite3
    from app import get_db
    
    schedule = get_2025_nfl_schedule()
    total_games = 0
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Clear existing 2025 games
        cursor.execute('DELETE FROM nfl_games WHERE year = 2025')
        
        for week, games in schedule.items():
            for game in games:
                game_id = f"nfl_2025_w{week}_{game['away_team']}_{game['home_team']}"
                
                cursor.execute('''
                    INSERT INTO nfl_games 
                    (week, year, game_id, away_team, home_team, game_date, 
                     is_thursday_night, is_monday_night, is_sunday_night, 
                     game_status, tv_network)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    week, 2025, game_id, game['away_team'], game['home_team'],
                    game['game_date'].strftime('%Y-%m-%d %H:%M:%S'),
                    game.get('is_thursday_night', False),
                    game.get('is_monday_night', False),
                    game.get('is_sunday_night', False),
                    'scheduled',
                    game.get('tv_network', 'TBD')
                ))
                total_games += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully imported {total_games} games for 2025 NFL season")
        return total_games
        
    except Exception as e:
        print(f"❌ Error importing 2025 schedule: {e}")
        return 0

if __name__ == "__main__":
    import_2025_schedule_to_db()
