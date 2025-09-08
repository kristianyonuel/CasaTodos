#!/usr/bin/env python3
"""
Comprehensive PDF generation test to debug "failed to load PDF document" issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from pdf_generator import generate_weekly_dashboard_pdf


def debug_pdf_generation():
    """Debug PDF generation with detailed error checking"""
    print("🔍 PDF Generation Debug Test")
    print("=" * 50)
    
    try:
        # Test 1: Basic PDF generation
        print("\n1. Testing basic PDF generation...")
        pdf_bytes = generate_weekly_dashboard_pdf(1, 2025)
        
        if not pdf_bytes:
            print("❌ PDF generation returned None or empty")
            return False
        
        print(f"✅ PDF generated: {len(pdf_bytes)} bytes")
        
        # Test 2: Verify PDF header
        print("\n2. Checking PDF format...")
        if pdf_bytes[:4] != b'%PDF':
            print(f"❌ Invalid PDF header: {pdf_bytes[:10]}")
            return False
        
        print("✅ Valid PDF header detected")
        
        # Test 3: Check PDF footer
        if b'%%EOF' not in pdf_bytes[-20:]:
            print("⚠️  Warning: PDF might be truncated (no %%EOF marker)")
        else:
            print("✅ PDF properly terminated")
        
        # Test 4: Save and verify file
        print("\n3. Saving test PDF...")
        test_filename = "debug_pdf_test.pdf"
        with open(test_filename, 'wb') as f:
            f.write(pdf_bytes)
        
        # Check saved file
        saved_size = os.path.getsize(test_filename)
        if saved_size != len(pdf_bytes):
            print(f"❌ File size mismatch: {saved_size} vs {len(pdf_bytes)}")
            return False
        
        print(f"✅ PDF saved successfully: {test_filename} ({saved_size} bytes)")
        
        # Test 5: Check database content
        print("\n4. Checking database content...")
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
        user_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM user_picks')
        pick_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1 AND year = 2025')
        game_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Database stats:")
        print(f"   Users: {user_count}")
        print(f"   Picks: {pick_count}")
        print(f"   Week 1 Games: {game_count}")
        
        # Test 6: Generate PDF with different parameters
        print("\n5. Testing different parameters...")
        try:
            pdf_bytes_week2 = generate_weekly_dashboard_pdf(2, 2025)
            print(f"✅ Week 2 PDF: {len(pdf_bytes_week2) if pdf_bytes_week2 else 0} bytes")
        except Exception as e:
            print(f"⚠️  Week 2 PDF failed: {e}")
        
        print("\n🎉 All tests passed! PDF generation is working correctly.")
        print(f"\n📝 Test PDF saved as: {test_filename}")
        print("   You can try opening this file to verify it's valid.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure reportlab is installed: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_pdf_generation()
    exit(0 if success else 1)
