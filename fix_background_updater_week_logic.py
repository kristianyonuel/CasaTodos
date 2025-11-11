import sqlite3

def fix_background_updater_week_logic():
    """Fix the _get_current_nfl_week method to use database settings"""
    
    print("🔧 FIXING BACKGROUND UPDATER WEEK LOGIC")
    print("=" * 50)
    
    # Read the current background_updater.py file
    try:
        with open('C:\\Users\\cjuarbe\\Casa\\CasaTodos\\background_updater.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read background_updater.py: {e}")
        return False
    
    # Find the current _get_current_nfl_week method
    if '_get_current_nfl_week(self) -> Optional[int]:' not in content:
        print("❌ Could not find _get_current_nfl_week method")
        return False
    
    # Create the improved method that checks database first
    improved_method = '''    def _get_current_nfl_week(self) -> Optional[int]:
        """Determine current NFL week - first from database, then by date"""
        try:
            # First, try to get current week from database settings
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = 'current_week'")
            result = cursor.fetchone()
            
            if result:
                week = int(result[0])
                conn.close()
                return week
            
            # Check for other week settings as fallback
            for setting in ['display_week', 'picks_week', 'week_override']:
                cursor.execute("SELECT setting_value FROM league_settings WHERE setting_name = ?", (setting,))
                result = cursor.fetchone()
                if result:
                    week = int(result[0])
                    conn.close()
                    return week
            
            conn.close()
            
            # Fallback: Calculate week based on date (original logic)
            # NFL 2025 season starts in early September
            # Week 1 typically starts around September 5-8
            season_start = datetime(2025, 9, 5)  # Approximate start date
            current_date = datetime.now()

            if current_date < season_start:
                return None  # Season hasn't started

            # Calculate weeks since season start
            days_since_start = (current_date - season_start).days
            week = (days_since_start // 7) + 1

            # NFL regular season is 18 weeks
            if week > 18:
                return None  # Season is over

            return week

        except Exception as e:
            logger.error(f"Error determining current NFL week: {e}")
            # Emergency fallback - return 10 for current week
            return 10'''
    
    # Find the start and end of the current method
    start_pattern = 'def _get_current_nfl_week(self) -> Optional[int]:'
    start_index = content.find(start_pattern)
    
    if start_index == -1:
        print("❌ Could not find method start")
        return False
    
    # Find the next method or class definition after this one
    lines = content[start_index:].split('\n')
    method_lines = []
    indent_level = None
    
    for i, line in enumerate(lines):
        if i == 0:  # First line
            method_lines.append(line)
            continue
            
        # Determine indent level from first non-empty line
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
        
        # If we hit a line with same or less indentation (and it's not empty), we've reached the end
        if line.strip() and indent_level is not None:
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= 4:  # Method level indentation
                break
                
        method_lines.append(line)
    
    old_method = '\n'.join(method_lines)
    
    # Replace the method
    new_content = content.replace(old_method, improved_method)
    
    # Save the fixed version
    try:
        with open('background_updater_fixed.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Created background_updater_fixed.py")
    except Exception as e:
        print(f"❌ Could not write fixed file: {e}")
        return False
    
    # Now replace the original file
    try:
        import shutil
        shutil.copy('C:\\Users\\cjuarbe\\Casa\\CasaTodos\\background_updater.py', 'background_updater_backup.py')
        print("✅ Created backup: background_updater_backup.py")
        
        with open('C:\\Users\\cjuarbe\\Casa\\CasaTodos\\background_updater.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Updated background_updater.py")
        
    except Exception as e:
        print(f"❌ Could not update original file: {e}")
        print("   You can manually copy background_updater_fixed.py over the original")
        return False
    
    print("\n🎯 BACKGROUND UPDATER FIXED!")
    print("   - Now checks database settings first")
    print("   - Falls back to date calculation if needed")
    print("   - Emergency fallback to Week 10")
    print("\n🔄 Restart Flask server to apply changes")
    
    return True

if __name__ == "__main__":
    fix_background_updater_week_logic()