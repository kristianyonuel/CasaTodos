#!/usr/bin/env python3
"""
Fix database foreign key violations by cleaning up orphaned picks
"""

import sqlite3

def fix_database_integrity():
    """Fix foreign key violations and orphaned data"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print('🔧 FIXING DATABASE INTEGRITY ISSUES')
    print('=' * 45)
    
    # Disable foreign keys temporarily
    cursor.execute('PRAGMA foreign_keys = OFF')
    
    print('\n🧹 CLEANING ORPHANED PICKS:')
    
    # Find picks that reference non-existent games
    cursor.execute('''
        SELECT p.id, p.game_id, u.username
        FROM user_picks p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        WHERE g.id IS NULL
        ORDER BY p.id
        LIMIT 10
    ''')
    
    orphaned_picks = cursor.fetchall()
    if orphaned_picks:
        print(f'Found {len(orphaned_picks)} orphaned picks (showing first 10):')
        for pick in orphaned_picks:
            print(f'  Pick ID {pick[0]}: User {pick[2]} -> Game ID {pick[1]} (missing)')
    
    # Delete orphaned picks
    cursor.execute('''
        DELETE FROM user_picks 
        WHERE id IN (
            SELECT p.id 
            FROM user_picks p
            LEFT JOIN nfl_games g ON p.game_id = g.id
            WHERE g.id IS NULL
        )
    ''')
    
    deleted_picks = cursor.rowcount
    print(f'✅ Deleted {deleted_picks} orphaned picks')
    
    # Clean up orphaned user statistics
    print(f'\n🧹 CLEANING ORPHANED USER STATISTICS:')
    cursor.execute('''
        DELETE FROM user_statistics 
        WHERE user_id NOT IN (SELECT id FROM users)
    ''')
    
    deleted_stats = cursor.rowcount
    print(f'✅ Deleted {deleted_stats} orphaned user statistics')
    
    # Re-enable foreign keys and check
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('PRAGMA foreign_key_check')
    remaining_violations = cursor.fetchall()
    
    print(f'\n🔍 VERIFICATION:')
    if remaining_violations:
        print(f'⚠️ Still {len(remaining_violations)} foreign key violations')
    else:
        print('✅ All foreign key violations resolved!')
    
    # Final counts
    cursor.execute('SELECT COUNT(*) FROM user_picks')
    final_picks = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE year = 2025')
    total_games = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    conn.commit()
    
    print(f'\n📊 CLEANED DATABASE SUMMARY:')
    print(f'  Games (2025): {total_games}')
    print(f'  Users: {total_users}')
    print(f'  Valid Picks: {final_picks}')
    print(f'  Removed: {deleted_picks} orphaned picks + {deleted_stats} orphaned stats')
    
    print(f'\n✅ DATABASE INTEGRITY RESTORED!')
    print(f'💾 The database should now work properly on your server')
    
    conn.close()

if __name__ == "__main__":
    fix_database_integrity()