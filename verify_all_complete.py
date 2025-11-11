#!/usr/bin/env python3
"""
Verify all users now have complete Week 9 picks
"""

import sqlite3

def verify_all_users_complete():
    """Verify all users have complete Week 9 picks"""
    print("=" * 70)
    print("VERIFYING ALL USERS HAVE COMPLETE WEEK 9 PICKS")
    print("=" * 70)
    
    conn = sqlite3.connect('nfl_fantasy.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check all non-admin users
    cursor.execute("SELECT id, username FROM users WHERE NOT is_admin ORDER BY username")
    all_users = cursor.fetchall()
    
    print(f"\nChecking {len(all_users)} users:")
    print("-" * 50)
    
    complete_users = 0
    incomplete_users = 0
    
    for user in all_users:
        cursor.execute("""
            SELECT COUNT(*) as pick_count
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = 9 AND g.year = 2025
        """, (user['id'],))
        
        pick_count = cursor.fetchone()['pick_count']
        
        if pick_count == 14:
            status = "✅ Complete"
            complete_users += 1
        else:
            status = f"❌ INCOMPLETE ({pick_count}/14)"
            incomplete_users += 1
        
        print(f"  {user['username']:12} ({user['id']:2}): {pick_count:2}/14 picks - {status}")
    
    print(f"\n" + "=" * 50)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"✅ Complete users: {complete_users}")
    print(f"❌ Incomplete users: {incomplete_users}")
    print(f"📊 Total users: {len(all_users)}")
    
    if incomplete_users == 0:
        print(f"\n🎉 SUCCESS! All {complete_users} users have complete Week 9 picks!")
        print("🎯 Admin interface will now work perfectly for all users!")
        print("📋 Every user can be selected in 'Set User Picks' with all 14 games showing")
    else:
        print(f"\n⚠️  WARNING: {incomplete_users} users still missing picks")
    
    # Show sample picks for a few users to confirm data quality
    print(f"\n" + "=" * 50)
    print("SAMPLE PICKS VERIFICATION")
    print("=" * 50)
    
    sample_users = ['jean', 'kristian', 'vizca']
    for username in sample_users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_result = cursor.fetchone()
        if not user_result:
            continue
            
        user_id = user_result['id']
        
        cursor.execute("""
            SELECT 
                g.away_team,
                g.home_team,
                up.selected_team
            FROM user_picks up
            JOIN nfl_games g ON up.game_id = g.id
            WHERE up.user_id = ? AND g.week = 9 AND g.year = 2025
            ORDER BY g.game_date
            LIMIT 3
        """, (user_id,))
        
        picks = cursor.fetchall()
        print(f"\n{username.upper()}'s first 3 picks:")
        for pick in picks:
            print(f"  {pick['away_team']} @ {pick['home_team']} -> {pick['selected_team']}")
    
    conn.close()

if __name__ == "__main__":
    verify_all_users_complete()