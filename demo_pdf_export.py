#!/usr/bin/env python3
"""
Demo script to show PDF export functionality with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from pdf_generator import generate_weekly_dashboard_pdf

def add_sample_picks():
    """Add some sample picks to demonstrate PDF functionality"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get first few games for Week 1
    cursor.execute('''
        SELECT id, away_team, home_team 
        FROM nfl_games 
        WHERE week = 1 AND year = 2025 
        ORDER BY game_date 
        LIMIT 3
    ''')
    games = cursor.fetchall()
    
    # Get non-admin users
    cursor.execute('SELECT id, username FROM users WHERE is_admin = 0 LIMIT 3')
    users = cursor.fetchall()
    
    if not games or not users:
        print("❌ No games or users found for demo")
        conn.close()
        return False
    
    print("📝 Adding sample picks for demo...")
    
    # Add some picks for demonstration
    for user_id, username in users:
        for i, (game_id, away_team, home_team) in enumerate(games):
            # Alternate picks between home and away
            selected_team = home_team if (user_id + i) % 2 == 0 else away_team
            
            # Add pick if it doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO user_picks 
                (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (user_id, game_id, selected_team, 24, 21))
    
    conn.commit()
    conn.close()
    print("✅ Sample picks added")
    return True

def demo_pdf_export():
    """Demonstrate PDF export with current data"""
    print("🏈 La Casa de Todos - PDF Export Demo")
    print("=" * 40)
    
    # Add sample data
    if add_sample_picks():
        print("\n📄 Generating PDF with sample data...")
        
        try:
            pdf_bytes = generate_weekly_dashboard_pdf(1, 2025)
            
            if pdf_bytes and len(pdf_bytes) > 0:
                filename = "demo_weekly_dashboard_week_1_2025.pdf"
                with open(filename, 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"✅ Demo PDF generated: {filename}")
                print(f"📊 PDF size: {len(pdf_bytes)} bytes")
                print("\n📋 PDF Contents:")
                print("• Title: La Casa de Todos - Week 1 Dashboard")
                print("• Week Summary: Total/Final/Pending games")
                print("• Leaderboard Table: Rank, Player, Wins, Losses, Win %, Monday Night")
                print("• Games Status Table: Game type, Matchup, Score, Status")
                print("\n🎉 You can now use the admin panel 'Export Weekly Dashboard PDF' button!")
                return True
            else:
                print("❌ PDF generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False

if __name__ == "__main__":
    success = demo_pdf_export()
    exit(0 if success else 1)
