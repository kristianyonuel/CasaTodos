import sqlite3

def emergency_week10_fix():
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("EMERGENCY WEEK 10 FIX")
    print("=" * 30)
    
    # Set all possible week settings to 10
    settings = [
        'current_week', 'display_week', 'picks_week', 'leaderboard_week',
        'week_override', 'active_week', 'nfl_week', 'game_week', 
        'score_week', 'espn_week', 'update_week', 'background_week',
        'force_week_10', 'override_week_calculation'
    ]
    
    for setting in settings:
        cursor.execute("""
            INSERT OR REPLACE INTO league_settings 
            (category, setting_name, setting_value, setting_type, display_name, description, is_public, is_editable, sort_order)
            VALUES ('system', ?, '10', 'integer', ?, 'FORCE WEEK 10', 0, 1, 99)
        """, (setting, setting.replace('_', ' ').title()))
        print(f"Set {setting} = 10")
    
    conn.commit()
    conn.close()
    print("All week settings forced to 10!")
    print("Restart Flask server now!")

if __name__ == "__main__":
    emergency_week10_fix()