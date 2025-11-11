#!/usr/bin/env python3
"""
Update Flask Templates with NFL Team Logos and Betting Odds
Adds logo display and betting information to game templates
"""

import os
import re
import sqlite3
from pathlib import Path

def update_games_template():
    """Update games.html template to show logos and betting odds"""
    
    print("🎨 UPDATING GAMES TEMPLATE WITH LOGOS AND BETTING")
    print("=" * 50)
    
    templates_dir = Path("templates")
    games_template = templates_dir / "games.html"
    
    if not games_template.exists():
        print(f"❌ Template not found: {games_template}")
        return False
    
    # Read current template
    with open(games_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_path = templates_dir / "games_backup_with_logos.html"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created backup: {backup_path}")
    
    # Enhanced game template with logos and betting
    enhanced_game_card = '''
    <div class="game-card-enhanced">
        <div class="team-matchup">
            <div class="team-info">
                {% if away_team_logo %}
                <img src="{{ away_team_logo }}" alt="{{ game.away_team }}" class="team-logo">
                {% endif %}
                <strong>{{ game.away_team }}</strong>
                {% if game.away_score is not none %}
                    <span class="score">({{ game.away_score }})</span>
                {% endif %}
            </div>
            
            <div class="vs-indicator">@</div>
            
            <div class="team-info">
                {% if home_team_logo %}
                <img src="{{ home_team_logo }}" alt="{{ game.home_team }}" class="team-logo">
                {% endif %}
                <strong>{{ game.home_team }}</strong>
                {% if game.home_score is not none %}
                    <span class="score">({{ game.home_score }})</span>
                {% endif %}
            </div>
        </div>
        
        <!-- Game Details -->
        <div class="game-details">
            <div><strong>{{ game.game_date.strftime('%A, %B %d') }}</strong></div>
            <div>{{ game.game_time.strftime('%I:%M %p') if game.game_time else 'TBD' }} ET</div>
            {% if game.tv_network %}
            <div class="tv-network">📺 {{ game.tv_network }}</div>
            {% endif %}
        </div>
        
        <!-- Betting Information -->
        {% if game.spread_line or game.over_under or game.moneyline_home %}
        <div class="betting-info">
            <div class="betting-header">🎰 Vegas Odds</div>
            
            {% if game.spread_line %}
            <div class="betting-line">
                <span>Spread:</span>
                <span class="spread">
                    {% if game.spread_favorite == game.home_team %}
                        {{ game.home_team }} {{ game.spread_line }}
                    {% else %}
                        {{ game.away_team }} {{ game.spread_line }}
                    {% endif %}
                </span>
            </div>
            {% endif %}
            
            {% if game.over_under %}
            <div class="betting-line">
                <span>Over/Under:</span>
                <span class="over-under">{{ game.over_under }}</span>
            </div>
            {% endif %}
            
            {% if game.moneyline_home or game.moneyline_away %}
            <div class="betting-line">
                <span>Moneyline:</span>
                <span class="moneyline">
                    {{ game.away_team }} {% if game.moneyline_away > 0 %}+{% endif %}{{ game.moneyline_away }}
                    | {{ game.home_team }} {% if game.moneyline_home > 0 %}+{% endif %}{{ game.moneyline_home }}
                </span>
            </div>
            {% endif %}
            
            {% if game.betting_updated %}
            <div class="betting-updated">
                Updated: {{ game.betting_updated.strftime('%m/%d %I:%M %p') }}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- Pick Section if user is logged in -->
        {% if session.user_id %}
        <div class="pick-section">
            <form method="POST" action="{{ url_for('games') }}">
                <input type="hidden" name="game_id" value="{{ game.game_id }}">
                
                <div class="pick-options">
                    <label class="pick-option">
                        <input type="radio" name="pick" value="{{ game.away_team }}" 
                               {% if game.user_pick == game.away_team %}checked{% endif %}
                               {% if game.locked %}disabled{% endif %}>
                        <span class="team-with-logo">
                            {% if away_team_logo %}
                            <img src="{{ away_team_logo }}" alt="{{ game.away_team }}" class="team-logo">
                            {% endif %}
                            {{ game.away_team }}
                        </span>
                    </label>
                    
                    <label class="pick-option">
                        <input type="radio" name="pick" value="{{ game.home_team }}" 
                               {% if game.user_pick == game.home_team %}checked{% endif %}
                               {% if game.locked %}disabled{% endif %}>
                        <span class="team-with-logo">
                            {% if home_team_logo %}
                            <img src="{{ home_team_logo }}" alt="{{ game.home_team }}" class="team-logo">
                            {% endif %}
                            {{ game.home_team }}
                        </span>
                    </label>
                </div>
                
                {% if not game.locked %}
                <button type="submit" class="btn-pick">Save Pick</button>
                {% else %}
                <div class="locked-message">🔒 Picks locked</div>
                {% endif %}
            </form>
        </div>
        {% endif %}
    </div>
    '''
    
    # Find and replace existing game card pattern
    # Look for game display patterns and replace them
    
    # Pattern 1: Simple team display
    pattern1 = r'(<div[^>]*class="[^"]*game[^"]*"[^>]*>.*?</div>)'
    if re.search(pattern1, content, re.DOTALL):
        content = re.sub(pattern1, enhanced_game_card, content, flags=re.DOTALL)
        print("✅ Updated game card pattern 1")
    
    # If no existing pattern found, append the enhanced template
    if '<!-- ENHANCED GAME TEMPLATE -->' not in content:
        content += '\n\n<!-- ENHANCED GAME TEMPLATE -->\n'
        content += enhanced_game_card
        print("✅ Added enhanced game template")
    
    # Write updated template
    with open(games_template, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {games_template}")
    return True

def create_flask_route_helper():
    """Create helper function for Flask routes to get team logos"""
    
    print(f"\n📝 CREATING FLASK ROUTE HELPER")
    print("-" * 35)
    
    helper_code = '''
# ADD THIS TO YOUR FLASK APP.PY FILE

def get_team_logos_and_betting(games):
    """
    Enhance games list with team logos and betting information
    Call this function before rendering templates
    """
    import sqlite3
    
    enhanced_games = []
    
    # Get team logo mapping
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all team info for logos
    cursor.execute('SELECT team_name, team_code, logo_url FROM team_info')
    team_logos = {}
    for team_name, team_code, logo_url in cursor.fetchall():
        team_logos[team_name] = logo_url
    
    conn.close()
    
    for game in games:
        # Add logo URLs to game object
        game.away_team_logo = team_logos.get(game.away_team)
        game.home_team_logo = team_logos.get(game.home_team)
        enhanced_games.append(game)
    
    return enhanced_games

# EXAMPLE USAGE IN YOUR FLASK ROUTES:

@app.route('/games')
def games():
    # ... your existing game query logic ...
    games = get_week_games(current_week)  # Your existing function
    
    # Enhance with logos and betting
    enhanced_games = get_team_logos_and_betting(games)
    
    return render_template('games.html', 
                         games=enhanced_games, 
                         current_week=current_week)

# UPDATE YOUR DATABASE QUERY TO INCLUDE BETTING FIELDS:

def get_week_games(week):
    """Updated to include betting information"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    query = """
    SELECT g.*, 
           g.spread_line, g.spread_favorite, g.over_under,
           g.moneyline_home, g.moneyline_away, g.betting_updated,
           p.team_picked as user_pick
    FROM nfl_games g
    LEFT JOIN user_picks p ON g.game_id = p.game_id 
                           AND p.user_id = %s
    WHERE g.week = ? AND g.year = 2025
    ORDER BY g.game_date, g.game_time
    """
    
    user_id = session.get('user_id') if 'session' in globals() else None
    cursor.execute(query, (user_id, week))
    
    games = cursor.fetchall()
    conn.close()
    
    return games
'''
    
    with open('flask_logo_betting_helper.py', 'w') as f:
        f.write(helper_code)
    
    print("✅ Created flask_logo_betting_helper.py")
    print("📋 Instructions saved for integrating with Flask app")

def update_dashboard_template():
    """Update index.html/dashboard template with enhanced game display"""
    
    print(f"\n🏠 UPDATING DASHBOARD TEMPLATE")
    print("-" * 30)
    
    templates_dir = Path("templates")
    
    # Try to find main dashboard template
    dashboard_files = ['index.html', 'index_new.html', 'dashboard.html']
    
    for template_name in dashboard_files:
        template_path = templates_dir / template_name
        if template_path.exists():
            print(f"✅ Found dashboard template: {template_name}")
            
            # Create backup
            backup_path = templates_dir / f"{template_name.split('.')[0]}_backup_with_logos.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add logo support to dashboard
            logo_css = '''
<!-- Add this to the <head> section or after existing CSS -->
<style>
/* Enhanced dashboard game cards */
.dashboard-game {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    background: #f9f9f9;
}

.team-matchup-mini {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
}

.team-with-logo-mini {
    display: flex;
    align-items: center;
}

.team-logo-mini {
    width: 24px;
    height: 24px;
    margin-right: 6px;
    border-radius: 3px;
}

.betting-preview {
    font-size: 0.85em;
    color: #666;
    margin-top: 4px;
}
</style>
'''
            
            if '<head>' in content and logo_css not in content:
                content = content.replace('</head>', f'{logo_css}\n</head>')
                
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ Updated {template_name} with logo styles")
            
            break
    
    return True

def main():
    """Main function to update templates"""
    
    try:
        print("🎨 NFL TEMPLATE ENHANCEMENT")
        print("=" * 40)
        
        # Update main games template
        update_games_template()
        
        # Create Flask helper code
        create_flask_route_helper()
        
        # Update dashboard template
        update_dashboard_template()
        
        print(f"\n🎉 TEMPLATE UPDATES COMPLETE!")
        print("=" * 40)
        print("✅ Games template enhanced with logos and betting")
        print("✅ Flask helper code created")
        print("✅ Dashboard template updated")
        print("\n📝 Next Steps:")
        print("1. Copy code from flask_logo_betting_helper.py to app.py")
        print("2. Update Flask routes to use get_team_logos_and_betting()")
        print("3. Restart Flask server")
        print("4. Test logo and betting display")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating templates: {e}")
        return False

if __name__ == "__main__":
    main()