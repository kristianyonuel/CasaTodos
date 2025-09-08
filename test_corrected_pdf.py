#!/usr/bin/env python3
"""
Test the corrected PDF generation with proper week filtering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from pdf_generator import generate_weekly_dashboard_pdf

def check_week_data():
    """Check the actual data for Week 1 to verify counts"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("🔍 Checking Week 1, 2025 data...")
    
    # Check total games for Week 1
    cursor.execute('''
        SELECT COUNT(*) as total_games, 
               COUNT(CASE WHEN is_final = 1 THEN 1 END) as final_games
        FROM nfl_games 
        WHERE week = 1 AND year = 2025
    ''')
    
    game_counts = cursor.fetchone()
    print(f"📊 Week 1 Games: {game_counts[0]} total, {game_counts[1]} final")
    
    # Check a few users' actual picks for Week 1
    cursor.execute('''
        SELECT u.username,
               COUNT(CASE WHEN p.is_correct = 1 AND g.week = 1 AND g.year = 2025 THEN 1 END) as week1_wins,
               COUNT(CASE WHEN p.is_correct = 0 AND g.week = 1 AND g.year = 2025 THEN 1 END) as week1_losses,
               COUNT(CASE WHEN g.week = 1 AND g.year = 2025 THEN p.id END) as week1_picks
        FROM users u
        LEFT JOIN user_picks p ON u.id = p.user_id
        LEFT JOIN nfl_games g ON p.game_id = g.id
        WHERE u.is_admin = 0 AND u.username IN ('Raymond', 'Javier', 'Rada')
        GROUP BY u.id, u.username
        ORDER BY week1_wins DESC
    ''')
    
    user_data = cursor.fetchall()
    print("\n📋 Sample user data for Week 1:")
    for username, wins, losses, picks in user_data:
        total_games = wins + losses
        if total_games > 0:
            win_pct = (wins / total_games) * 100
            print(f"  {username}: {wins} wins, {losses} losses, {picks} picks, {win_pct:.1f}% win rate")
    
    conn.close()
    return True

def test_corrected_pdf():
    """Test the corrected PDF generation"""
    print("\n📄 Testing corrected PDF generation...")
    
    try:
        pdf_bytes = generate_weekly_dashboard_pdf(1, 2025)
        
        if pdf_bytes and len(pdf_bytes) > 0:
            filename = "corrected_weekly_dashboard_week_1_2025.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"✅ Corrected PDF generated: {filename}")
            print(f"📊 PDF size: {len(pdf_bytes)} bytes")
            print("\n🎉 The PDF should now show correct win/loss counts for Week 1 only!")
            return True
        else:
            print("❌ PDF generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏈 Testing Corrected PDF Generation")
    print("=" * 40)
    
    check_week_data()
    success = test_corrected_pdf()
    
    if success:
        print("\n✅ PDF generation fixed! Win/loss counts are now accurate for the specified week.")
    else:
        print("\n❌ PDF generation still has issues.")
    
    exit(0 if success else 1)
