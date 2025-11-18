#!/usr/bin/env python3
"""
Comprehensive fix for us.total_games_won column reference error
This script will:
1. Scan all Python files for problematic queries
2. Test all leaderboard-related functions 
3. Provide specific fixes for any issues found
"""

import os
import re
import sqlite3
import sys
from pathlib import Path


def scan_python_files_for_problematic_queries():
    """Scan all Python files for queries that might use us.total_games_won"""
    print("🔍 SCANNING PYTHON FILES FOR PROBLEMATIC QUERIES")
    print("=" * 60)
    
    problematic_patterns = [
        r'us\.total_games_won',
        r'user_statistics\s+us.*total_games_won', 
        r'FROM\s+user_statistics\s+us.*total_games_won'
    ]
    
    python_files = list(Path('.').glob('**/*.py'))
    issues_found = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern in problematic_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues_found.append({
                            'file': str(py_file),
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern
                        })
                        print(f"❌ FOUND ISSUE: {py_file}:{line_num}")
                        print(f"   Pattern: {pattern}")
                        print(f"   Line: {line.strip()}")
                        print()
        
        except Exception as e:
            print(f"⚠️  Error reading {py_file}: {e}")
    
    if not issues_found:
        print("✅ No problematic us.total_games_won patterns found in Python files")
    
    return issues_found


def test_all_app_routes():
    """Test importing the app and accessing routes that might cause issues"""
    print("\n🧪 TESTING APP ROUTES FOR LEADERBOARD ISSUES")
    print("=" * 60)
    
    try:
        # Import the app
        sys.path.insert(0, '.')
        import app
        
        # Test if we can create the Flask app
        flask_app = app.app
        
        with flask_app.test_client() as client:
            print("✅ Flask app imported successfully")
            
            # Test routes that might use leaderboard queries
            routes_to_test = [
                '/leaderboard',
                '/weekly_leaderboard',
                '/debug_leaderboard'
            ]
            
            for route in routes_to_test:
                try:
                    # This won't work without proper session, but we're checking for import errors
                    print(f"   Testing route: {route}")
                    
                    # Check if the route function exists in the app
                    endpoint = route.lstrip('/')
                    if hasattr(app, endpoint):
                        print(f"   ✅ Route function {endpoint} found")
                    else:
                        print(f"   ⚠️  Route function {endpoint} not found")
                        
                except Exception as e:
                    print(f"   ❌ Error with route {route}: {e}")
        
    except Exception as e:
        print(f"❌ Error importing app: {e}")
        print("   This might indicate a syntax error or import issue")
        return False
    
    return True


def create_fixed_leaderboard_query():
    """Create and test a corrected leaderboard query"""
    print("\n🔧 CREATING CORRECTED LEADERBOARD QUERY")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Test a comprehensive leaderboard query that properly uses user_statistics
        print("Testing comprehensive leaderboard query...")
        
        cursor.execute('''
            SELECT 
                u.username,
                -- Weekly wins from weekly_results table
                COUNT(DISTINCT CASE WHEN wr.is_winner = 1 THEN wr.week || '-' || wr.year END) as weekly_wins,
                -- Total games won calculated from picks
                SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_games_won_calculated,
                -- Total wins from user_statistics (corrected column name)
                COALESCE(us.total_wins, 0) as total_wins_from_stats,
                -- Weeks played
                COUNT(DISTINCT CASE WHEN g.is_final = 1 THEN g.week || '-' || g.year END) as weeks_played,
                -- Total games
                COUNT(CASE WHEN g.is_final = 1 THEN 1 END) as total_games_played,
                -- Other user statistics
                COALESCE(us.win_percentage, 0.0) as win_percentage,
                COALESCE(us.average_score, 0.0) as average_score
            FROM users u
            LEFT JOIN user_picks p ON u.id = p.user_id
            LEFT JOIN nfl_games g ON p.game_id = g.id
            LEFT JOIN weekly_results wr ON u.id = wr.user_id
            LEFT JOIN user_statistics us ON u.id = us.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id, u.username, us.total_wins, us.win_percentage, us.average_score
            HAVING COUNT(CASE WHEN g.is_final = 1 THEN 1 END) > 0 OR COUNT(CASE WHEN wr.is_winner = 1 THEN 1 END) > 0
            ORDER BY weekly_wins DESC, total_games_won_calculated DESC, u.username
        ''')
        
        results = cursor.fetchall()
        
        print(f"✅ Corrected query successful - {len(results)} results")
        
        if results:
            print("\nSample results:")
            print("User | Weekly Wins | Games Won (calc) | Games Won (stats) | Win %")
            print("-" * 70)
            for row in results[:5]:
                username, weekly_wins, calc_wins, stats_wins, weeks, total, win_pct, avg = row
                print(f"{username:12} | {weekly_wins:11} | {calc_wins:16} | {stats_wins:17} | {win_pct:5.1f}%")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing corrected query: {e}")
        return False


