import sqlite3
from datetime import datetime

def fix_week10_schedule():
    """Replace incorrect Week 10 games with the actual NFL Week 10 schedule"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🏈 FIXING WEEK 10 NFL SCHEDULE")
    print("=" * 50)
    
    # First, delete all incorrect Week 10 games
    cursor.execute('DELETE FROM nfl_games WHERE week = 10 AND year = 2025')
    deleted_count = cursor.rowcount
    print(f"✅ Deleted {deleted_count} incorrect Week 10 games")
    
    # Correct Week 10 games 
    week10_games = [
        # Thursday Nov 6
        ('Las Vegas Raiders', 'Denver Broncos', '2025-11-06 21:15:00', 'AMZN', 'Empower Field at Mile High, Denver, CO', -9.5, True, False, False),
        
        # Sunday Nov 9 - Early Games
        ('Atlanta Falcons', 'Indianapolis Colts', '2025-11-09 10:30:00', 'NFLN', 'Olympic Stadium Berlin, Berlin, DEU', -6.5, False, False, False),
        ('Buffalo Bills', 'Miami Dolphins', '2025-11-09 14:00:00', 'CBS', 'Hard Rock Stadium, Miami Gardens, FL', -9.5, False, False, False),
        ('Jacksonville Jaguars', 'Houston Texans', '2025-11-09 14:00:00', 'CBS', 'NRG Stadium, Houston, TX', -1.0, False, False, False),
        ('New York Giants', 'Chicago Bears', '2025-11-09 14:00:00', 'FOX', 'Soldier Field, Chicago, IL', -4.5, False, False, False),
        ('New Orleans Saints', 'Carolina Panthers', '2025-11-09 14:00:00', 'FOX', 'Bank of America Stadium, Charlotte, NC', -5.5, False, False, False),
        ('New England Patriots', 'Tampa Bay Buccaneers', '2025-11-09 14:00:00', 'CBS', 'Raymond James Stadium, Tampa, FL', -2.5, False, False, False),
        ('Cleveland Browns', 'New York Jets', '2025-11-09 14:00:00', 'CBS', 'MetLife Stadium, East Rutherford, NJ', -2.5, False, False, False),
        ('Baltimore Ravens', 'Minnesota Vikings', '2025-11-09 14:00:00', 'FOX', 'U.S. Bank Stadium, Minneapolis, MN', -4.0, False, False, False),
        
        # Sunday Late Games
        ('Arizona Cardinals', 'Seattle Seahawks', '2025-11-09 17:05:00', 'CBS', 'Lumen Field, Seattle, WA', -6.5, False, False, False),
        ('Los Angeles Rams', 'San Francisco 49ers', '2025-11-09 17:25:00', 'FOX', 'Levi\'s Stadium, Santa Clara, CA', -4.5, False, False, False),
        ('Detroit Lions', 'Washington Commanders', '2025-11-09 17:25:00', 'FOX', 'Northwest Stadium, Landover, MD', -8.5, False, False, False),
        
        # Sunday Night
        ('Pittsburgh Steelers', 'Los Angeles Chargers', '2025-11-09 21:20:00', 'NBC', 'SoFi Stadium, Inglewood, CA', -3.0, False, True, False),
        
        # Monday Night
        ('Philadelphia Eagles', 'Green Bay Packers', '2025-11-10 21:15:00', 'ABC', 'Lambeau Field, Green Bay, WI', -2.5, False, False, True)
    ]
    
    print(f"\n📝 Inserting {len(week10_games)} correct Week 10 games:")
    
    for i, (away_team, home_team, game_date, tv_network, stadium, betting_line, is_tnf, is_snf, is_mnf) in enumerate(week10_games, 1):
        game_id = f"nfl_2025_w10_{i}"
        
        cursor.execute('''
            INSERT INTO nfl_games (
                game_id, week, year, away_team, home_team, game_date,
                tv_network, stadium, betting_line, 
                is_thursday_night, is_sunday_night, is_monday_night,
                is_final, home_score, away_score, quarter, time_remaining, game_status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, 10, 2025, away_team, home_team, game_date,
            tv_network, stadium, betting_line,
            is_tnf, is_snf, is_mnf,
            False, None, None, 0, None, 'Scheduled',
            datetime.now(), datetime.now()
        ))
        
        # Format game time for display
        date_obj = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S')
        time_str = date_obj.strftime('%a %m/%d %I:%M %p')
        
        special = ""
        if is_tnf:
            special = " 📺 TNF"
        elif is_snf:
            special = " 🌙 SNF"
        elif is_mnf:
            special = " 🏈 MNF"
        
        print(f"  {i:2d}. {away_team:20s} @ {home_team:20s} - {time_str}{special}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Week 10 schedule updated with {len(week10_games)} games")
    print("🏈 Tonight's Thursday Night Football: Raiders @ Broncos (9:15 PM)")
    print("📅 Week 10 runs November 6-10, 2025")

if __name__ == "__main__":
    fix_week10_schedule()