#!/usr/bin/env python3
"""
Debug script to check the timezone and deadline calculation issue
"""

from datetime import datetime, timedelta
import pytz

def debug_timezone_issue():
    """Debug the timezone conversion issue"""
    
    print("🔍 DEBUGGING TIMEZONE ISSUE")
    print("="*50)
    
    # Check what day September 5, 2025 is
    sep_5_2025 = datetime(2025, 9, 5)
    print(f"September 5, 2025 is a {sep_5_2025.strftime('%A')} (weekday {sep_5_2025.weekday()})")
    print("(Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6)")
    
    # Test the game time from database
    game_time_str = "2025-09-05 20:00:00"
    game_time = datetime.strptime(game_time_str, '%Y-%m-%d %H:%M:%S')
    
    print(f"\nGame time from database: {game_time_str}")
    print(f"Parsed datetime (naive): {game_time}")
    
    # AST timezone
    ast_tz = pytz.timezone('America/Puerto_Rico')
    
    # Test different timezone interpretations
    print(f"\n🔍 TESTING DIFFERENT TIMEZONE INTERPRETATIONS:")
    
    # Option 1: Treat as UTC, convert to AST
    game_time_utc = game_time.replace(tzinfo=pytz.UTC)
    game_time_ast_from_utc = game_time_utc.astimezone(ast_tz)
    print(f"1. Treating as UTC → AST: {game_time_ast_from_utc}")
    deadline_from_utc = game_time_ast_from_utc - timedelta(minutes=30)
    print(f"   Deadline (30 min before): {deadline_from_utc}")
    
    # Option 2: Treat as AST directly
    game_time_ast_direct = game_time.replace(tzinfo=ast_tz)
    print(f"2. Treating as AST directly: {game_time_ast_direct}")
    deadline_direct = game_time_ast_direct - timedelta(minutes=30)
    print(f"   Deadline (30 min before): {deadline_direct}")
    
    # Option 3: Check if it's EST/EDT and convert
    est_tz = pytz.timezone('US/Eastern')
    game_time_est = game_time.replace(tzinfo=est_tz)
    game_time_ast_from_est = game_time_est.astimezone(ast_tz)
    print(f"3. Treating as EST → AST: {game_time_ast_from_est}")
    deadline_from_est = game_time_ast_from_est - timedelta(minutes=30)
    print(f"   Deadline (30 min before): {deadline_from_est}")
    
    print(f"\n📋 ANALYSIS:")
    print(f"If you see 4:00 PM AST as deadline, it suggests Option 1 (treating as UTC)")
    print(f"If the game should be at 8:00 PM AST, deadline should be 7:30 PM AST (Option 2)")
    print(f"The 3.5 hour difference suggests UTC→AST conversion when data is already in AST")
    
    # Check the actual offset
    print(f"\n🕐 TIMEZONE OFFSET INFO:")
    utc_now = datetime.now(pytz.UTC)
    ast_now = utc_now.astimezone(ast_tz)
    offset = ast_now.utcoffset()
    print(f"AST offset from UTC: {offset}")
    print(f"AST timezone: {ast_tz}")

if __name__ == "__main__":
    debug_timezone_issue()
