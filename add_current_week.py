import sqlite3

conn = sqlite3.connect('/home/casa/CasaTodos/nfl_fantasy.db')
cursor = conn.cursor()

# Add current_week setting
cursor.execute("""
    INSERT OR REPLACE INTO league_settings 
    (category, setting_name, setting_value, setting_type, display_name, description, is_public, is_editable, sort_order)
    VALUES ('general', 'current_week', '9', 'integer', 'Current Week', 'Current NFL week being displayed', 1, 1, 5)
""")

conn.commit()
print("✅ Added current_week = 9 setting")
conn.close()