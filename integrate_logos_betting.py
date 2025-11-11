#!/usr/bin/env python3
"""
INTEGRATE LOGOS AND BETTING ODDS
Comprehensive integration of team logos and Vegas betting odds into games.html
"""

import os
import shutil
from datetime import datetime

def backup_current_template():
    """Create backup of current working template"""
    source = "templates/games.html"
    backup = f"templates/games_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    if os.path.exists(source):
        shutil.copy2(source, backup)
        print(f"✅ Backed up current template to {backup}")
        return backup
    return None

def create_enhanced_games_template():
    """Create enhanced games.html with logos and betting odds"""
    
    template_content = '''{% extends "base.html" %}

{% block title %}Week {{ current_week }} Games{% endblock %}

{% block content %}
<div class="container">
    <h1>🏈 Week {{ current_week }} Games</h1>
    
    {% if games %}
        {% for game in games %}
        <div class="game-card">
            <!-- Game Header with Team Logos -->
            <div class="game-header">
                <div class="teams-display">
                    <div class="team away-team">
                        <img src="{{ url_for('static', filename='images/' + game.away_team|replace(' ', '_')|lower + '.svg') }}" 
                             alt="{{ game.away_team }} logo" 
                             class="team-logo"
                             onerror="this.style.display='none'">
                        <span class="team-name">{{ game.away_team }}</span>
                    </div>
                    
                    <div class="game-vs">@</div>
                    
                    <div class="team home-team">
                        <img src="{{ url_for('static', filename='images/' + game.home_team|replace(' ', '_')|lower + '.svg') }}" 
                             alt="{{ game.home_team }} logo" 
                             class="team-logo"
                             onerror="this.style.display='none'">
                        <span class="team-name">{{ game.home_team }}</span>
                    </div>
                </div>
                
                {% if game.game_date %}
                <div class="game-time">{{ game.game_date.strftime('%A, %B %d at %I:%M %p') }}</div>
                {% endif %}
            </div>
            
            <!-- Betting Information -->
            {% if game.spread or game.over_under %}
            <div class="betting-info">
                <div class="betting-stats">
                    {% if game.spread %}
                    <div class="bet-item">
                        <span class="bet-label">Spread:</span>
                        <span class="bet-value">{{ game.spread }}</span>
                    </div>
                    {% endif %}
                    
                    {% if game.over_under %}
                    <div class="bet-item">
                        <span class="bet-label">O/U:</span>
                        <span class="bet-value">{{ game.over_under }}</span>
                    </div>
                    {% endif %}
                    
                    {% if game.away_odds or game.home_odds %}
                    <div class="bet-item">
                        <span class="bet-label">Moneyline:</span>
                        <span class="bet-value">
                            {{ game.away_team }}: {{ game.away_odds if game.away_odds else '+100' }} | 
                            {{ game.home_team }}: {{ game.home_odds if game.home_odds else '+100' }}
                        </span>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endif %}
            
            <!-- Game Status/Score -->
            {% if game.final_score_away is not none and game.final_score_home is not none %}
            <div class="game-score final">
                <div class="score-display">
                    <span class="away-score">{{ game.away_team }}: {{ game.final_score_away }}</span>
                    <span class="score-separator">-</span>
                    <span class="home-score">{{ game.home_team }}: {{ game.final_score_home }}</span>
                </div>
                <div class="game-status">FINAL</div>
            </div>
            {% elif game.current_score_away is not none and game.current_score_home is not none %}
            <div class="game-score live">
                <div class="score-display">
                    <span class="away-score">{{ game.away_team }}: {{ game.current_score_away }}</span>
                    <span class="score-separator">-</span>
                    <span class="home-score">{{ game.home_team }}: {{ game.current_score_home }}</span>
                </div>
                <div class="game-status live-indicator">LIVE</div>
            </div>
            {% endif %}
            
            <!-- User Pick Section -->
            {% if session.user_id %}
            <div class="pick-section">
                <form method="POST">
                    <input type="hidden" name="game_id" value="{{ game.game_id }}">
                    
                    <div class="pick-options">
                        <label class="pick-option {% if game.user_pick == game.away_team %}selected{% endif %}">
                            <input type="radio" name="pick" value="{{ game.away_team }}" 
                                   {% if game.user_pick == game.away_team %}checked{% endif %}>
                            <img src="{{ url_for('static', filename='images/' + game.away_team|replace(' ', '_')|lower + '.svg') }}" 
                                 alt="{{ game.away_team }}" 
                                 class="pick-logo"
                                 onerror="this.style.display='none'">
                            <span>{{ game.away_team }}</span>
                        </label>
                        
                        <label class="pick-option {% if game.user_pick == game.home_team %}selected{% endif %}">
                            <input type="radio" name="pick" value="{{ game.home_team }}" 
                                   {% if game.user_pick == game.home_team %}checked{% endif %}>
                            <img src="{{ url_for('static', filename='images/' + game.home_team|replace(' ', '_')|lower + '.svg') }}" 
                                 alt="{{ game.home_team }}" 
                                 class="pick-logo"
                                 onerror="this.style.display='none'">
                            <span>{{ game.home_team }}</span>
                        </label>
                    </div>
                    
                    <button type="submit" class="btn-pick">Save Pick</button>
                </form>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <div class="no-games">
            <p>No games available for Week {{ current_week }}</p>
        </div>
    {% endif %}
</div>

<style>
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.game-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #e1e5e9;
    border-radius: 12px;
    padding: 25px;
    margin: 20px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.game-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}

/* Game Header Styling */
.game-header {
    margin-bottom: 20px;
}

.teams-display {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 30px;
    margin-bottom: 10px;
}

.team {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 120px;
}

.team-logo {
    width: 50px;
    height: 50px;
    margin-bottom: 8px;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.team-name {
    font-weight: bold;
    font-size: 1.1em;
    color: #333;
}

.game-vs {
    font-size: 1.5em;
    font-weight: bold;
    color: #666;
    align-self: flex-start;
    margin-top: 20px;
}

.game-time {
    text-align: center;
    color: #666;
    font-size: 0.95em;
    margin-top: 10px;
}

/* Betting Information */
.betting-info {
    background: #f1f3f5;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
}

.betting-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
}

.bet-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 100px;
}

.bet-label {
    font-size: 0.85em;
    color: #666;
    font-weight: 500;
    margin-bottom: 4px;
}

.bet-value {
    font-weight: bold;
    color: #333;
    font-size: 0.95em;
}

/* Game Score Display */
.game-score {
    background: #e8f5e8;
    border: 1px solid #c3e6c3;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
    text-align: center;
}

.game-score.live {
    background: #fff3cd;
    border-color: #ffeaa7;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.score-display {
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 8px;
    color: #333;
}

.score-separator {
    margin: 0 15px;
    color: #666;
}

.game-status {
    font-size: 0.9em;
    font-weight: 600;
    color: #28a745;
}

.live-indicator {
    color: #ffc107;
}

/* Pick Section */
.pick-section {
    border-top: 1px solid #eee;
    padding-top: 20px;
    margin-top: 20px;
}

.pick-options {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    justify-content: center;
    flex-wrap: wrap;
}

.pick-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 15px 20px;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: bold;
    background: white;
    min-width: 120px;
}

.pick-option:hover {
    border-color: #007bff;
    background-color: #f8f9fa;
    transform: translateY(-1px);
}

.pick-option.selected,
.pick-option:has(input[type="radio"]:checked) {
    border-color: #007bff;
    background-color: #e3f2fd;
    box-shadow: 0 2px 8px rgba(0,123,255,0.2);
}

.pick-option input[type="radio"] {
    margin-bottom: 8px;
}

.pick-logo {
    width: 30px;
    height: 30px;
    margin: 5px 0;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));
}

.btn-pick {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1em;
    display: block;
    margin: 0 auto;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-pick:hover {
    background: linear-gradient(135deg, #0056b3, #004085);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.no-games {
    text-align: center;
    padding: 60px 20px;
    color: #666;
    font-size: 1.1em;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

/* Responsive Design */
@media (max-width: 768px) {
    .teams-display {
        flex-direction: column;
        gap: 15px;
    }
    
    .game-vs {
        align-self: center;
        margin-top: 0;
    }
    
    .betting-stats {
        flex-direction: column;
        gap: 10px;
    }
    
    .pick-options {
        flex-direction: column;
        align-items: center;
    }
    
    .pick-option {
        width: 100%;
        max-width: 250px;
    }
}
</style>
{% endblock %}'''

    return template_content

