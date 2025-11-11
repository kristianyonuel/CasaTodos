import sqlite3
from datetime import datetime

def update_week10_schedule():
    """Update Week 10 NFL schedule with correct dates, times, and details"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🏈 UPDATING WEEK 10 NFL SCHEDULE")
    print("=" * 50)
    
    # Week 10 games with correct schedule
    week10_games = [
        # Thursday Nov 6
        {
            'away_team': 'Las Vegas Raiders',
            'home_team': 'Denver Broncos', 
            'game_date': '2025-11-06 21:15:00',
            'tv_network': 'AMZN',
            'stadium': 'Empower Field at Mile High, Denver, CO',
            'betting_line': -9.5,
            'is_thursday_night': True
        },
        
        # Sunday Nov 9 - Early Games
        {
            'away_team': 'Atlanta Falcons',
            'home_team': 'Indianapolis Colts',
            'game_date': '2025-11-09 10:30:00',  # London game
            'tv_network': 'NFLN', 
            'stadium': 'Olympic Stadium Berlin, Berlin, DEU',
            'betting_line': -6.5
        },
        {
            'away_team': 'Buffalo Bills',
            'home_team': 'Miami Dolphins',
            'game_date': '2025-11-09 14:00:00',
            'tv_network': 'CBS',
            'stadium': 'Hard Rock Stadium, Miami Gardens, FL',
            'betting_line': -9.5
        },
        {
            'away_team': 'Jacksonville Jaguars', 
            'home_team': 'Houston Texans',
            'game_date': '2025-11-09 14:00:00',
            'tv_network': 'CBS',
            'stadium': 'NRG Stadium, Houston, TX',
            'betting_line': -1.0
        },
        {
            'away_team': 'New York Giants',
            'home_team': 'Chicago Bears',
            'game_date': '2025-11-09 14:00:00',
            'tv_network': 'FOX',
            'stadium': 'Soldier Field, Chicago, IL', 
            'betting_line': -4.5
        },
        {
            'away_team': 'New Orleans Saints',
            'home_team': 'Carolina Panthers',
            'game_date': '2025-11-09 14:00:00',
            'tv_network': 'FOX',
            'stadium': 'Bank of America Stadium, Charlotte, NC',
            'betting_line': -5.5
        },
        {
            'away_team': 'New England Patriots',
            'home_team': 'Tampa Bay Buccaneers',
            'game_date': '2025-11-09 14:00:00',
            'tv_network': 'CBS',
            'stadium': 'Raymond James Stadium, Tampa, FL',
            'betting_line': -2.5
        },
        {
            'away_team': 'Cleveland Browns',
            'home_team': 'New York Jets',
            'game_date': '2025-11-09 14:00:00',
            'tv_network': 'CBS',
            'stadium': 'MetLife Stadium, East Rutherford, NJ',
            'betting_line': -2.5
        },
        {
            'away_team': 'Baltimore Ravens',
            'home_team': 'Minnesota Vikings',
            'game_date': '2025-11-09 14:00:00',
            'tv_network': 'FOX',
            'stadium': 'U.S. Bank Stadium, Minneapolis, MN',
            'betting_line': -4.0
        },
        
        # Sunday Late Games
        {
            'away_team': 'Arizona Cardinals',
            'home_team': 'Seattle Seahawks',
            'game_date': '2025-11-09 17:05:00',
            'tv_network': 'CBS',
            'stadium': 'Lumen Field, Seattle, WA',
            'betting_line': -6.5
        },
        {
            'away_team': 'Los Angeles Rams',
            'home_team': 'San Francisco 49ers',
            'game_date': '2025-11-09 17:25:00',
            'tv_network': 'FOX',
            'stadium': 'Levi\'s Stadium, Santa Clara, CA',
            'betting_line': -4.5
        },
        {
            'away_team': 'Detroit Lions',
            'home_team': 'Washington Commanders',
            'game_date': '2025-11-09 17:25:00',
            'tv_network': 'FOX',
            'stadium': 'Northwest Stadium, Landover, MD',
            'betting_line': -8.5
        },
        
        # Sunday Night
        {
            'away_team': 'Pittsburgh Steelers',
            'home_team': 'Los Angeles Chargers',
            'game_date': '2025-11-09 21:20:00',
            'tv_network': 'NBC',
            'stadium': 'SoFi Stadium, Inglewood, CA',
            'betting_line': -3.0,
            'is_sunday_night': True
        },
        
        # Monday Night
        {
            'away_team': 'Philadelphia Eagles',
            'home_team': 'Green Bay Packers',
            'game_date': '2025-11-10 21:15:00',
            'tv_network': 'ABC',
            'stadium': 'Lambeau Field, Green Bay, WI',
            'betting_line': -2.5,
            'is_monday_night': True
        }
    ]
    
    updated_count = 0
    
    for game_data in week10_games:
        # Find the game by teams
        cursor.execute('''
            SELECT id, game_id FROM nfl_games 
            WHERE week = 10 AND year = 2025 
              AND away_team = ? AND home_team = ?
        ''', (game_data['away_team'], game_data['home_team']))
        
        result = cursor.fetchone()
        if result:
            game_id = result[1]
            
            # Update the game with correct schedule info
            cursor.execute('''
                UPDATE nfl_games SET
                    game_date = ?,
                    tv_network = ?,
                    stadium = ?,
                    betting_line = ?,
                    is_thursday_night = ?,
                    is_sunday_night = ?,
                    is_monday_night = ?,
                    updated_at = ?
                WHERE game_id = ?
            ''', (
                game_data['game_date'],
                game_data['tv_network'],
                game_data['stadium'],
                game_data['betting_line'],
                game_data.get('is_thursday_night', False),
                game_data.get('is_sunday_night', False), 
                game_data.get('is_monday_night', False),
                datetime.now(),
                game_id
            ))
            
            updated_count += 1
            print(f"✅ Updated: {game_data['away_team']} @ {game_data['home_team']} - {game_data['game_date']}")
        else:
            print(f"❌ Game not found: {game_data['away_team']} @ {game_data['home_team']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎯 Updated {updated_count}/14 Week 10 games")
    print("✅ Week 10 schedule is now ready!")
    print(f"🏈 Tonight's game: Raiders @ Broncos (9:15 PM)")

if __name__ == "__main__":
    update_week10_schedule()