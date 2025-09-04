import sqlite3
import datetime

def debug_week1():
    print("Week 1 Debug Script")
    print("=" * 30)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        current_year = datetime.datetime.now().year
        
        # Check Week 1 games
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = ?', (current_year,))
        week1_count = cursor.fetchone()[0]
        print(f"Week 1 games: {week1_count}")
        
        if week1_count > 0:
            cursor.execute('''
                SELECT game_id, home_team, away_team, game_date, is_monday_night, is_thursday_night 
                FROM nfl_games WHERE week = 1 AND year = ? 
                ORDER BY game_date
            ''', (current_year,))
            
            games = cursor.fetchall()
            print("\nWeek 1 Games:")
            for game in games:
                print(f"  {game[2]} @ {game[1]} on {game[3]} {'(TNF)' if game[5] else '(MNF)' if game[4] else ''}")
        
        # Check all weeks
        cursor.execute('''
            SELECT week, COUNT(*) 
            FROM nfl_games 
            WHERE year = ? 
            GROUP BY week 
            ORDER BY week
        ''', (current_year,))
        
        all_weeks = cursor.fetchall()
        print(f"\nAll weeks with games:")
        for week, count in all_weeks:
            print(f"  Week {week}: {count} games")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_week1()
