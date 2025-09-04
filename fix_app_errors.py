"""
Script to identify and fix common app.py errors
"""
import ast
import sys

def check_app_syntax():
    """Check app.py for syntax errors"""
    try:
        with open('app.py', 'r') as f:
            code = f.read()
        
        # Parse the code
        ast.parse(code)
        print("✅ No syntax errors found in app.py")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error in app.py:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def check_imports():
    """Check for import issues"""
    try:
        # Test imports
        import database
        print("✅ database.py imports successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        import nfl_schedule
        print("✅ nfl_schedule.py imports successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def main():
    print("Checking app.py for errors...")
    print("=" * 40)
    
    syntax_ok = check_app_syntax()
    imports_ok = check_imports()
    
    if syntax_ok and imports_ok:
        print("\n✅ All checks passed!")
        print("You can now run: python3 app.py")
    else:
        print("\n❌ Issues found. Fix the above errors first.")

if __name__ == "__main__":
    main()
