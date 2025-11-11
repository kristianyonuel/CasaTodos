import sqlite3

def update_current_week_to_10():
    """Update the current_week setting from 9 to 10"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔧 UPDATING CURRENT WEEK TO 10")
    print("=" * 40)
    
    # Check current setting
    cursor.execute("SELECT setting_name, setting_value FROM league_settings WHERE setting_name = 'current_week'")
    current_setting = cursor.fetchone()
    
    if current_setting:
        print(f"Current setting: {current_setting[0]} = {current_setting[1]}")
        
        # Update to Week 10
        cursor.execute("UPDATE league_settings SET setting_value = '10' WHERE setting_name = 'current_week'")
        updated_rows = cursor.rowcount
        
        if updated_rows > 0:
            print("✅ Updated current_week from 9 to 10")
        else:
            print("❌ Failed to update current_week")
            
    else:
        print("❌ current_week setting not found")
        print("➕ Adding current_week = 10 setting...")
        
        cursor.execute('''
            INSERT INTO league_settings (category, setting_name, setting_value, setting_type, display_name, description, is_public, is_editable, sort_order)
            VALUES ('general', 'current_week', '10', 'integer', 'Current Week', 'Current NFL week being displayed', 1, 1, 5)
        ''')
        
        print("✅ Added current_week = 10")
    
    # Verify the change
    cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
    new_value = cursor.fetchone()
    
    if new_value:
        print(f"✅ Verified: current_week = {new_value[0]}")
    
    conn.commit()
    conn.close()
    
    print("\n🎯 RESULT:")
    print("✅ System should now show Week 10 for picks")
    print("🏈 Tonight's game: Raiders @ Broncos (9:15 PM)")

if __name__ == "__main__":
    update_current_week_to_10()