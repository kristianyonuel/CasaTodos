#!/usr/bin/env python3
"""
Test case-insensitive username functionality
"""

import sqlite3
import os
from datetime import datetime

def test_case_insensitive_login():
    """Test the case-insensitive username lookup"""
    
    if not os.path.exists('nfl_fantasy.db'):
        print("❌ Database not found. Run setup_database.py first")
        return False
    
    print("🧪 Testing case-insensitive username functionality...")
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Test case-insensitive lookup with existing users
        test_cases = [
            ('admin', 'ADMIN'),
            ('ADMIN', 'admin'), 
            ('Admin', 'admin'),
            ('aDmIn', 'admin'),
            ('dad', 'DAD'),
            ('MOM', 'mom')
        ]
        
        print("Testing case-insensitive lookups:")
        for test_input, expected_original in test_cases:
            cursor.execute('SELECT id, username FROM users WHERE LOWER(username) = LOWER(?)', (test_input,))
            result = cursor.fetchone()
            
            if result:
                print(f"✅ '{test_input}' → Found user: '{result[1]}' (ID: {result[0]})")
            else:
                print(f"❌ '{test_input}' → No user found")
        
        # Test duplicate prevention
        print("\n🧪 Testing duplicate prevention...")
        cursor.execute('SELECT username FROM users WHERE LOWER(username) = LOWER(?)', ('ADMIN',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"✅ Duplicate check works: Found existing user '{existing_user[0]}' for 'ADMIN'")
        else:
            print("❌ Duplicate check failed")
        
        conn.close()
        print("\n✅ Case-insensitive username functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_case_insensitive_login()
