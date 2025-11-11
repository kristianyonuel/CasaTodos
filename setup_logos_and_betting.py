#!/usr/bin/env python3
"""
Add NFL Team Logos and Vegas Betting Odds
Creates team logo infrastructure and adds betting odds to games
"""

import os
import sqlite3
import requests
from pathlib import Path

def create_logo_infrastructure():
    """Create the necessary folders and download team logos"""
    
    print("🏈 SETTING UP NFL TEAM LOGOS AND VEGAS ODDS")
    print("=" * 50)
    
    # Create images directory
    images_dir = Path("static/images")
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {images_dir}")
    
    # NFL team logo URLs (using ESPN's logo API)
    nfl_teams = {
        'Arizona Cardinals': 'ari',
        'Atlanta Falcons': 'atl', 
        'Baltimore Ravens': 'bal',
        'Buffalo Bills': 'buf',
        'Carolina Panthers': 'car',
        'Chicago Bears': 'chi',
        'Cincinnati Bengals': 'cin',
        'Cleveland Browns': 'cle',
        'Dallas Cowboys': 'dal',
        'Denver Broncos': 'den',
        'Detroit Lions': 'det',
        'Green Bay Packers': 'gb',
        'Houston Texans': 'hou',
        'Indianapolis Colts': 'ind',
        'Jacksonville Jaguars': 'jax',
        'Kansas City Chiefs': 'kc',
        'Las Vegas Raiders': 'lv',
        'Los Angeles Chargers': 'lac',
        'Los Angeles Rams': 'lar',
        'Miami Dolphins': 'mia',
        'Minnesota Vikings': 'min',
        'New England Patriots': 'ne',
        'New Orleans Saints': 'no',
        'New York Giants': 'nyg',
        'New York Jets': 'nyj',
        'Philadelphia Eagles': 'phi',
        'Pittsburgh Steelers': 'pit',
        'San Francisco 49ers': 'sf',
        'Seattle Seahawks': 'sea',
        'Tampa Bay Buccaneers': 'tb',
        'Tennessee Titans': 'ten',
        'Washington Commanders': 'was'
    }
    
    print(f"\n📥 Downloading {len(nfl_teams)} team logos...")
    
    downloaded = 0
    for team_name, team_code in nfl_teams.items():
        try:
            # ESPN logo URL
            logo_url = f"https://a.espncdn.com/i/teamlogos/nfl/500/{team_code}.png"
            
            # Download logo
            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                logo_path = images_dir / f"{team_code}.png"
                with open(logo_path, 'wb') as f:
                    f.write(response.content)
                downloaded += 1
                print(f"   ✅ {team_name} ({team_code}.png)")
            else:
                print(f"   ❌ Failed to download {team_name}")
                
        except Exception as e:
            print(f"   ❌ Error downloading {team_name}: {e}")
    
    print(f"\n✅ Downloaded {downloaded}/{len(nfl_teams)} team logos")
    
    return nfl_teams

