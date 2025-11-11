#!/usr/bin/env python3
"""
Create placeholder NFL team logos using text-based SVG graphics
Since external downloads failed, we'll create simple SVG logos locally
"""

import os
from pathlib import Path

def create_svg_team_logos():
    """Create simple SVG logos for all NFL teams"""
    
    print("🎨 CREATING SVG TEAM LOGOS")
    print("=" * 30)
    
    # Ensure images directory exists
    images_dir = Path("static/images")
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # NFL teams with colors and abbreviations
    nfl_teams = {
        'ari': {'name': 'Cardinals', 'color': '#97233F', 'text_color': '#FFFFFF'},
        'atl': {'name': 'Falcons', 'color': '#A71930', 'text_color': '#FFFFFF'},
        'bal': {'name': 'Ravens', 'color': '#241773', 'text_color': '#FFFFFF'},
        'buf': {'name': 'Bills', 'color': '#00338D', 'text_color': '#FFFFFF'},
        'car': {'name': 'Panthers', 'color': '#0085CA', 'text_color': '#FFFFFF'},
        'chi': {'name': 'Bears', 'color': '#0B162A', 'text_color': '#FFFFFF'},
        'cin': {'name': 'Bengals', 'color': '#FB4F14', 'text_color': '#FFFFFF'},
        'cle': {'name': 'Browns', 'color': '#311D00', 'text_color': '#FFFFFF'},
        'dal': {'name': 'Cowboys', 'color': '#003594', 'text_color': '#FFFFFF'},
        'den': {'name': 'Broncos', 'color': '#FB4F14', 'text_color': '#FFFFFF'},
        'det': {'name': 'Lions', 'color': '#0076B6', 'text_color': '#FFFFFF'},
        'gb': {'name': 'Packers', 'color': '#203731', 'text_color': '#FFB612'},
        'hou': {'name': 'Texans', 'color': '#03202F', 'text_color': '#FFFFFF'},
        'ind': {'name': 'Colts', 'color': '#002C5F', 'text_color': '#FFFFFF'},
        'jax': {'name': 'Jaguars', 'color': '#101820', 'text_color': '#D7A22A'},
        'kc': {'name': 'Chiefs', 'color': '#E31837', 'text_color': '#FFB81C'},
        'lv': {'name': 'Raiders', 'color': '#000000', 'text_color': '#A5ACAF'},
        'lac': {'name': 'Chargers', 'color': '#0080C6', 'text_color': '#FFC20E'},
        'lar': {'name': 'Rams', 'color': '#003594', 'text_color': '#FFA300'},
        'mia': {'name': 'Dolphins', 'color': '#008E97', 'text_color': '#FFFFFF'},
        'min': {'name': 'Vikings', 'color': '#4F2683', 'text_color': '#FFC62F'},
        'ne': {'name': 'Patriots', 'color': '#002244', 'text_color': '#FFFFFF'},
        'no': {'name': 'Saints', 'color': '#101820', 'text_color': '#D3BC8D'},
        'nyg': {'name': 'Giants', 'color': '#0B2265', 'text_color': '#FFFFFF'},
        'nyj': {'name': 'Jets', 'color': '#125740', 'text_color': '#FFFFFF'},
        'phi': {'name': 'Eagles', 'color': '#004C54', 'text_color': '#FFFFFF'},
        'pit': {'name': 'Steelers', 'color': '#FFB612', 'text_color': '#101820'},
        'sf': {'name': '49ers', 'color': '#AA0000', 'text_color': '#B3995D'},
        'sea': {'name': 'Seahawks', 'color': '#002244', 'text_color': '#69BE28'},
        'tb': {'name': 'Bucs', 'color': '#D50A0A', 'text_color': '#FFFFFF'},
        'ten': {'name': 'Titans', 'color': '#0C2340', 'text_color': '#4B92DB'},
        'was': {'name': 'Commanders', 'color': '#5A1414', 'text_color': '#FFB612'}
    }
    
    created_count = 0
    
    for team_code, team_info in nfl_teams.items():
        svg_content = f'''<svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad{team_code}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{team_info['color']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{team_info['color']};stop-opacity:0.8" />
    </linearGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="32" cy="32" r="30" fill="url(#grad{team_code})" stroke="{team_info['text_color']}" stroke-width="2"/>
  
  <!-- Team abbreviation -->
  <text x="32" y="38" font-family="Arial, sans-serif" font-size="12" font-weight="bold" 
        text-anchor="middle" fill="{team_info['text_color']}">{team_code.upper()}</text>
</svg>'''
        
        # Save as SVG file
        svg_path = images_dir / f"{team_code}.svg"
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        created_count += 1
        print(f"   ✅ Created {team_info['name']} logo ({team_code}.svg)")
    
    print(f"\n✅ Created {created_count} SVG team logos")
    return created_count

def update_database_logo_paths():
    """Update database to use SVG logo paths"""
    
    import sqlite3
    
    print(f"\n🔄 UPDATING LOGO PATHS IN DATABASE")
    print("-" * 35)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Update all logo URLs to use SVG files
    cursor.execute('''
        UPDATE team_info 
        SET logo_url = '/static/images/' || team_code || '.svg'
        WHERE team_code IS NOT NULL
    ''')
    
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ Updated {updated_count} team logo paths to use SVG files")

def main():
    """Create SVG logos and update database"""
    
    try:
        # Create SVG logos
        created_count = create_svg_team_logos()
        
        # Update database paths
        update_database_logo_paths()
        
        print(f"\n🎉 SVG LOGO SETUP COMPLETE!")
        print("=" * 35)
        print(f"✅ Created {created_count} SVG team logos")
        print("✅ Updated database logo paths")
        print("\n📁 Logo files created in: static/images/")
        print("🔗 URLs use format: /static/images/[team_code].svg")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating SVG logos: {e}")
        return False

if __name__ == "__main__":
    main()