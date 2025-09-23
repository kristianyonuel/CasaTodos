#!/usr/bin/env python3
"""
Fix for premature winner declaration issue on Ubuntu server
This patches the scoring_updater.py to only mark winners when week is complete
"""

def fix_premature_winner_issue():
    """Apply the scoring updater fix to prevent premature winner declarations"""
    
    import os
    
    print("=== FIXING PREMATURE WINNER ISSUE ON SERVER ===")
    
    # Path to scoring_updater.py on server
    scoring_file = "scoring_updater.py"
    
    if not os.path.exists(scoring_file):
        print(f"❌ File not found: {scoring_file}")
        print("Make sure you're in the correct directory with the scoring_updater.py file")
        return False
    
    try:
        # Read the current file
        with open(scoring_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the problematic line
        old_pattern = "is_winner = rank == 1  # First place is the winner"
        
        if old_pattern not in content:
            print("❌ Pattern not found - file may already be fixed or different")
            return False
        
        # Replace with the fixed version
        new_pattern = """# Check if the week is completely finished before declaring winners
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       COUNT(CASE WHEN is_final = 1 THEN 1 END) as completed_games
                FROM nfl_games 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            total_games, completed_games = cursor.fetchone()
            week_completed = (total_games == completed_games and total_games > 0)
            
            # Clear existing results for this week/year
            cursor.execute('''
                DELETE FROM weekly_results 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            # Insert new results
            for rank, result in enumerate(results, 1):
                # Only mark as winner if the week is completely finished
                is_winner = rank == 1 and week_completed"""
        
        # Find the context and replace
        context_start = """# Clear existing results for this week/year
            cursor.execute('''
                DELETE FROM weekly_results 
                WHERE week = ? AND year = ?
            ''', (week, year))
            
            # Insert new results
            for rank, result in enumerate(results, 1):
                is_winner = rank == 1  # First place is the winner"""
        
        if context_start not in content:
            print("❌ Context not found - file structure may be different")
            return False
        
        # Perform the replacement
        fixed_content = content.replace(context_start, new_pattern)
        
        # Backup the original file
        backup_file = f"{scoring_file}.backup"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created backup: {backup_file}")
        
        # Write the fixed version
        with open(scoring_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Applied fix to {scoring_file}")
        print("✅ The system will now only mark winners when ALL games in the week are completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        return False

if __name__ == "__main__":
    if fix_premature_winner_issue():
        print("\n🎉 SUCCESS! Premature winner issue fixed!")
        print("Benefits:")
        print("  - Week 3 winners will be cleared until all games complete")
        print("  - Season leaderboard will show only legitimate winners")
        print("  - Future weeks will wait for completion before declaring winners")
    else:
        print("\n❌ FAILED! Manual fix may be required")
        print("Contact your developer for assistance")
