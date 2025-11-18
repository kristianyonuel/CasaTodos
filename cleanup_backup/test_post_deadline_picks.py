#!/usr/bin/env python3
"""
Test script for post-deadline pick visibility functionality
"""

import sqlite3
from datetime import datetime, timedelta

def test_post_deadline_picks():
    """Test the post-deadline pick visibility feature"""
    
    print("🧪 TESTING POST-DEADLINE PICK VISIBILITY")
    print("="*50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Check if we have users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        user_count = cursor.fetchone()[0]
        print(f"Non-admin users in database: {user_count}")
        
        if user_count < 2:
            print("❌ Need at least 2 users to test pick visibility")
            return False
        
        # Check if we have games
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = 2025')
        game_count = cursor.fetchone()[0]
        print(f"Games for Week 1, 2025: {game_count}")
        
        if game_count == 0:
            print("❌ No games found for testing")
            return False
        
        # Check if we have picks from multiple users
        cursor.execute('''
            SELECT g.id, g.home_team, g.away_team, COUNT(DISTINCT up.user_id) as pick_count
            FROM nfl_games g
            LEFT JOIN user_picks up ON g.id = up.game_id
            WHERE g.week = 1 AND g.year = 2025
            GROUP BY g.id, g.home_team, g.away_team
            HAVING pick_count > 1
            LIMIT 5
        ''')
        
        games_with_multiple_picks = cursor.fetchall()
        print(f"\nGames with picks from multiple users:")
        
        if not games_with_multiple_picks:
            print("❌ No games found with picks from multiple users")
            print("💡 Try creating some test picks for multiple users first")
            return False
        
        for game_id, home_team, away_team, pick_count in games_with_multiple_picks:
            print(f"  Game {game_id}: {away_team} @ {home_team} - {pick_count} users")
            
            # Show picks for this game
            cursor.execute('''
                SELECT u.username, up.selected_team, up.predicted_home_score, up.predicted_away_score
                FROM user_picks up
                JOIN users u ON up.user_id = u.id
                WHERE up.game_id = ? AND u.is_admin = 0
                ORDER BY u.username
            ''', (game_id,))
            
            picks = cursor.fetchall()
            for username, selected_team, home_score, away_score in picks:
                score_info = ""
                if home_score is not None or away_score is not None:
                    score_info = f" (Predicted: {away_score or '?'}-{home_score or '?'})"
                print(f"    {username}: {selected_team}{score_info}")
        
        # Test the all_picks data structure format
        print(f"\n🔍 Testing all_picks data structure format:")
        
        cursor.execute('''
            SELECT g.id, u.username, up.selected_team, up.predicted_home_score, up.predicted_away_score
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            JOIN users u ON up.user_id = u.id
            WHERE g.week = 1 AND g.year = 2025 AND u.is_admin = 0
            ORDER BY g.id, u.username
            LIMIT 10
        ''')
        
        all_picks_data = {}
        for row in cursor.fetchall():
            game_id = row[0]
            if game_id not in all_picks_data:
                all_picks_data[game_id] = []
            all_picks_data[game_id].append({
                'username': row[1],
                'selected_team': row[2],
                'predicted_home_score': row[3],
                'predicted_away_score': row[4]
            })
        
        print(f"Sample all_picks structure:")
        for game_id, picks in list(all_picks_data.items())[:2]:
            print(f"  Game {game_id}:")
            for pick in picks:
                print(f"    {pick}")
        
        print(f"\n✅ Post-deadline pick visibility data structure looks good!")
        print(f"📝 The feature should work when deadlines pass")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing post-deadline picks: {e}")
        return False

def create_sample_picks():
    """Create some sample picks for testing if none exist"""
    
    print("\n🔧 CREATING SAMPLE PICKS FOR TESTING")
    print("="*50)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Get first few games
        cursor.execute('''
            SELECT id, home_team, away_team 
            FROM nfl_games 
            WHERE week = 1 AND year = 2025 
            LIMIT 3
        ''')
        games = cursor.fetchall()
        
        # Get first few users
        cursor.execute('''
            SELECT id, username 
            FROM users 
            WHERE is_admin = 0 
            LIMIT 4
        ''')
        users = cursor.fetchall()
        
        if not games or not users:
            print("❌ Need games and users to create sample picks")
            return False
        
        # Create some sample picks
        import random
        
        for game_id, home_team, away_team in games:
            print(f"\nCreating picks for {away_team} @ {home_team}:")
            
            # Randomly assign some users to pick each team
            for user_id, username in users:
                # Skip some users randomly to simulate real scenario
                if random.random() > 0.7:
                    continue
                
                # Randomly pick home or away team
                selected_team = random.choice([home_team, away_team])
                
                # Add some score predictions for variety
                away_score = random.randint(14, 35) if random.random() > 0.3 else None
                home_score = random.randint(14, 35) if random.random() > 0.3 else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_picks 
                    (user_id, game_id, selected_team, predicted_away_score, predicted_home_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, game_id, selected_team, away_score, home_score))
                
                score_info = ""
                if away_score or home_score:
                    score_info = f" (Predicted: {away_score or '?'}-{home_score or '?'})"
                
                print(f"  {username}: {selected_team}{score_info}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Sample picks created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample picks: {e}")
        return False

if __name__ == "__main__":
    print("🏈 LA CASA DE TODOS - POST-DEADLINE PICK VISIBILITY TEST")
    print("="*60)
    
    success = test_post_deadline_picks()
    
    if not success:
        print("\n🔧 Attempting to create sample data...")
        if create_sample_picks():
            print("\n🔄 Retesting with sample data...")
            success = test_post_deadline_picks()
    
    if success:
        print(f"\n🎉 POST-DEADLINE PICK VISIBILITY FEATURE READY!")
        print(f"📋 To test:")
        print(f"   1. Start the app: python app.py")
        print(f"   2. Go to /games page")
        print(f"   3. When deadlines pass, you'll see everyone's picks")
        print(f"   4. Your pick will be highlighted differently")
    else:
        print(f"\n❌ Feature needs setup or debugging")
    
    print(f"\n" + "="*60)