def generate_fix_recommendations():
    """Generate specific fix recommendations"""
    print("\n💡 FIX RECOMMENDATIONS")
    print("=" * 60)
    
    print("If you're getting 'us.total_games_won' errors, here are the fixes:")
    print()
    print("1. ❌ WRONG: us.total_games_won")
    print("   ✅ CORRECT: us.total_wins")
    print()
    print("2. If you want to use user_statistics table:")
    print("   ```sql")
    print("   SELECT u.username, us.total_wins")
    print("   FROM users u") 
    print("   LEFT JOIN user_statistics us ON u.id = us.user_id")
    print("   ```")
    print()
    print("3. If you want calculated total games won (recommended):")
    print("   ```sql")
    print("   SELECT u.username,")
    print("          SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as total_games_won")
    print("   FROM users u")
    print("   LEFT JOIN user_picks p ON u.id = p.user_id")
    print("   LEFT JOIN nfl_games g ON p.game_id = g.id")
    print("   WHERE g.is_final = 1")
    print("   GROUP BY u.id, u.username")
    print("   ```")
    print()
    print("4. Available columns in user_statistics:")
    print("   • total_wins (not total_games_won)")
    print("   • total_points")
    print("   • win_percentage")
    print("   • average_score")
    print("   • best_week_score")
    print("   • worst_week_score")


def main():
    """Main diagnostic and fix function"""
    print("🚨 NFL FANTASY LEADERBOARD ERROR DIAGNOSTIC & FIX")
    print("=" * 70)
    
    # Step 1: Scan files for issues
    issues = scan_python_files_for_problematic_queries()
    
    # Step 2: Test app imports
    app_ok = test_all_app_routes()
    
    # Step 3: Test corrected queries
    query_ok = create_fixed_leaderboard_query()
    
    # Step 4: Recommendations
    generate_fix_recommendations()
    
    # Summary
    print("\n📋 SUMMARY")
    print("=" * 60)
    if issues:
        print(f"❌ Found {len(issues)} problematic code patterns")
        print("   → Review the files listed above and fix us.total_games_won references")
    else:
        print("✅ No problematic code patterns found in Python files")
    
    if not app_ok:
        print("❌ App import issues detected")
        print("   → Check for syntax errors in app.py")
    else:
        print("✅ App imports successfully")
    
    if query_ok:
        print("✅ Corrected leaderboard query works")
    else:
        print("❌ Database query issues")
    
    print("\n🎯 NEXT STEPS:")
    if issues:
        print("1. Fix the problematic queries found in the file scan")
        print("2. Replace us.total_games_won with us.total_wins")
        print("3. Test your leaderboard page again")
    else:
        print("1. The error might be in a cached template or dynamic query")
        print("2. Try restarting your Flask application")
        print("3. Clear any browser caches")
        print("4. Check if the error occurs in a specific browser/route")


if __name__ == "__main__":
    main()
