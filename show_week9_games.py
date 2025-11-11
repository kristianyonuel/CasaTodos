#!/usr/bin/env python3

import sqlite3

def show_week9_games():
    """Show all Week 9 game results from the database"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🏈 WEEK 9 GAME RESULTS IN DATABASE")
    print("=" * 80)
    
    cursor.execute('''
        SELECT game_id, week, home_team, away_team, home_score, away_score, winner, game_date
        FROM nfl_games 
        WHERE week = 9 
        ORDER BY game_id
    ''')
    
    games = cursor.fetchall()
    
    for game in games:
        game_id, week, home_team, away_team, home_score, away_score, winner, game_date = game
        print(f"Game {game_id}: {away_team} {away_score} - {home_team} {home_score}")
        print(f"  Winner: {winner}")
        print(f"  Date: {game_date}")
        print()
    
    conn.close()

if __name__ == "__main__":
    show_week9_games()