def add_team_logo_mapping():
    """Add team logo mapping to database"""
    
    print(f"\n🗄️ ADDING TEAM LOGO MAPPING TO DATABASE")
    print("-" * 40)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Create team_info table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_info (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE NOT NULL,
            team_code TEXT NOT NULL,
            logo_url TEXT,
            primary_color TEXT,
            secondary_color TEXT,
            city TEXT,
            conference TEXT,
            division TEXT
        )
    ''')
    
    # Team data with colors and divisions
    teams_data = [
        ('Arizona Cardinals', 'ari', '#97233F', '#000000', 'Arizona', 'NFC', 'West'),
        ('Atlanta Falcons', 'atl', '#A71930', '#000000', 'Atlanta', 'NFC', 'South'),
        ('Baltimore Ravens', 'bal', '#241773', '#000000', 'Baltimore', 'AFC', 'North'),
        ('Buffalo Bills', 'buf', '#00338D', '#C60C30', 'Buffalo', 'AFC', 'East'),
        ('Carolina Panthers', 'car', '#0085CA', '#101820', 'Carolina', 'NFC', 'South'),
        ('Chicago Bears', 'chi', '#0B162A', '#C83803', 'Chicago', 'NFC', 'North'),
        ('Cincinnati Bengals', 'cin', '#FB4F14', '#000000', 'Cincinnati', 'AFC', 'North'),
        ('Cleveland Browns', 'cle', '#311D00', '#FF3C00', 'Cleveland', 'AFC', 'North'),
        ('Dallas Cowboys', 'dal', '#003594', '#869397', 'Dallas', 'NFC', 'East'),
        ('Denver Broncos', 'den', '#FB4F14', '#002244', 'Denver', 'AFC', 'West'),
        ('Detroit Lions', 'det', '#0076B6', '#B0B7BC', 'Detroit', 'NFC', 'North'),
        ('Green Bay Packers', 'gb', '#203731', '#FFB612', 'Green Bay', 'NFC', 'North'),
        ('Houston Texans', 'hou', '#03202F', '#A71930', 'Houston', 'AFC', 'South'),
        ('Indianapolis Colts', 'ind', '#002C5F', '#A2AAAD', 'Indianapolis', 'AFC', 'South'),
        ('Jacksonville Jaguars', 'jax', '#101820', '#D7A22A', 'Jacksonville', 'AFC', 'South'),
        ('Kansas City Chiefs', 'kc', '#E31837', '#FFB81C', 'Kansas City', 'AFC', 'West'),
        ('Las Vegas Raiders', 'lv', '#000000', '#A5ACAF', 'Las Vegas', 'AFC', 'West'),
        ('Los Angeles Chargers', 'lac', '#0080C6', '#FFC20E', 'Los Angeles', 'AFC', 'West'),
        ('Los Angeles Rams', 'lar', '#003594', '#FFA300', 'Los Angeles', 'NFC', 'West'),
        ('Miami Dolphins', 'mia', '#008E97', '#FC4C02', 'Miami', 'AFC', 'East'),
        ('Minnesota Vikings', 'min', '#4F2683', '#FFC62F', 'Minnesota', 'NFC', 'North'),
        ('New England Patriots', 'ne', '#002244', '#C60C30', 'New England', 'AFC', 'East'),
        ('New Orleans Saints', 'no', '#101820', '#D3BC8D', 'New Orleans', 'NFC', 'South'),
        ('New York Giants', 'nyg', '#0B2265', '#A71930', 'New York', 'NFC', 'East'),
        ('New York Jets', 'nyj', '#125740', '#000000', 'New York', 'AFC', 'East'),
        ('Philadelphia Eagles', 'phi', '#004C54', '#A5ACAF', 'Philadelphia', 'NFC', 'East'),
        ('Pittsburgh Steelers', 'pit', '#FFB612', '#101820', 'Pittsburgh', 'AFC', 'North'),
        ('San Francisco 49ers', 'sf', '#AA0000', '#B3995D', 'San Francisco', 'NFC', 'West'),
        ('Seattle Seahawks', 'sea', '#002244', '#69BE28', 'Seattle', 'NFC', 'West'),
        ('Tampa Bay Buccaneers', 'tb', '#D50A0A', '#FF7900', 'Tampa Bay', 'NFC', 'South'),
        ('Tennessee Titans', 'ten', '#0C2340', '#4B92DB', 'Tennessee', 'AFC', 'South'),
        ('Washington Commanders', 'was', '#5A1414', '#FFB612', 'Washington', 'NFC', 'East')
    ]
    
    for team_data in teams_data:
        team_name, team_code, primary_color, secondary_color, city, conference, division = team_data
        logo_url = f"/static/images/{team_code}.png"
        
        cursor.execute('''
            INSERT OR REPLACE INTO team_info 
            (team_name, team_code, logo_url, primary_color, secondary_color, city, conference, division)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (team_name, team_code, logo_url, primary_color, secondary_color, city, conference, division))
        
        print(f"   ✅ Added {team_name} ({team_code})")
    
    conn.commit()
    conn.close()
    print(f"✅ Added {len(teams_data)} teams to database")

