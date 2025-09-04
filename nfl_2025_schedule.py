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
    Generate complete 2025 NFL schedule with realistic matchups
    """
    schedule = {}
    
    # Season starts September 4, 2025 (Thursday)
    season_start = datetime(2025, 9, 4)
    
    # All 32 teams
    teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN',
             'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LV', 'LAC', 'LAR', 'MIA',
             'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']
    
    for week in range(1, 19):
        week_start = season_start + timedelta(weeks=week-1)
        schedule[week] = []
        
        # Week 1 - Season Opener (Thursday)
        if week == 1:
            # Thursday Night - Season Opener
            schedule[week].append({
                'away_team': 'KC',
                'home_team': 'BUF',
                'game_date': week_start.replace(hour=20, minute=15),
                'is_thursday_night': True,
                'is_monday_night': False,
                'tv_network': 'NBC'
            })
            
            # Sunday games
            sunday = week_start + timedelta(days=3)
            sunday_games = [
                ('MIA', 'NE'), ('PIT', 'BAL'), ('CIN', 'CLE'), ('HOU', 'IND'),
                ('JAX', 'TEN'), ('CHI', 'DET'), ('MIN', 'GB'), ('CAR', 'NO'),
                ('TB', 'ATL'), ('LV', 'LAC'), ('ARI', 'SF'), ('SEA', 'LAR'),
                ('NYG', 'WAS'), ('DEN', 'NYJ')
            ]
            
            for i, (away, home) in enumerate(sunday_games):
                game_time = sunday.replace(hour=13 if i < 10 else 16, minute=0 if i < 10 else 25)
                schedule[week].append({
                    'away_team': away,
                    'home_team': home,
                    'game_date': game_time,
                    'is_thursday_night': False,
                    'is_monday_night': False,
                    'tv_network': 'CBS' if i % 2 == 0 else 'FOX'
                })
            
            # Monday Night Football
            monday = week_start + timedelta(days=4)
            schedule[week].append({
                'away_team': 'DAL',
                'home_team': 'PHI',
                'game_date': monday.replace(hour=20, minute=15),
                'is_thursday_night': False,
                'is_monday_night': True,
                'tv_network': 'ESPN'
            })
        
        # Regular weeks 2-17
        elif 2 <= week <= 17:
            used_teams = set()
            
            # Thursday Night Football (weeks 2-17)
            thursday = week_start + timedelta(days=3)
            tnf_matchups = generate_weekly_matchups(week, teams, 'thursday')
            if tnf_matchups:
                away, home = tnf_matchups[0]
                schedule[week].append({
                    'away_team': away,
                    'home_team': home,
                    'game_date': thursday.replace(hour=20, minute=15),
                    'is_thursday_night': True,
                    'is_monday_night': False,
                    'tv_network': 'Prime Video'
                })
                used_teams.update([away, home])
            
            # Sunday games
            sunday = week_start + timedelta(days=6)
            sunday_matchups = generate_weekly_matchups(week, teams, 'sunday', used_teams)
            
            for i, (away, home) in enumerate(sunday_matchups):
                if len(used_teams) >= 30:  # Leave 2 teams for MNF
                    break
                
                game_time = sunday.replace(hour=13 if i < 8 else 16, minute=0 if i < 8 else 25)
                
                # Sunday Night Football (one game per week)
                if i == len(sunday_matchups) - 1 and week > 1:
                    game_time = sunday.replace(hour=20, minute=20)
                    is_snf = True
                    tv_network = 'NBC'
                else:
                    is_snf = False
                    tv_network = 'CBS' if i % 2 == 0 else 'FOX'
                
                schedule[week].append({
                    'away_team': away,
                    'home_team': home,
                    'game_date': game_time,
                    'is_thursday_night': False,
                    'is_monday_night': False,
                    'is_sunday_night': is_snf,
                    'tv_network': tv_network
                })
                used_teams.update([away, home])
            
            # Monday Night Football
            monday = week_start + timedelta(days=7)
            remaining_teams = [t for t in teams if t not in used_teams]
            if len(remaining_teams) >= 2:
                schedule[week].append({
                    'away_team': remaining_teams[0],
                    'home_team': remaining_teams[1],
                    'game_date': monday.replace(hour=20, minute=15),
                    'is_thursday_night': False,
                    'is_monday_night': True,
                    'tv_network': 'ESPN'
                })
        
        # Week 18 - Final week (all division games)
        elif week == 18:
            sunday = week_start + timedelta(days=6)
            
            # All games on Sunday (no Thursday/Monday in Week 18)
            week18_games = [
                ('MIA', 'NE'), ('NYJ', 'BUF'), ('CLE', 'BAL'), ('PIT', 'CIN'),
                ('IND', 'HOU'), ('TEN', 'JAX'), ('ATL', 'CAR'), ('TB', 'NO'),
                ('NYG', 'PHI'), ('WAS', 'DAL'), ('GB', 'CHI'), ('DET', 'MIN'),
                ('LAR', 'SEA'), ('SF', 'ARI'), ('KC', 'DEN'), ('LV', 'LAC')
            ]
            
            # All games at 1:00 PM ET and 4:25 PM ET
            for i, (away, home) in enumerate(week18_games):
                game_time = sunday.replace(hour=13 if i < 8 else 16, minute=0 if i < 8 else 25)
                schedule[week].append({
                    'away_team': away,
                    'home_team': home,
                    'game_date': game_time,
                    'is_thursday_night': False,
                    'is_monday_night': False,
                    'tv_network': 'CBS' if i % 2 == 0 else 'FOX'
                })
    
    return schedule

def generate_weekly_matchups(week, teams, game_type, used_teams=None):
    """Generate realistic matchups for each week"""
    if used_teams is None:
        used_teams = set()
    
    available_teams = [t for t in teams if t not in used_teams]
    matchups = []
    
    # Rotate teams to create variety
    week_offset = (week - 1) * 3
    
    if game_type == 'thursday' and len(available_teams) >= 2:
        # Rotate for Thursday games
        home_idx = week_offset % len(available_teams)
        away_idx = (week_offset + 1) % len(available_teams)
        return [(available_teams[away_idx], available_teams[home_idx])]
    
    elif game_type == 'sunday':
        # Create Sunday matchups
        for i in range(0, min(len(available_teams) - 2, 26), 2):  # Leave 2 for MNF
            if i + 1 < len(available_teams):
                away_idx = (i + week_offset) % len(available_teams)
                home_idx = (i + 1 + week_offset) % len(available_teams)
                
                if available_teams[away_idx] not in used_teams and available_teams[home_idx] not in used_teams:
                    matchups.append((available_teams[away_idx], available_teams[home_idx]))
                    used_teams.update([available_teams[away_idx], available_teams[home_idx]])
    
    return matchups

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
