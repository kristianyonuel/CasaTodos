#!/usr/bin/env python3
"""
TEMPLATE PROTECTION AND RESTORATION SYSTEM
Protects the games.html template from corruption and auto-restores it
"""

import os
import shutil
import hashlib
from datetime import datetime

TEMPLATE_PATH = "templates/games.html"
BACKUP_PATH = "templates/games_master_backup.html"

def get_file_hash(filepath):
    """Get MD5 hash of a file"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def create_master_backup():
    """Create a master backup of the working template"""
    if os.path.exists(TEMPLATE_PATH):
        shutil.copy2(TEMPLATE_PATH, BACKUP_PATH)
        print(f"✅ Master backup created: {BACKUP_PATH}")
        return True
    return False

def validate_template():
    """Check if the template is valid Jinja2 syntax"""
    if not os.path.exists(TEMPLATE_PATH):
        return False, "Template file does not exist"
    
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic validation checks
        if not content.strip():
            return False, "Template is empty"
        
        if not content.startswith("{% extends"):
            return False, "Template missing extends directive"
        
        if not content.endswith("{% endblock %}"):
            return False, "Template missing endblock"
        
        # Check for balanced blocks
        blocks = content.count("{% block")
        endblocks = content.count("{% endblock")
        if blocks != endblocks:
            return False, f"Unbalanced blocks: {blocks} blocks, {endblocks} endblocks"
        
        # Check for balanced if statements
        ifs = content.count("{% if")
        endifs = content.count("{% endif")
        if ifs != endifs:
            return False, f"Unbalanced if statements: {ifs} ifs, {endifs} endifs"
        
        # Check for balanced for loops
        fors = content.count("{% for")
        endfors = content.count("{% endfor")
        if fors != endfors:
            return False, f"Unbalanced for loops: {fors} fors, {endfors} endfors"
        
        return True, "Template is valid"
        
    except Exception as e:
        return False, f"Error reading template: {e}"

def restore_from_backup():
    """Restore template from master backup"""
    if os.path.exists(BACKUP_PATH):
        shutil.copy2(BACKUP_PATH, TEMPLATE_PATH)
        print(f"✅ Template restored from backup: {BACKUP_PATH}")
        return True
    return False

def create_clean_template():
    """Create a clean, simple games.html template"""
    
    clean_template = '''{% extends "base.html" %}

{% block title %}Week {{ current_week }} Games{% endblock %}

{% block content %}
<div class="container">
    <h1>🏈 Week {{ current_week }} Games</h1>
    
    {% if games %}
        {% for game in games %}
        <div class="game-card">
            <div class="game-header">
                <h3>{{ game.away_team }} @ {{ game.home_team }}</h3>
                {% if game.game_date %}
                <div class="game-time">{{ game.game_date.strftime('%A, %B %d at %I:%M %p') }}</div>
                {% endif %}
            </div>
            
            {% if session.user_id %}
            <div class="pick-section">
                <form method="POST">
                    <input type="hidden" name="game_id" value="{{ game.game_id }}">
                    
                    <div class="pick-options">
                        <label class="pick-option">
                            <input type="radio" name="pick" value="{{ game.away_team }}" 
                                   {% if game.user_pick == game.away_team %}checked{% endif %}>
                            {{ game.away_team }}
                        </label>
                        
                        <label class="pick-option">
                            <input type="radio" name="pick" value="{{ game.home_team }}" 
                                   {% if game.user_pick == game.home_team %}checked{% endif %}>
                            {{ game.home_team }}
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
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
}

.game-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.game-header h3 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 1.3em;
}

.game-time {
    color: #666;
    font-size: 0.9em;
    margin-bottom: 15px;
}

.pick-section {
    border-top: 1px solid #eee;
    padding-top: 15px;
}

.pick-options {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
    justify-content: center;
}

.pick-option {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    border: 2px solid #ddd;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: bold;
}

.pick-option:hover {
    border-color: #007bff;
    background-color: #f8f9fa;
}

.pick-option:has(input[type="radio"]:checked) {
    border-color: #007bff;
    background-color: #e3f2fd;
}

.pick-option input[type="radio"] {
    margin-right: 8px;
}

.btn-pick {
    background: #007bff;
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1em;
    display: block;
    margin: 0 auto;
    font-weight: bold;
}

.btn-pick:hover {
    background: #0056b3;
}

.no-games {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 1.1em;
}
</style>
{% endblock %}'''

    try:
        with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
            f.write(clean_template)
        print(f"✅ Clean template created: {TEMPLATE_PATH}")
        return True
    except Exception as e:
        print(f"❌ Error creating clean template: {e}")
        return False

def main():
    """Main template protection function"""
    print("🛡️  TEMPLATE PROTECTION SYSTEM")
    print("=" * 40)
    
    # Check if template exists and is valid
    is_valid, message = validate_template()
    
    if is_valid:
        print(f"✅ Template is valid: {message}")
        
        # Create/update master backup
        create_master_backup()
        
    else:
        print(f"❌ Template is invalid: {message}")
        
        # Try to restore from backup first
        if restore_from_backup():
            is_valid, message = validate_template()
            if is_valid:
                print("✅ Successfully restored from backup")
            else:
                print("❌ Backup is also corrupted, creating clean template")
                create_clean_template()
        else:
            print("⚠️ No backup found, creating clean template")
            create_clean_template()
    
    # Final validation
    is_valid, message = validate_template()
    if is_valid:
        print("🎉 Template protection complete - games.html is ready!")
    else:
        print(f"❌ Failed to create valid template: {message}")

if __name__ == "__main__":
    main()