def add_betting_odds_to_games():
    """Add betting odds columns to nfl_games table and populate with sample data"""
    
    print(f"\n🎰 ADDING VEGAS BETTING ODDS")
    print("-" * 30)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Add betting columns if they don't exist
    betting_columns = [
        ('spread_line', 'REAL'),           # Point spread (e.g., -3.5)
        ('spread_favorite', 'TEXT'),       # Which team is favored
        ('over_under', 'REAL'),           # Total points over/under
        ('moneyline_home', 'INTEGER'),     # Home team moneyline odds
        ('moneyline_away', 'INTEGER'),     # Away team moneyline odds
        ('betting_updated', 'TIMESTAMP')   # When odds were last updated
    ]
    
    for column_name, column_type in betting_columns:
        try:
            cursor.execute(f'ALTER TABLE nfl_games ADD COLUMN {column_name} {column_type}')
            print(f"   ✅ Added column: {column_name}")
        except sqlite3.OperationalError:
            print(f"   ⚠️ Column {column_name} already exists")
    
    # Get Week 10 games to add sample betting data
    cursor.execute('''
        SELECT game_id, home_team, away_team, game_date 
        FROM nfl_games 
        WHERE week = 10 AND year = 2025 
        ORDER BY game_date
    ''')
    week10_games = cursor.fetchall()
    
    # Sample betting odds for Week 10 games (realistic odds)
    sample_odds = [
        (-3.5, 'home', 47.5, -160, +140),   # Raiders @ Broncos (TNF)
        (-2.5, 'away', 42.5, +120, -140),   # Colts @ Falcons  
        (-6.5, 'home', 48.5, -280, +220),   # Dolphins @ Bills
        (-1.5, 'away', 44.5, +105, -125),   # Patriots @ Bears
        (-4.5, 'home', 51.5, -200, +170),   # Giants @ Panthers
        (-7.5, 'away', 46.5, -320, +250),   # Vikings @ Jaguars
        (-3.5, 'home', 49.5, -160, +140),   # Saints @ Steelers
        (-10.5, 'away', 52.5, -450, +350),  # Commanders @ Eagles
        (-2.5, 'home', 45.5, -130, +110),   # Jets @ Cardinals
        (-1.5, 'home', 43.5, +110, -130),   # 49ers @ Buccaneers
        (-6.5, 'away', 50.5, -280, +220),   # Titans @ Chargers
        (-3.5, 'away', 47.5, -160, +140),   # Lions @ Texans
        (-4.5, 'home', 54.5, -200, +170),   # Chiefs @ Browns (MNF)
        (-2.5, 'away', 48.5, -130, +110)    # Rams @ Seahawks (MNF)
    ]
    
    for i, (game_id, home_team, away_team, game_date) in enumerate(week10_games):
        if i < len(sample_odds):
            spread, spread_fav, over_under, ml_home, ml_away = sample_odds[i]
            
            # Determine which team is favored
            if spread_fav == 'home':
                favorite = home_team
            else:
                favorite = away_team
                spread = -spread  # Flip the spread for away favorites
            
            cursor.execute('''
                UPDATE nfl_games 
                SET spread_line = ?, spread_favorite = ?, over_under = ?, 
                    moneyline_home = ?, moneyline_away = ?, betting_updated = datetime('now')
                WHERE game_id = ?
            ''', (spread, favorite, over_under, ml_home, ml_away, game_id))
            
            print(f"   ✅ {away_team} @ {home_team}: {favorite} {abs(spread)}, O/U {over_under}")
    
    conn.commit()
    conn.close()
    print(f"✅ Added betting odds to {len(week10_games)} Week 10 games")

def create_logo_css():
    """Create CSS for team logos and betting display"""
    
    print(f"\n🎨 CREATING LOGO AND BETTING STYLES")
    print("-" * 35)
    
    css_content = '''
/* NFL Team Logo Styles */
.team-logo {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    margin-right: 8px;
    vertical-align: middle;
    object-fit: contain;
}

.team-logo-large {
    width: 48px;
    height: 48px;
    border-radius: 6px;
    margin-right: 12px;
    vertical-align: middle;
    object-fit: contain;
}

.team-with-logo {
    display: flex;
    align-items: center;
    font-weight: bold;
}

/* Betting Odds Styles */
.betting-info {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    font-size: 0.9em;
}

.betting-line {
    display: flex;
    justify-content: space-between;
    margin: 4px 0;
}

.spread {
    font-weight: bold;
    color: #007bff;
}

.over-under {
    color: #28a745;
    font-weight: bold;
}

.moneyline {
    color: #dc3545;
    font-weight: bold;
}

.favorite {
    background: #fff3cd;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: bold;
}

.betting-updated {
    font-size: 0.8em;
    color: #6c757d;
    text-align: right;
    margin-top: 8px;
}

/* Game Card Enhancements */
.game-card-enhanced {
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.team-matchup {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.team-info {
    display: flex;
    align-items: center;
    flex: 1;
}

.vs-indicator {
    font-size: 1.2em;
    font-weight: bold;
    color: #6c757d;
    margin: 0 16px;
}
'''
    
    # Append to existing style.css
    with open('static/style.css', 'a') as f:
        f.write('\n\n/* NFL TEAM LOGOS AND BETTING ODDS STYLES */\n')
        f.write(css_content)
    
    print("✅ Added logo and betting styles to style.css")

def main():
    """Main function to set up logos and betting odds"""
    
    try:
        # Create logo infrastructure
        nfl_teams = create_logo_infrastructure()
        
        # Add team data to database
        add_team_logo_mapping()
        
        # Add betting odds
        add_betting_odds_to_games()
        
        # Create CSS styles
        create_logo_css()
        
        print(f"\n🎉 SETUP COMPLETE!")
        print("=" * 50)
        print("✅ Team logos downloaded and ready")
        print("✅ Team info added to database") 
        print("✅ Betting odds added to Week 10 games")
        print("✅ CSS styles updated")
        print("\n📝 Next Steps:")
        print("1. Update Flask templates to show logos")
        print("2. Add betting display to game cards")
        print("3. Restart Flask server")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up logos and betting: {e}")
        return False

if __name__ == "__main__":
    main()