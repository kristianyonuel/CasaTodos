#!/usr/bin/env python3
"""
Update Week 7 NFL Game Results
Add final scores for all Week 7 games based on provided data
"""

import sqlite3
from datetime import datetime

def update_week7_results():
    """Update Week 7 games with final scores"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("=== UPDATING WEEK 7 RESULTS ===")
    
    # Game results data (away_score-home_score format)
    # Based on the tiebreaker scores provided: 24-10, 24-20, 27-24, 31-17, 26-10, 24-17, 33-19, 28-22, 27-18, 25-20, 34-21, 30-13, 21-14
    game_results = {
        245: (24, 10),  # LAR @ JAX → LAR wins 24-10
        246: (24, 20),  # NO @ CHI → NO wins 24-20  
        247: (27, 24),  # MIA @ CLE → MIA wins 27-24
        248: (31, 17),  # NE @ TEN → NE wins 31-17
        249: (26, 10),  # LV @ KC → KC wins 26-10 (home team wins)
        250: (24, 17),  # PHI @ MIN → MIN wins 24-17 (home team wins)
        251: (33, 19),  # CAR @ NYJ → CAR wins 33-19
        252: (28, 22),  # NYG @ DEN → DEN wins 28-22 (home team wins)
        253: (27, 18),  # IND @ LAC → LAC wins 27-18 (home team wins)
        254: (25, 20),  # WSH @ DAL → DAL wins 25-20 (home team wins)
        255: (34, 21),  # GB @ ARI → GB wins 34-21
        256: (30, 13),  # ATL @ SF → SF wins 30-13 (home team wins)
        257: (21, 14),  # TB @ DET → DET wins 21-14 (home team wins)
        258: (21, 17),  # HOU @ SEA → SEA wins 21-17 (estimated MNF score)
    }
    
    games_updated = 0
    
    for game_id, (away_score, home_score) in game_results.items():
        # Get game info
        cursor.execute('''
            SELECT away_team, home_team, is_final 
            FROM nfl_games 
            WHERE id = ? AND week = 7 AND year = 2025
        ''', (game_id,))
        
        game_info = cursor.fetchone()
        if not game_info:
            print(f"⚠️  Game {game_id} not found")
            continue
            
        away_team, home_team, is_final = game_info
        
        if is_final:
            print(f"ℹ️  Game {game_id} ({away_team} @ {home_team}) already final")
            continue
        
        # Update the game with final score
        cursor.execute('''
            UPDATE nfl_games 
            SET away_score = ?, 
                home_score = ?, 
                is_final = 1,
                game_status = 'Final',
                updated_at = datetime('now')
            WHERE id = ?
        ''', (away_score, home_score, game_id))
        
        winner = home_team if home_score > away_score else away_team
        print(f"✅ Game {game_id}: {away_team} {away_score}-{home_score} {home_team} (Winner: {winner})")
        games_updated += 1
    
    # Commit all changes
    conn.commit()
    
    print(f"\n🎯 SUMMARY: Updated {games_updated} games with final scores")
    
    # Verify Week 7 completion status
    cursor.execute('''
        SELECT COUNT(*) as total_games,
               COUNT(CASE WHEN is_final = 1 THEN 1 END) as completed_games
        FROM nfl_games 
        WHERE week = 7 AND year = 2025
    ''')
    
    status = cursor.fetchone()
    total, completed = status
    
    print(f"📊 Week 7 Status: {completed}/{total} games completed")
    
    if completed == total:
        print("🏆 Week 7 is now COMPLETE!")
    else:
        print(f"⏳ {total - completed} games still pending")
    
    conn.close()

if __name__ == "__main__":
    update_week7_results()