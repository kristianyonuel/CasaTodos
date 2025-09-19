#!/usr/bin/env python3
"""
Emergency Manual Score Update
Run this when automatic scoring system is not working
"""
import sqlite3
from datetime import datetime

def manual_score_update():
    """Manually update scores for known completed games"""
    print("🚨 EMERGENCY MANUAL SCORE UPDATE")
    print("=" * 50)
    print()
    
    # Connect to database
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Known game results that need to be manually entered
    # ADD NEW RESULTS HERE AS GAMES COMPLETE
    known_results = [
        # Week 3 - Buffalo game (already applied)
        {
            'week': 3,
            'year': 2025,
            'away_team': 'MIA',
            'home_team': 'BUF', 
            'away_score': 21,
            'home_score': 31,
            'winner': 'BUF'
        },
        # ADD MORE RESULTS HERE AS NEEDED
        # Example format:
        # {
        #     'week': 3,
        #     'year': 2025,
        #     'away_team': 'HOU',
        #     'home_team': 'JAX',
        #     'away_score': 17,
        #     'home_score': 24,
        #     'winner': 'JAX'
        # },
    ]
    
    games_updated = 0
    picks_scored = 0
    
    for result in known_results:
        try:
            # Find the game
            cursor.execute('''
                SELECT id, away_team, home_team, is_final
                FROM nfl_games
                WHERE away_team = ? AND home_team = ? 
                  AND week = ? AND year = ?
            ''', (result['away_team'], result['home_team'], 
                  result['week'], result['year']))
            
            game = cursor.fetchone()
            if not game:
                print(f"⚠️  Game not found: {result['away_team']} @ {result['home_team']} Week {result['week']}")
                continue
            
            if game['is_final']:
                print(f"✅ Already final: {result['away_team']} @ {result['home_team']}")
                continue
            
            # Update game score
            cursor.execute('''
                UPDATE nfl_games 
                SET away_score = ?, home_score = ?, is_final = 1
                WHERE id = ?
            ''', (result['away_score'], result['home_score'], game['id']))
            
            print(f"🏈 Updated: {result['away_team']} {result['away_score']} - {result['home_score']} {result['home_team']}")
            games_updated += 1
            
            # Score all picks for this game
            cursor.execute('''
                SELECT up.id, up.user_id, u.username, up.selected_team
                FROM user_picks up
                JOIN users u ON up.user_id = u.id
                WHERE up.game_id = ? AND u.is_admin = 0
            ''', (game['id'],))
            
            picks = cursor.fetchall()
            game_picks_scored = 0
            
            for pick in picks:
                is_correct = 1 if pick['selected_team'] == result['winner'] else 0
                cursor.execute('''
                    UPDATE user_picks 
                    SET is_correct = ?
                    WHERE id = ?
                ''', (is_correct, pick['id']))
                
                status = 'CORRECT' if is_correct else 'INCORRECT'
                print(f"   {pick['username']}: {pick['selected_team']} - {status}")
                game_picks_scored += 1
            
            picks_scored += game_picks_scored
            print(f"   ✅ Scored {game_picks_scored} picks")
            print()
            
        except Exception as e:
            print(f"❌ Error updating {result['away_team']} @ {result['home_team']}: {e}")
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print(f"📊 SUMMARY:")
    print(f"   Games updated: {games_updated}")
    print(f"   Picks scored: {picks_scored}")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if games_updated > 0:
        print("✅ Manual update completed successfully!")
        print("📤 Don't forget to upload the updated database to your server")
    else:
        print("ℹ️  No games needed updating")

def add_new_result():
    """Interactive function to add a new game result"""
    print("\n🔧 ADD NEW GAME RESULT")
    print("=" * 30)
    
    try:
        week = int(input("Week number: "))
        year = int(input("Year (2025): ") or 2025)
        away_team = input("Away team (3-letter code): ").upper()
        home_team = input("Home team (3-letter code): ").upper()
        away_score = int(input("Away team score: "))
        home_score = int(input("Home team score: "))
        
        winner = home_team if home_score > away_score else away_team
        
        print(f"\n📝 New result to add:")
        print(f"   {away_team} {away_score} - {home_score} {home_team} (Winner: {winner})")
        
        confirm = input("\nAdd this result? (y/n): ").lower()
        if confirm == 'y':
            # Add to the known_results list in the script
            result_code = f"""
        {{
            'week': {week},
            'year': {year},
            'away_team': '{away_team}',
            'home_team': '{home_team}',
            'away_score': {away_score},
            'home_score': {home_score},
            'winner': '{winner}'
        }},"""
            
            print("\n📋 Add this to the 'known_results' list in manual_score_update.py:")
            print(result_code)
            print("\nThen run the script again to apply the update.")
        
    except ValueError:
        print("❌ Invalid input - please enter numbers for scores")
    except KeyboardInterrupt:
        print("\n👋 Cancelled")

def main():
    print("🏈 MANUAL SCORE UPDATE TOOL")
    print()
    print("1. Apply known results")
    print("2. Add new result")
    print()
    
    try:
        choice = input("Choice (1 or 2): ").strip()
        
        if choice == "1":
            manual_score_update()
        elif choice == "2":
            add_new_result()
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == '__main__':
    main()
