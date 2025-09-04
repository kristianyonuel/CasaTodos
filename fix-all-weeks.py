import sqlite3
import datetime
from app import ensure_games_exist, validate_nfl_games

def fix_all_weeks():
    """Fix and create games for all weeks"""
    print("Fixing games for all 18 weeks...")
    
    current_year = datetime.datetime.now().year
    fixed_weeks = 0
    
    for week in range(1, 19):
        try:
            print(f"Fixing Week {week}...")
            
            # Check current game count
            conn = sqlite3.connect('nfl_fantasy.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = ? AND year = ?', (week, current_year))
            before_count = cursor.fetchone()[0]
            conn.close()
            
            if before_count == 0:
                # Create games for this week
                after_count = ensure_games_exist(week, current_year)
                print(f"  ✓ Created {after_count} games for Week {week}")
                fixed_weeks += 1
            else:
                print(f"  ✓ Week {week} already has {before_count} games")
            
        except Exception as e:
            print(f"  ❌ Error fixing Week {week}: {e}")
            continue
    
    print(f"\nFixed {fixed_weeks} weeks")
    
    # Final validation
    if validate_nfl_games():
        print("✅ All weeks validated successfully")
    else:
        print("⚠️  Some weeks may still have issues")

if __name__ == "__main__":
    fix_all_weeks()
