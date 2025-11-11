#!/usr/bin/env python3
"""
Check system status for logos, betting odds, and Monday games
"""

import sqlite3
import os
from pathlib import Path

def check_system_status():
    print("🏈 La Casa de Todos - System Status Check")
    print("=" * 50)
    
    # Check database file
    db_path = 'nfl_fantasy.db'
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path) / 1024  # KB
        print(f"✅ Database: {db_path} exists ({db_size:.1f} KB)")
    else:
        print(f"❌ Database: {db_path} not found")
        return
    
    # Check team logos
    logo_dir = Path('static/images')
    if logo_dir.exists():
        logo_files = list(logo_dir.glob('*.svg'))
        print(f"✅ Team Logos: {len(logo_files)} SVG files found")
        if len(logo_files) < 32:
            print(f"⚠️  Expected 32 team logos, found {len(logo_files)}")
    else:
        print("❌ Logo directory 'static/images' not found")
    
    # Check database content
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current week
        cursor.execute("SELECT DISTINCT week FROM games ORDER BY week DESC LIMIT 1")
        latest_week = cursor.fetchone()
        print(f"✅ Latest Week in DB: {latest_week[0] if latest_week else 'None'}")
        
        # Check Week 10 games
        cursor.execute("SELECT COUNT(*) FROM games WHERE week = 10")
        week10_games = cursor.fetchone()[0]
        print(f"✅ Week 10 Games: {week10_games} games")
        
        # Check Monday Night games
        cursor.execute("SELECT game_id, home_team, away_team, game_date, is_completed FROM games WHERE is_monday_night = 1 AND week = 10")
        mnf_games = cursor.fetchall()
        print(f"✅ Week 10 Monday Night Games: {len(mnf_games)}")
        for game in mnf_games:
            print(f"   Game {game[0]}: {game[2]} @ {game[1]} | Date: {game[3]} | Complete: {game[4]}")
        
        # Check betting odds columns
        cursor.execute("PRAGMA table_info(games)")
        columns = [col[1] for col in cursor.fetchall()]
        betting_columns = [col for col in columns if 'odds' in col.lower() or 'spread' in col.lower()]
        print(f"✅ Betting Columns: {len(betting_columns)} found")
        if betting_columns:
            print(f"   Columns: {', '.join(betting_columns)}")
        
        # Check recent game updates
        cursor.execute("SELECT game_id, home_team, away_team, home_score, away_score, last_updated FROM games WHERE week = 10 ORDER BY last_updated DESC LIMIT 3")
        recent_updates = cursor.fetchall()
        print(f"✅ Recent Game Updates (Week 10):")
        for game in recent_updates:
            print(f"   {game[1]} vs {game[2]}: {game[3]}-{game[4]} | Updated: {game[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
    
    # Check template file
    template_path = 'templates/games.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_logos = 'team-logo' in content
            has_betting = 'betting-info' in content
            has_scores = 'game-score' in content
            print(f"✅ Template Status:")
            print(f"   Team Logos: {'✅' if has_logos else '❌'}")
            print(f"   Betting Info: {'✅' if has_betting else '❌'}")
            print(f"   Score Display: {'✅' if has_scores else '❌'}")
    else:
        print("❌ Template 'templates/games.html' not found")
    
    print("\n🔍 System Ready for Enhancement Testing")

if __name__ == "__main__":
    check_system_status()