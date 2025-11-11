import sqlite3

def patch_score_updater_to_week10():
    """Create a patched version of fix_score_updater.py that forces Week 10"""
    
    print("🔧 CREATING PATCHED SCORE UPDATER FOR WEEK 10")
    print("=" * 50)
    
    # Read the current fix_score_updater.py
    try:
        with open('fix_score_updater.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ fix_score_updater.py not found")
        return False
    
    # Create a patched version that always returns 10
    patched_content = content.replace(
        'return result[0] if result else 9  # Default to week 9',
        'return 10  # FORCED TO WEEK 10'
    )
    
    # Also replace any other Week 9 defaults
    patched_content = patched_content.replace(
        'return result[0] if result else 9',
        'return 10  # FORCED TO WEEK 10'
    )
    
    # Save the patched version
    with open('fix_score_updater_week10.py', 'w') as f:
        f.write(patched_content)
    
    print("✅ Created fix_score_updater_week10.py")
    
    # Now let's also create a simple direct override
    override_content = '''#!/usr/bin/env python3
"""
Emergency Week 10 override - patches any hardcoded Week 9 logic
"""

import sqlite3

def emergency_week10_override():
    """Force everything to Week 10"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🚨 EMERGENCY WEEK 10 OVERRIDE ACTIVATED")
    print("=" * 50)
    
    # Add every possible setting that might control week display
    override_settings = [
        ('current_week', '10'),
        ('display_week', '10'), 
        ('picks_week', '10'),
        ('leaderboard_week', '10'),
        ('week_override', '10'),
        ('active_week', '10'),
        ('nfl_week', '10'),
        ('game_week', '10'),
        ('score_week', '10'),
        ('espn_week', '10'),
        ('update_week', '10'),
        ('background_week', '10')
    ]
    
    for setting_name, value in override_settings:
        cursor.execute("""
            INSERT OR REPLACE INTO league_settings 
            (category, setting_name, setting_value, setting_type, display_name, description, is_public, is_editable, sort_order)
            VALUES ('system', ?, ?, 'integer', ?, 'EMERGENCY WEEK 10 OVERRIDE', 0, 1, 99)
        """, (setting_name, value, setting_name.replace('_', ' ').title()))
        print(f"   ✅ {setting_name} = {value}")
    
    conn.commit()
    conn.close()
    
    print("\\n🎯 ALL WEEK SETTINGS FORCED TO 10")
    print("   Flask app should now show Week 10!")
    
if __name__ == "__main__":
    emergency_week10_override()
'''
    
    with open('emergency_week10_override.py', 'w') as f:
        f.write(override_content)
    
    print("✅ Created emergency_week10_override.py")
    
    # Run the emergency override
    exec(override_content)
    
    return True

if __name__ == "__main__":
    patch_score_updater_to_week10()