def apply_template_integration():
    """Apply the enhanced template with logos and betting odds"""
    
    print("🚀 INTEGRATING TEAM LOGOS AND BETTING ODDS")
    print("=" * 50)
    
    # Backup current template
    backup_file = backup_current_template()
    
    # Create enhanced template
    enhanced_template = create_enhanced_games_template()
    
    # Write enhanced template
    template_path = "templates/games.html"
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_template)
        print(f"✅ Enhanced template written to {template_path}")
        
        # Verify file was written correctly
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 5000:  # Should be substantial
                print(f"✅ Template verification passed ({len(content)} characters)")
            else:
                print(f"⚠️  Template seems short ({len(content)} characters)")
                
    except Exception as e:
        print(f"❌ Error writing template: {e}")
        if backup_file and os.path.exists(backup_file):
            shutil.copy2(backup_file, template_path)
            print(f"✅ Restored from backup: {backup_file}")
        return False
    
    # Verify logo files exist
    logo_dir = "static/images"
    if os.path.exists(logo_dir):
        logo_files = [f for f in os.listdir(logo_dir) if f.endswith('.svg')]
        print(f"✅ Found {len(logo_files)} team logo files")
        if len(logo_files) >= 30:
            print("✅ Logo collection appears complete")
        else:
            print(f"⚠️  Only {len(logo_files)} logos found, expecting ~32")
    else:
        print(f"❌ Logo directory not found: {logo_dir}")
        return False
    
    print("\n🎯 INTEGRATION SUMMARY:")
    print("✅ Enhanced games.html with team logos")
    print("✅ Added Vegas betting odds display")
    print("✅ Improved responsive design")
    print("✅ Enhanced visual styling")
    print("✅ Fallback handling for missing logos")
    
    print(f"\n📁 Backup created: {backup_file}")
    print("🔄 Restart Flask server to see changes")
    
    return True

if __name__ == "__main__":
    success = apply_template_integration()
    if success:
        print("\n🚀 READY: Restart Flask server to see enhanced games page!")
    else:
        print("\n❌ Integration failed - check errors above")