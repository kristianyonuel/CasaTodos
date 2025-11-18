#!/usr/bin/env python3
import sqlite3

def check_weeks():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        print("=== AVAILABLE WEEKS IN DATABASE ===")
        cursor.execute("""
            SELECT week, year, COUNT(*) as game_count 
            FROM nfl_games 
            GROUP BY week, year 
            ORDER BY year DESC, week DESC
        """)
        
        weeks = cursor.fetchall()
        for week, year, count in weeks:
            print(f"Week {week}, {year}: {count} games")
        
        print("\n=== WEEK 6 GAMES SPECIFICALLY ===")
        cursor.execute("""
            SELECT game_id, away_team, home_team, game_date, is_final
            FROM nfl_games 
            WHERE week = 6 AND year = 2025
            ORDER BY game_date
        """)
        
        week6_games = cursor.fetchall()
        if week6_games:
            print(f"Found {len(week6_games)} games for Week 6, 2025:")
            for game_id, away, home, date, is_final in week6_games:
                status = "Final" if is_final else "Scheduled"
                print(f"  Game {game_id}: {away} @ {home} ({date}) - {status}")
        else:
            print("No games found for Week 6, 2025")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_weeks()