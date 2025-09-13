#!/usr/bin/env python3
"""
Simple Ubuntu scoring fix script for WSH@GB game
Handles database schema differences and fixes Week 2, 2025 scoring
"""

import sqlite3
import os
import sys


def find_database():
    """Find the database file"""
    paths = [
        '/home/casa/CasaTodos/nfl_fantasy.db',
        '/home/casa/CasaTodos/database.db',
        './nfl_fantasy.db',
        './database.db'
    ]
    
    for path in paths:
        if os.path.exists(path):
            print(f"✅ Found database: {path}")
            return path
    
    print("❌ Database not found!")
    return None


def main():
    """Main fix function"""
    print("🏈 UBUNTU SCORING FIX - WSH@GB Game")
    print("=" * 40)
    
    # Find database
    db_path = find_database()
    if not db_path:
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n=== FINDING WSH@GB GAME ===")
        
        # Find WSH@GB game in Week 2, 2025
        cursor.execute('''
            SELECT id, home_team, away_team 
            FROM nfl_games 
            WHERE week = 2 AND year = 2025 
            AND ((home_team IN ('GB', 'Green Bay') AND away_team IN ('WSH', 'WAS', 'Washington')) 
                 OR (away_team IN ('GB', 'Green Bay') AND home_team IN ('WSH', 'WAS', 'Washington')))
        ''')
        
        game = cursor.fetchone()
        
        if not game:
            # Fallback - show all Week 2 games
            print("Direct search failed. All Week 2, 2025 games:")
            cursor.execute('''
                SELECT id, home_team, away_team 
                FROM nfl_games 
                WHERE week = 2 AND year = 2025
            ''')
            games = cursor.fetchall()
            
            for game_id, home, away in games:
                print(f"  Game {game_id}: {away} @ {home}")
            
            # Look for any game with GB or WSH
            for game_id, home, away in games:
                if ('GB' in home or 'GB' in away or 
                    'Green' in home or 'Green' in away or
                    'WSH' in home or 'WSH' in away or
                    'Washington' in home or 'Washington' in away):
                    print(f"🎯 Possible target: Game {game_id}: {away} @ {home}")
                    game = (game_id, home, away)
                    break
            
            if not game:
                print("❌ Could not find WSH@GB game!")
                sys.exit(1)
        
        game_id, home_team, away_team = game
        print(f"🎯 Target game: {game_id} ({away_team} @ {home_team})")
        
        print("\n=== CURRENT PICKS ===")
        
        # Show current picks
        cursor.execute('''
            SELECT u.username, up.selected_team, up.is_correct
            FROM user_picks up
            JOIN users u ON up.user_id = u.id
            WHERE up.game_id = ? AND u.is_admin = 0
            ORDER BY u.username
        ''', (game_id,))
        
        picks = cursor.fetchall()
        
        if not picks:
            print("❌ No picks found!")
            sys.exit(1)
        
        for username, selected, correct in picks:
            status = "✅" if correct == 1 else "❌"
            print(f"  {username}: {selected} {status}")
        
        print("\n⚠️  APPLYING FIX...")
        print("Result: GB 27 - WSH 18 (Green Bay won)")
        
        # Determine team codes from the game
        gb_team = None
        wsh_team = None
        
        # Check which team is GB/WSH
        if ('GB' in home_team or 'Green' in home_team):
            gb_team = home_team
            wsh_team = away_team
        elif ('GB' in away_team or 'Green' in away_team):
            gb_team = away_team
            wsh_team = home_team
        elif ('WSH' in home_team or 'Washington' in home_team):
            wsh_team = home_team
            gb_team = away_team
        elif ('WSH' in away_team or 'Washington' in away_team):
            wsh_team = away_team
            gb_team = home_team
        else:
            # Manual assignment based on known teams
            print(f"Teams: {home_team} vs {away_team}")
            print("Assuming GB=home, WSH=away based on context")
            gb_team = home_team
            wsh_team = away_team
        
        print(f"GB team code: {gb_team}")
        print(f"WSH team code: {wsh_team}")
        
        # Fix GB picks (winners - should be correct)
        cursor.execute('''
            UPDATE user_picks 
            SET is_correct = 1 
            WHERE game_id = ? AND selected_team = ?
        ''', (game_id, gb_team))
        
        gb_fixed = cursor.rowcount
        
        # Fix WSH picks (losers - should be incorrect)
        cursor.execute('''
            UPDATE user_picks 
            SET is_correct = 0 
            WHERE game_id = ? AND selected_team = ?
        ''', (game_id, wsh_team))
        
        wsh_fixed = cursor.rowcount
        
        print(f"✅ Fixed {gb_fixed} GB picks (set to correct)")
        print(f"✅ Fixed {wsh_fixed} WSH picks (set to incorrect)")
        
        # Try to update game scores (if columns exist)
        try:
            if home_team == gb_team:
                cursor.execute('''
                    UPDATE nfl_games 
                    SET home_score = 27, away_score = 18, is_final = 1
                    WHERE id = ?
                ''', (game_id,))
            else:
                cursor.execute('''
                    UPDATE nfl_games 
                    SET home_score = 18, away_score = 27, is_final = 1
                    WHERE id = ?
                ''', (game_id,))
            print("✅ Updated game scores")
        except sqlite3.OperationalError:
            print("⚠️  Score columns not available (OK)")
        
        # Verify fix
        print("\n=== VERIFICATION ===")
        cursor.execute('''
            SELECT u.username, up.selected_team, up.is_correct
            FROM user_picks up
            JOIN users u ON up.user_id = u.id
            WHERE up.game_id = ? AND u.is_admin = 0
            ORDER BY up.is_correct DESC, u.username
        ''', (game_id,))
        
        picks_after = cursor.fetchall()
        correct_count = 0
        
        for username, selected, correct in picks_after:
            if correct == 1:
                print(f"  ✅ {username}: {selected} (1 point)")
                correct_count += 1
            else:
                print(f"  ❌ {username}: {selected} (0 points)")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"\n🎉 FIX COMPLETED!")
        print(f"   {correct_count} users now have correct picks")
        print(f"   Weekly leaderboard should show proper results")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
