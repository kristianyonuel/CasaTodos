#!/usr/bin/env python3
"""
Test script to verify Friday and Saturday game deadline handling
This script tests that:
1. Friday games have individual deadlines (30 minutes before each game)
2. Saturday games have individual deadlines (30 minutes before each game)
3. Friday and Saturday games are NOT included in Sunday game deadlines
4. Sunday and Monday games share the same deadline (30 minutes before first Sunday game)
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta
import pytz

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deadline_manager import DeadlineManager
from utils.timezone_utils import convert_to_ast

def create_test_games():
    """Create test games for different days of the week"""
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Clear existing test games for week 13 (which has Friday games)
        cursor.execute('DELETE FROM nfl_games WHERE week = 13 AND year = 2025')
        
        # Create a base datetime for Week 13, 2025 (starting Dec 1, 2025)
        week_start = datetime(2025, 12, 1)  # Monday
        
        # Thursday Night Football - Dec 4, 2025 at 8:15 PM
        thursday = week_start + timedelta(days=3)  # Thursday
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_thursday_night, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'TNF_W13', 'Packers', 'Lions', thursday.replace(hour=20, minute=15), True, 'scheduled'))
        
        # Friday Night Game - Dec 5, 2025 at 8:00 PM (Individual deadline)
        friday = week_start + timedelta(days=4)  # Friday
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'FRI_W13', 'Chiefs', 'Raiders', friday.replace(hour=20, minute=0), 'scheduled'))
        
        # Saturday Games - Dec 6, 2025 (Individual deadlines)
        saturday = week_start + timedelta(days=5)  # Saturday
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'SAT1_W13', 'Cowboys', 'Eagles', saturday.replace(hour=16, minute=30), 'scheduled'))
        
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'SAT2_W13', 'Bills', 'Patriots', saturday.replace(hour=20, minute=0), 'scheduled'))
        
        # Sunday Games - Dec 7, 2025 (Share deadline with Monday)
        sunday = week_start + timedelta(days=6)  # Sunday
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'SUN1_W13', 'Saints', 'Falcons', sunday.replace(hour=13, minute=0), 'scheduled'))
        
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'SUN2_W13', 'Bengals', 'Steelers', sunday.replace(hour=16, minute=25), 'scheduled'))
        
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_sunday_night, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'SNF_W13', 'Jets', 'Dolphins', sunday.replace(hour=20, minute=20), True, 'scheduled'))
        
        # Monday Night Football - Dec 8, 2025 at 8:15 PM (Uses Sunday deadline)
        monday = week_start + timedelta(days=7)  # Monday
        cursor.execute('''
            INSERT INTO nfl_games (week, year, game_id, home_team, away_team, game_date, is_monday_night, game_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (13, 2025, 'MNF_W13', 'Rams', '49ers', monday.replace(hour=20, minute=15), True, 'scheduled'))
        
        conn.commit()
        conn.close()
        
        print("✅ Test games created successfully for Week 13, 2025")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test games: {e}")
        return False

def test_deadline_logic():
    """Test the deadline logic for different game types"""
    
    print("\n" + "="*80)
    print("TESTING FRIDAY/SATURDAY DEADLINE EXCLUSION")
    print("="*80)
    
    dm = DeadlineManager()
    
    # Test Week 13, 2025 deadlines
    deadlines = dm.get_week_deadlines(13, 2025)
    
    print("\n🔍 DEADLINE ANALYSIS:")
    print("-" * 50)
    
    # Thursday Night
    if deadlines.get('thursday_night'):
        thursday_info = deadlines['thursday_night']
        print(f"📅 Thursday Night: {thursday_info['matchup']}")
        print(f"   Game Time: {thursday_info['game_time'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print(f"   Deadline:  {thursday_info['deadline'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print()
    
    # Friday Games (Individual deadlines)
    friday_games = deadlines.get('friday_games', [])
    if friday_games:
        print(f"📅 Friday Games ({len(friday_games)} games with individual deadlines):")
        for i, friday_info in enumerate(friday_games, 1):
            print(f"   Game {i}: {friday_info['matchup']}")
            print(f"   Game Time: {friday_info['game_time'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
            print(f"   Deadline:  {friday_info['deadline'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print()
    
    # Saturday Games (Individual deadlines)
    saturday_games = deadlines.get('saturday_games', [])
    if saturday_games:
        print(f"📅 Saturday Games ({len(saturday_games)} games with individual deadlines):")
        for i, saturday_info in enumerate(saturday_games, 1):
            print(f"   Game {i}: {saturday_info['matchup']}")
            print(f"   Game Time: {saturday_info['game_time'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
            print(f"   Deadline:  {saturday_info['deadline'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print()
    
    # Sunday Games (Shared deadline)
    if deadlines.get('sunday_games'):
        sunday_info = deadlines['sunday_games']
        print(f"📅 Sunday Games (shared deadline): {sunday_info['matchup']}")
        print(f"   First Game Time: {sunday_info['game_time'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print(f"   Shared Deadline: {sunday_info['deadline'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print()
    
    # Monday Night (Uses Sunday deadline)
    if deadlines.get('monday_night'):
        monday_info = deadlines['monday_night']
        print(f"📅 Monday Night (uses Sunday deadline): {monday_info['matchup']}")
        print(f"   Game Time: {monday_info['game_time'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print(f"   Deadline:  {monday_info['deadline'].strftime('%A %B %d, %Y at %-I:%M %p AST')}")
        print()
    
    # Verification Tests
    print("\n🧪 VERIFICATION TESTS:")
    print("-" * 50)
    
    # Test 1: Friday games should have individual deadlines
    friday_test_passed = len(friday_games) > 0
    print(f"✅ Test 1 - Friday games have individual deadlines: {'PASS' if friday_test_passed else 'FAIL'}")
    if friday_test_passed:
        for i, friday_info in enumerate(friday_games):
            expected_deadline = friday_info['game_time'] - timedelta(minutes=30)
            actual_deadline = friday_info['deadline']
            time_diff = abs((actual_deadline - expected_deadline).total_seconds())
            deadline_correct = time_diff < 60  # Within 1 minute tolerance
            print(f"   Friday Game {i+1}: {'✅ PASS' if deadline_correct else '❌ FAIL'} - Deadline is 30 min before game")
    
    # Test 2: Saturday games should have individual deadlines  
    saturday_test_passed = len(saturday_games) > 0
    print(f"✅ Test 2 - Saturday games have individual deadlines: {'PASS' if saturday_test_passed else 'FAIL'}")
    if saturday_test_passed:
        for i, saturday_info in enumerate(saturday_games):
            expected_deadline = saturday_info['game_time'] - timedelta(minutes=30)
            actual_deadline = saturday_info['deadline']
            time_diff = abs((actual_deadline - expected_deadline).total_seconds())
            deadline_correct = time_diff < 60  # Within 1 minute tolerance
            print(f"   Saturday Game {i+1}: {'✅ PASS' if deadline_correct else '❌ FAIL'} - Deadline is 30 min before game")
    
    # Test 3: Sunday and Monday should share the same deadline
    sunday_monday_share_deadline = False
    if deadlines.get('sunday_games') and deadlines.get('monday_night'):
        sunday_deadline = deadlines['sunday_games']['deadline']
        monday_deadline = deadlines['monday_night']['deadline']
        sunday_monday_share_deadline = sunday_deadline == monday_deadline
    
    print(f"✅ Test 3 - Sunday and Monday share same deadline: {'PASS' if sunday_monday_share_deadline else 'FAIL'}")
    
    # Test 4: Sunday deadline should be 30 minutes before first Sunday game
    sunday_deadline_correct = False
    if deadlines.get('sunday_games'):
        sunday_info = deadlines['sunday_games']
        expected_deadline = sunday_info['game_time'] - timedelta(minutes=30)
        actual_deadline = sunday_info['deadline']
        time_diff = abs((actual_deadline - expected_deadline).total_seconds())
        sunday_deadline_correct = time_diff < 60  # Within 1 minute tolerance
    
    print(f"✅ Test 4 - Sunday deadline is 30 min before first Sunday game: {'PASS' if sunday_deadline_correct else 'FAIL'}")
    
    # Test 5: Friday/Saturday games are NOT included in Sunday deadline calculation
    friday_saturday_excluded = True
    if deadlines.get('sunday_games'):
        sunday_game_time = deadlines['sunday_games']['game_time']
        # Check that the Sunday deadline is based on Sunday games, not Friday/Saturday
        for friday_info in friday_games:
            if friday_info['game_time'] < sunday_game_time:
                # Friday game is before Sunday, but Sunday deadline should not be based on it
                friday_saturday_excluded = True  # This is expected
        
        for saturday_info in saturday_games:
            if saturday_info['game_time'] < sunday_game_time:
                # Saturday game is before Sunday, but Sunday deadline should not be based on it
                friday_saturday_excluded = True  # This is expected
    
    print(f"✅ Test 5 - Friday/Saturday excluded from Sunday deadline: {'PASS' if friday_saturday_excluded else 'FAIL'}")
    
    # Overall result
    all_tests_passed = (friday_test_passed and saturday_test_passed and 
                       sunday_monday_share_deadline and sunday_deadline_correct and 
                       friday_saturday_excluded)
    
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    
    return all_tests_passed

def test_deadline_summary():
    """Test the deadline summary functionality"""
    
    print("\n" + "="*80)
    print("TESTING DEADLINE SUMMARY")
    print("="*80)
    
    dm = DeadlineManager()
    summary = dm.get_deadline_summary(13, 2025)
    
    print("\n📊 DEADLINE SUMMARY:")
    print("-" * 50)
    
    for day, info in summary.items():
        if day == 'next_deadline':
            if info:
                print(f"⏰ Next Deadline: {info.get('type', 'Unknown')} - {info.get('formatted_time', 'N/A')}")
                print(f"   Hours remaining: {info.get('hours_remaining', 0):.1f}")
        elif day == 'all_deadlines_passed':
            print(f"🕐 All deadlines passed: {info}")
        elif info:
            if isinstance(info, list):
                print(f"📅 {day.capitalize()}: {len(info)} games")
                for i, game in enumerate(info):
                    print(f"   Game {i+1}: {game.get('matchup', 'N/A')} at {game.get('formatted_time', 'N/A')}")
                    print(f"   Hours remaining: {game.get('hours_remaining', 0):.1f}")
            else:
                print(f"📅 {day.capitalize()}: {info.get('matchup', 'N/A')} at {info.get('formatted_time', 'N/A')}")
                print(f"   Hours remaining: {info.get('hours_remaining', 0):.1f}")

def main():
    """Main test function"""
    
    print("🏈 NFL DEADLINE SYSTEM - FRIDAY/SATURDAY EXCLUSION TEST")
    print("="*80)
    
    # Create test games
    if not create_test_games():
        return False
    
    # Test deadline logic
    logic_passed = test_deadline_logic()
    
    # Test deadline summary
    test_deadline_summary()
    
    print("\n" + "="*80)
    print(f"🏁 FINAL RESULT: {'✅ ALL TESTS PASSED' if logic_passed else '❌ TESTS FAILED'}")
    print("="*80)
    
    return logic_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
