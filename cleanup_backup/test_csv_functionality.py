#!/usr/bin/env python3
"""
Test script for CSV import/export functionality
Creates sample data and tests the CSV workflow
"""
from __future__ import annotations

import csv
import io
import sys
import os
from datetime import datetime

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_csv():
    """Create a sample CSV file for testing"""
    sample_data = [
        ['username', 'game_id', 'away_team', 'home_team', 'selected_team', 'predicted_home_score', 'predicted_away_score'],
        ['john_doe', '1', 'Bills', 'Chiefs', 'Chiefs', '', ''],
        ['john_doe', '2', 'Cowboys', 'Giants', 'Cowboys', '', ''],
        ['john_doe', '3', 'Packers', 'Bears', '', '', ''],  # No pick
        ['jane_smith', '1', 'Bills', 'Chiefs', 'Bills', '', ''],
        ['jane_smith', '2', 'Cowboys', 'Giants', 'Giants', '', ''],
        ['jane_smith', '3', 'Packers', 'Bears', 'Packers', '24', '17'],  # MNF with prediction
        ['bob_wilson', '1', 'Bills', 'Chiefs', 'Chiefs', '', ''],
        ['bob_wilson', '2', 'Cowboys', 'Giants', '', '', ''],  # No pick
        ['bob_wilson', '3', 'Packers', 'Bears', 'Bears', '21', '14'],
    ]
    
    filename = 'sample_picks_test.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sample_data)
    
    print(f"✅ Created sample CSV: {filename}")
    return filename

def validate_csv_format(filename):
    """Validate the CSV format"""
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_columns = ['username', 'game_id', 'away_team', 'home_team', 'selected_team']
            
            # Check headers
            if not all(col in reader.fieldnames for col in required_columns):
                print("❌ Missing required columns")
                print(f"Expected: {required_columns}")
                print(f"Found: {reader.fieldnames}")
                return False
            
            # Check data
            row_count = 0
            picks_count = 0
            users = set()
            
            for row in reader:
                row_count += 1
                users.add(row['username'])
                
                if row['selected_team'].strip():
                    picks_count += 1
                
                # Validate game_id is numeric
                if not row['game_id'].isdigit():
                    print(f"❌ Row {row_count}: Invalid game_id '{row['game_id']}'")
                    return False
            
            print(f"✅ CSV validation passed:")
            print(f"   - Total rows: {row_count}")
            print(f"   - Users: {len(users)} ({', '.join(sorted(users))})")
            print(f"   - Picks with selections: {picks_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error validating CSV: {e}")
        return False

def test_csv_workflow():
    """Test the complete CSV workflow"""
    print("Testing CSV Import/Export Workflow")
    print("=" * 50)
    
    # Step 1: Create sample CSV
    sample_file = create_sample_csv()
    
    # Step 2: Validate format
    if not validate_csv_format(sample_file):
        print("❌ CSV validation failed")
        return False
    
    # Step 3: Display sample content
    print(f"\n📄 Sample CSV content:")
    print("-" * 30)
    
    with open(sample_file, 'r', encoding='utf-8') as csvfile:
        content = csvfile.read()
        print(content)
    
    # Step 4: Test reading and processing
    print("🔄 Processing CSV data:")
    print("-" * 30)
    
    with open(sample_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        user_stats = {}
        
        for row in reader:
            username = row['username']
            selected_team = row['selected_team'].strip()
            
            if username not in user_stats:
                user_stats[username] = {'total_games': 0, 'picks_made': 0}
            
            user_stats[username]['total_games'] += 1
            
            if selected_team:
                user_stats[username]['picks_made'] += 1
        
        for username, stats in user_stats.items():
            completion = (stats['picks_made'] / stats['total_games']) * 100
            print(f"   {username}: {stats['picks_made']}/{stats['total_games']} picks ({completion:.1f}% complete)")
    
    # Step 5: Cleanup
    try:
        os.remove(sample_file)
        print(f"\n🧹 Cleaned up: {sample_file}")
    except:
        pass
    
    print("\n✅ CSV workflow test completed successfully!")
    print("\n📋 Usage Instructions:")
    print("1. Go to Admin Panel")
    print("2. Select Week and Year")
    print("3. Click 'Export Picks CSV' to download template")
    print("4. Fill in picks for offline users")
    print("5. Click 'Import Picks CSV' to upload completed file")
    print("6. Validate before importing")
    print("7. Import with appropriate options")
    
    return True

if __name__ == "__main__":
    try:
        test_csv_workflow()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
