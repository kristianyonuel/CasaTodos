import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== FIXING MONDAY NIGHT FOOTBALL TIMES ===')

def parse_date(date_str):
    """Parse date string handling both formats"""
    try:
        # Try ISO format first (2025-09-08T00:20:00)
        return datetime.fromisoformat(date_str.replace('T', ' '))
    except:
        try:
            # Try standard format (2025-09-08 00:20:00)
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

# Get all MNF games that have midnight times (problematic)
cursor.execute('''
    SELECT id, home_team, away_team, game_date, week, year
    FROM nfl_games 
    WHERE is_monday_night = 1 
    AND (
        game_date LIKE '%00:15:00' OR
        game_date LIKE '%00:20:00'
    )
    ORDER BY year, week
''')

problematic_games = cursor.fetchall()

print(f'Found {len(problematic_games)} MNF games with midnight times:')
for game in problematic_games:
    print(f'  Week {game[4]}: {game[2]} @ {game[1]} - {game[3]}')

if problematic_games:
    print('\nFixing times to 8:15 PM ET (Monday Night Football standard)...')
    
    updates_made = 0
    for game in problematic_games:
        game_id = game[0]
        current_date = game[3]
        
        # Parse the current date
        dt = parse_date(current_date)
        if dt is None:
            print(f'  ❌ Could not parse date for Game {game_id}: {current_date}')
            continue
        
        # For midnight games, move to 8:15 PM on the same day
        # But if it's Tuesday midnight, move to Monday 8:15 PM
        if dt.hour == 0:  # Midnight games
            if dt.weekday() == 1:  # Tuesday
                # Move back to Monday 8:15 PM
                new_date = dt.replace(day=dt.day - 1, hour=20, minute=15, second=0)
            else:
                # Keep same day but change to 8:15 PM
                new_date = dt.replace(hour=20, minute=15, second=0)
            
            new_date_str = new_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Update the database
            cursor.execute('''
                UPDATE nfl_games 
                SET game_date = ? 
                WHERE id = ?
            ''', (new_date_str, game_id))
            
            day_old = dt.strftime('%A')
            day_new = new_date.strftime('%A')
            time_old = dt.strftime('%I:%M %p')
            time_new = new_date.strftime('%I:%M %p')
            
            print(f'  ✅ Game {game_id}: {day_old} {time_old} → {day_new} {time_new}')
            updates_made += 1
    
    # Commit changes
    conn.commit()
    print(f'\n🎉 Updated {updates_made} Monday Night Football games!')
    print('   All MNF games now at 8:15 PM ET (7:15 PM AST) on proper day')
    
else:
    print('✅ No problematic MNF games found!')

# Verify the fix
print('\n=== VERIFICATION ===')
cursor.execute('''
    SELECT id, home_team, away_team, game_date, week, year
    FROM nfl_games 
    WHERE is_monday_night = 1 
    ORDER BY year, week
''')

all_mnf = cursor.fetchall()
print(f'All {len(all_mnf)} Monday Night Football games:')
for game in all_mnf:
    dt = parse_date(game[3])
    if dt:
        day_name = dt.strftime('%A')
        time_str = dt.strftime('%I:%M %p')
        print(f'  Week {game[4]}: {game[2]} @ {game[1]} - {day_name} {time_str} ET')
    else:
        print(f'  Week {game[4]}: {game[2]} @ {game[1]} - ERROR: {game[3]}')

conn.close()
print('\n✅ Monday Night Football timezone fix complete!')