#!/usr/bin/env python3
"""
Test script to verify the timezone deadline fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deadline_manager import DeadlineManager
from datetime import datetime

def test_deadline_fix():
    """Test the deadline calculation fix for September 5, 2025 KC @ LAC game"""
    
    print("🔧 TESTING DEADLINE TIMEZONE FIX")
    print("="*50)
    
    try:
        deadline_manager = DeadlineManager()
        
        # Test Week 1, 2025 (which should include Sept 5 game)
        week = 1
        year = 2025
        
        print(f"Getting deadlines for Week {week}, {year}...")
        deadlines = deadline_manager.get_week_deadlines(week, year)
        
        print(f"\nFound deadline categories: {list(deadlines.keys())}")
        
        # Check each deadline type
        for deadline_type, deadline_info in deadlines.items():
            if deadline_info:
                print(f"\n📅 {deadline_type.upper()}:")
                if isinstance(deadline_info, list):
                    # Friday/Saturday games return lists
                    for i, game_info in enumerate(deadline_info):
                        if isinstance(game_info, dict) and 'deadline' in game_info:
                            print(f"  Game {i+1}:")
                            print(f"    Matchup: {game_info.get('matchup', 'Unknown')}")
                            print(f"    Game Time: {game_info['game_time']}")
                            print(f"    Deadline: {game_info['deadline']}")
                            
                            # Check if this looks like the KC @ LAC game
                            matchup = game_info.get('matchup', '')
                            if 'KC' in matchup and 'LAC' in matchup:
                                print(f"    ⭐ THIS IS THE KC @ LAC GAME!")
                                
                                game_hour = game_info['game_time'].hour
                                deadline_hour = game_info['deadline'].hour
                                deadline_minute = game_info['deadline'].minute
                                
                                print(f"    📊 Analysis:")
                                print(f"       Game time hour: {game_hour} (should be 20 = 8 PM)")
                                print(f"       Deadline time: {deadline_hour}:{deadline_minute:02d} (should be 19:30 = 7:30 PM)")
                                
                                if game_hour == 20 and deadline_hour == 19 and deadline_minute == 30:
                                    print(f"    ✅ DEADLINE IS CORRECT!")
                                else:
                                    print(f"    ❌ DEADLINE IS STILL INCORRECT")
                                    
                elif isinstance(deadline_info, dict) and 'deadline' in deadline_info:
                    print(f"    Matchup: {deadline_info.get('matchup', 'Unknown')}")
                    print(f"    Game Time: {deadline_info['game_time']}")
                    print(f"    Deadline: {deadline_info['deadline']}")
        
        # Check what day September 5, 2025 is
        sep_5 = datetime(2025, 9, 5)
        print(f"\n📅 September 5, 2025 is a {sep_5.strftime('%A')} (weekday {sep_5.weekday()})")
        print(f"   This should be categorized as: {'Friday games' if sep_5.weekday() == 4 else 'Other'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing deadline fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏈 LA CASA DE TODOS - DEADLINE TIMEZONE FIX TEST")
    print("="*60)
    
    success = test_deadline_fix()
    
    if success:
        print(f"\n🎉 DEADLINE TEST COMPLETED!")
        print(f"📋 Check the output above to verify the KC @ LAC deadline is now 7:30 PM AST")
    else:
        print(f"\n❌ TEST FAILED - Check error messages above")
    
    print(f"\n" + "="*60)
