#!/usr/bin/env python3

# Fix the %-I format strings in the games template
import re

def fix_template():
    with open('templates/games.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Original content has %-I patterns:", "%-I" in content)
    
    # Replace %-I with %I (Windows compatible)
    fixed_content = content.replace('%-I', '%I')
    
    print("Fixed content has %-I patterns:", "%-I" in fixed_content)
    
    with open('templates/games.html', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Template fixed!")

if __name__ == "__main__":
    fix_template()
