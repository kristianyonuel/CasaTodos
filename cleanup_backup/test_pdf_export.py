#!/usr/bin/env python3
"""
Test script to verify PDF generation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_generator import generate_weekly_dashboard_pdf


def test_pdf_generation():
    """Test PDF generation for current week"""
    try:
        print("Testing PDF generation...")
        
        # Test with Week 1, 2025
        week = 1
        year = 2025
        
        pdf_bytes = generate_weekly_dashboard_pdf(week, year)
        
        if pdf_bytes and len(pdf_bytes) > 0:
            print("✅ PDF generated successfully!")
            print(f"📊 PDF size: {len(pdf_bytes)} bytes")
            
            # Save test PDF to verify contents
            test_filename = f"test_weekly_dashboard_week_{week}_{year}.pdf"
            with open(test_filename, 'wb') as f:
                f.write(pdf_bytes)
            print(f"💾 Test PDF saved as: {test_filename}")
            
            return True
        else:
            print("❌ PDF generation failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n🎉 PDF export functionality is working correctly!")
    else:
        print("\n❌ PDF export functionality needs debugging")
    
    exit(0 if success else 1)
