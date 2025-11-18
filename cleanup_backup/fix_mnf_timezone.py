import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

print('=== FIXING MONDAY NIGHT FOOTBALL TIMES ===')

# Monday Night Football typically starts at 8:15 PM ET (20:15)
# This will be 7:15 PM AST, keeping it on Monday in both timezones

# Get all MNF games across all weeks that have problematic times
cursor.execute('''
    SELECT id, home_team, away_team, game_date, week, year
    FROM nfl_games 
    WHERE is_monday_night = 1 
    AND (
        game_date LIKE '%-10-21 00:%' OR  -- Tuesday midnight (should be Monday night)
        game_date LIKE '%-10-20 00:%' OR  -- Monday midnight (should be Monday night)
        game_date LIKE '%00:15:00' OR     -- Any midnight games
        game_date LIKE '%00:20:00'        -- Any midnight games
    )
    ORDER BY year, week
''')

problematic_games = cursor.fetchall()

print(f'Found {len(problematic_games)} problematic MNF games:')
for game in problematic_games:
    print(f'  Week {game[4]}: {game[2]} @ {game[1]} - {game[3]}')

if problematic_games:
    print('\nFixing times to 8:15 PM ET (Monday Night Football standard time)...')
    
    updates_made = 0
    for game in problematic_games:
        game_id = game[0]
        current_date = game[3]
        
        # Parse the current date
        try:
            dt = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
            
            # Determine the correct Monday date
            if dt.hour == 0:  # Midnight games
                if dt.weekday() == 1:  # Tuesday
                    # Move back to Monday
                    new_date = dt.replace(day=dt.day - 1, hour=20, minute=15, second=0)
                elif dt.weekday() == 0:  # Monday midnight
                    # Keep Monday but change to 8:15 PM
                    new_date = dt.replace(hour=20, minute=15, second=0)
                else:
                    # For other days, assume it should be the previous Monday
                    days_back = (dt.weekday() - 0) % 7
                    if days_back == 0:
                        days_back = 0  # Already Monday
                    new_date = dt.replace(day=dt.day - days_back, hour=20, minute=15, second=0)
                
                new_date_str = new_date.strftime('%Y-%m-%d %H:%M:%S')
                
                # Update the database
                cursor.execute('''
                    UPDATE nfl_games 
                    SET game_date = ? 
                    WHERE id = ?
                ''', (new_date_str, game_id))
                
                print(f'  ✅ Updated Game {game_id}: {current_date} → {new_date_str}')
                updates_made += 1
                
        except Exception as e:
            print(f'  ❌ Error updating Game {game_id}: {e}')
    
    # Commit changes
    conn.commit()
    print(f'\n🎉 Successfully updated {updates_made} Monday Night Football games!')
    print('   All MNF games now show at 8:15 PM ET (7:15 PM AST) on Monday')
    
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
    dt = datetime.strptime(game[3], '%Y-%m-%d %H:%M:%S')
    day_name = dt.strftime('%A')
    time_str = dt.strftime('%I:%M %p')
    print(f'  Week {game[4]}: {game[2]} @ {game[1]} - {day_name} {time_str} ET')

conn.close()
print('\n✅ Monday Night Football timezone fix complete!')