import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check tables
        print('=== Database Tables ===')
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f'  - {table[0]}')
        
        # Check if it's nfl_games or games
        table_name = None
        for table in tables:
            if 'game' in table[0].lower():
                table_name = table[0]
                break
        
        if not table_name:
            print('No games table found!')
            print('Available tables:')
            for table in tables:
                print(f'  - {table[0]}')
            return
            
        print(f'\n=== Using table: {table_name} ===')
        
        # Get current week games (Week 2)
        cursor.execute(f'''
            SELECT id, game_date, away_team, home_team, 
                   strftime('%w', game_date) as day_of_week
            FROM {table_name}
            WHERE week = 2 AND year = 2025 
            ORDER BY game_date
        ''')
        
        games = cursor.fetchall()
        print(f'\nFound {len(games)} games for Week 2, 2025:')
        
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        monday_games = []
        
        for game in games:
            day_name = day_names[int(game['day_of_week'])]
            print(f'  Game {game["id"]}: {game["away_team"]} @ {game["home_team"]} - {game["game_date"]} ({day_name})')
            
            if int(game['day_of_week']) == 1:  # Monday
                monday_games.append(game)
        
        print(f'\n=== Monday Games ({len(monday_games)} found) ===')
        for game in monday_games:
            print(f'  {game["away_team"]} @ {game["home_team"]} - {game["game_date"]} (ID: {game["id"]})')
        
        if monday_games:
            # Apply our detection logic
            cursor.execute(f'''
                SELECT id, game_date, away_team, home_team 
                FROM {table_name}
                WHERE week = 2 AND year = 2025 
                AND strftime('%w', game_date) = '1'
                ORDER BY game_date DESC, id DESC
                LIMIT 1
            ''')
            
            detected_mnf = cursor.fetchone()
            if detected_mnf:
                print(f'\n=== Detected Monday Night Football ===')
                print(f'  {detected_mnf["away_team"]} @ {detected_mnf["home_team"]} (ID: {detected_mnf["id"]})')
        
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_database()
