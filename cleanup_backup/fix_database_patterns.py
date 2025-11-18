#!/usr/bin/env python3
"""
Database Connection Pattern Fix Script
This script updates all old database connection patterns to use the new context manager.
"""

import re
import os

def fix_database_patterns():
    """Fix all database connection patterns in app.py"""
    
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print("❌ app.py not found")
        return False
    
    print("🔧 Fixing database connection patterns...")
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Keep track of changes
    changes_made = 0
    
    # Pattern 1: Simple conn = get_db() followed by cursor = conn.cursor()
    # Replace with: with get_db() as conn:\n        cursor = conn.cursor()
    pattern1 = r'(\s+)conn = get_db\(\)\s*\n(\s+)cursor = conn\.cursor\(\)'
    replacement1 = r'\1with get_db() as conn:\n\2    cursor = conn.cursor()'
    
    new_content, count1 = re.subn(pattern1, replacement1, content)
    changes_made += count1
    
    if count1 > 0:
        print(f"✅ Fixed {count1} simple database connection patterns")
    
    # Pattern 2: Remove conn.close() calls since context manager handles it
    pattern2 = r'\s+conn\.close\(\)\s*\n'
    replacement2 = ''
    
    new_content, count2 = re.subn(pattern2, replacement2, new_content)
    changes_made += count2
    
    if count2 > 0:
        print(f"✅ Removed {count2} conn.close() calls")
    
    # Pattern 3: Fix indentation for code that was after the old pattern
    # This is more complex and might need manual adjustment
    
    if changes_made > 0:
        # Backup the original file
        backup_file = 'app.py.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📁 Original file backed up to {backup_file}")
        
        # Write the fixed content
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"🎉 Made {changes_made} total changes to database patterns")
        print("\n⚠️  Please review the changes and fix any indentation issues manually")
        return True
    else:
        print("ℹ️  No patterns found to fix")
        return False

def create_manual_fix_guide():
    """Create a guide for manually fixing remaining issues"""
    
    guide_content = """# Manual Database Connection Fix Guide

After running the automated fix, you may need to manually adjust some patterns.

## Common Issues to Look For:

### 1. Indentation Problems
If you see code that looks misaligned after a `with get_db() as conn:` block, 
add 4 spaces of indentation to align it properly.

**Before:**
```python
with get_db() as conn:
    cursor = conn.cursor()
cursor.execute("SELECT ...")  # Wrong indentation
```

**After:**
```python
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ...")  # Correct indentation
```

### 2. Return Statements in Database Blocks
Make sure return statements and other control flow are properly indented.

### 3. Exception Handling
Update try/except blocks that span database operations:

**Before:**
```python
try:
    conn = get_db()
    cursor = conn.cursor()
    # database operations
    conn.commit()
    conn.close()
except Exception as e:
    # error handling
```

**After:**
```python
try:
    with get_db() as conn:
        cursor = conn.cursor()
        # database operations
        conn.commit()
except Exception as e:
    # error handling
```

## Routes That Need Manual Review:

1. `/admin/rules` - Complex database operations
2. `/admin/create_game` - Multiple database operations
3. `/admin/update_game` - Complex update logic
4. `/admin/delete_game` - Transaction handling
5. `/force_create_games/<int:week>/<int:year>` - Large operations

## Testing After Changes:

1. Start the application: `python app.py`
2. Test registration: Go to `/register`
3. Test login: Go to `/login`
4. Test games page: Go to `/games`
5. Test making picks: Submit some picks
6. Check logs for any remaining errors

## Quick Fix Commands:

If you see specific errors, here are quick fixes:

### AttributeError: '_GeneratorContextManager' object has no attribute 'cursor'
```python
# Change this:
conn = get_db()
cursor = conn.cursor()

# To this:
with get_db() as conn:
    cursor = conn.cursor()
```

### IndentationError after context manager
Add 4 spaces to all lines that should be inside the `with` block.
"""
    
    with open('DATABASE_FIX_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📋 Created DATABASE_FIX_GUIDE.md for manual fixes")

if __name__ == "__main__":
    print("🚀 Starting database connection pattern fix...")
    print("=" * 60)
    
    success = fix_database_patterns()
    create_manual_fix_guide()
    
    if success:
        print("\n✅ Automated fixes completed!")
        print("🔍 Please review the changes and test the application")
        print("📋 Check DATABASE_FIX_GUIDE.md for manual fix instructions")
    else:
        print("\n❌ No automated fixes were applied")
        print("💡 You may need to fix the patterns manually")
    
    print("\n🧪 Recommended next steps:")
    print("1. Review app.py changes")
    print("2. Test the application")
    print("3. Check for any remaining errors")
    print("4. Fix indentation issues if needed")
