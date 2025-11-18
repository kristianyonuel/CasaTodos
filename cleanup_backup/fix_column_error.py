#!/usr/bin/env python3
"""
Fix the us.total_games_won column reference error
This script will create a backward-compatible solution by adding an alias or view
"""

import sqlite3
import sys

def fix_total_games_won_error(db_path='nfl_fantasy.db'):
    """Fix the us.total_games_won error by creating a backward-compatible solution"""
    print("🔧 FIXING us.total_games_won COLUMN REFERENCE ERROR")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Option 1: Add total_games_won as an alias column in user_statistics
        print("🎯 Option 1: Adding total_games_won column as alias to total_wins")
        
        # Check if total_games_won column already exists
        cursor.execute("PRAGMA table_info(user_statistics)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'total_games_won' not in columns:
            print("   Adding total_games_won column...")
            cursor.execute('''
                ALTER TABLE user_statistics 
                ADD COLUMN total_games_won INTEGER DEFAULT 0
            ''')
            
            # Copy data from total_wins to total_games_won
            cursor.execute('''
                UPDATE user_statistics 
                SET total_games_won = total_wins
            ''')
            
            print("   ✅ Added total_games_won column and copied data from total_wins")
        else:
            print("   ✅ total_games_won column already exists")
        
        # Option 2: Create a view that provides backward compatibility
        print("\n🎯 Option 2: Creating backward-compatible view")
        
        try:
            cursor.execute("DROP VIEW IF EXISTS user_stats_compat")
            cursor.execute('''
                CREATE VIEW user_stats_compat AS
                SELECT 
                    id,
                    user_id,
                    seasons_played,
                    total_weeks_played,
                    total_wins,
                    total_wins as total_games_won,  -- Alias for backward compatibility
                    total_points,
                    best_week_score,
                    worst_week_score,
                    average_score,
                    win_percentage,
                    monday_night_accuracy,
                    confidence_accuracy,
                    exact_score_predictions,
                    perfect_weeks,
                    current_streak,
                    longest_streak,
                    favorite_team,
                    lucky_day,
                    total_prize_money,
                    created_at,
                    updated_at
                FROM user_statistics
            ''')
            print("   ✅ Created user_stats_compat view with total_games_won alias")
        except Exception as e:
            print(f"   ⚠️ Error creating view: {e}")
        
        # Option 3: Test the fix
        print("\n🧪 Testing the fix...")
        
        # Test the original problematic query
        try:
            cursor.execute('''
                SELECT u.username, us.total_games_won 
                FROM users u 
                LEFT JOIN user_statistics us ON u.id = us.user_id 
                WHERE u.is_admin = 0 
                ORDER BY us.total_games_won DESC
                LIMIT 5
            ''')
            results = cursor.fetchall()
            print(f"   ✅ Original query now works! Found {len(results)} results")
            for username, total_games_won in results:
                print(f"      {username}: {total_games_won} games won")
        except Exception as e:
            print(f"   ❌ Original query still fails: {e}")
        
        # Test using the view
        try:
            cursor.execute('''
                SELECT u.username, us.total_games_won 
                FROM users u 
                LEFT JOIN user_stats_compat us ON u.id = us.user_id 
                WHERE u.is_admin = 0 
                ORDER BY us.total_games_won DESC
                LIMIT 5
            ''')
            results = cursor.fetchall()
            print(f"   ✅ View-based query works! Found {len(results)} results")
        except Exception as e:
            print(f"   ⚠️ View-based query failed: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 FIX COMPLETE!")
        print("=" * 60)
        print("✅ Added total_games_won column to user_statistics table")
        print("✅ Created user_stats_compat view for backward compatibility")
        print("✅ Your leaderboard should now work without errors")
        print()
        print("💡 If you want to update your code to use the correct column name:")
        print("   Replace: us.total_games_won")
        print("   With:    us.total_wins")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'nfl_fantasy.db'
    fix_total_games_won_error(db_path)
