#!/usr/bin/env python3
"""
Test script to verify that deadline formatting works correctly.
This tests the fix for the strftime '%-I' issue on Windows.
"""

from datetime import datetime

def test_deadline_formatting():
    """Test that strftime formatting works correctly without %-I"""
    
    # Create a test datetime
    test_time = datetime(2025, 9, 7, 14, 30, 0)  # 2:30 PM
    
    print("Testing deadline formatting...")
    
    # Test the old problematic format (should fail on Windows)
    try:
        problematic_format = test_time.strftime('%A %-I:%M %p AST')
        print(f"❌ PROBLEM: %-I format worked (shouldn't on Windows): {problematic_format}")
    except ValueError as e:
        print(f"✅ EXPECTED: %-I format failed on Windows: {e}")
    
    # Test the fixed format (should work on all platforms)
    try:
        fixed_format = test_time.strftime('%A %I:%M %p AST')
        print(f"✅ SUCCESS: %I format works: {fixed_format}")
    except ValueError as e:
        print(f"❌ UNEXPECTED: %I format failed: {e}")
    
    # Test with different times to show leading zero behavior
    times = [
        datetime(2025, 9, 7, 9, 30, 0),   # 9:30 AM
        datetime(2025, 9, 7, 14, 30, 0),  # 2:30 PM  
        datetime(2025, 9, 7, 21, 15, 0),  # 9:15 PM
    ]
    
    print("\nFormatted examples:")
    for time in times:
        formatted = time.strftime('%A %I:%M %p AST')
        print(f"  {formatted}")

if __name__ == "__main__":
    test_deadline_formatting()
