#!/usr/bin/env python3
"""
Template Fix Script - Fixes incorrect URL references in templates
"""

import os
import re

def fix_template_urls():
    """Fix incorrect URL references in templates"""
    
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        print("❌ Templates directory not found")
        return False
    
    fixes_made = 0
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix common incorrect URL references
                fixes = [
                    # Fix export_all_picks_csv -> export_all_users_picks_csv
                    (r"url_for\(['\"]export_all_picks_csv['\"]", "url_for('export_all_users_picks_csv'"),
                    # Fix export_picks_csv -> export_all_users_picks_csv  
                    (r"url_for\(['\"]export_picks_csv['\"]", "url_for('export_all_users_picks_csv'"),
                    # Fix my_picks_csv -> my_picks_export (if needed)
                    (r"url_for\(['\"]my_picks_csv['\"]", "url_for('my_picks_export'"),
                ]
                
                for pattern, replacement in fixes:
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        print(f"🔧 Fixed URL reference in {filename}: {pattern}")
                        content = new_content
                        fixes_made += 1
                
                # Write back if changes were made
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Updated {filename}")
                else:
                    print(f"✅ {filename} - no fixes needed")
                    
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
    
    print(f"\n📊 Total fixes made: {fixes_made}")
    return fixes_made > 0

if __name__ == "__main__":
    print("🏈 La Casa de Todos - Template URL Fix Script")
    print("=" * 50)
    fix_template_urls()
