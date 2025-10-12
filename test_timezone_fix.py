#!/usr/bin/env python3
"""
Test the fixed timezone conversion
"""

from datetime import datetime
import sys
import os

# Add the current directory to Python path so we can import utils
sys.path.append('.')

from utils.timezone_utils import convert_to_ast, format_ast_time

# Test with the problematic game times from the database
test_times = [
    ("DEN @ NYJ (London game)", "2025-10-12 09:30:00"),
    ("Regular Sunday games", "2025-10-12 13:00:00"),
    ("Sunday late games", "2025-10-12 16:05:00"),
    ("Sunday night game", "2025-10-12 20:20:00"),
    ("Monday night game", "2025-10-13 19:15:00"),
]

print("Testing Fixed Timezone Conversion:")
print("=" * 45)
print("Database Time (ET) -> AST Display")
print()

for description, db_time_str in test_times:
    # Parse the database time (naive datetime)
    db_time = datetime.strptime(db_time_str, "%Y-%m-%d %H:%M:%S")
    
    # Convert using the fixed function
    ast_time = convert_to_ast(db_time)
    formatted_time = ast_time.strftime("%a %m/%d %I:%M %p AST")
    
    print(f"{description}:")
    print(f"  Database: {db_time_str}")
    print(f"  AST:      {formatted_time}")
    print()

print("Expected Results:")
print("- DEN @ NYJ should show: Sun 10/12 09:30 AM AST (London game)")
print("- Regular games should show: Sun 10/12 01:00 PM AST")
print("- Late games should show: Sun 10/12 04:05 PM AST")
print("- Sunday night: Sun 10/12 08:20 PM AST")
print("- Monday night: Mon 10/13 07:15 PM AST")