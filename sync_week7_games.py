#!/usr/bin/env python3
"""
Manual Week 7 Games Sync
Fix the missing Week 7 games issue
"""

import requests
import sqlite3
from datetime import datetime
import json

def sync_week7_games():
    """Manually sync Week 7 games from ESPN API"""
    
    # Get Week 7 games from ESPN API  
    print("🔄 Fetching Week 7 games from ESPN API...")
    
    try:
        # ESPN API for Week 7 2025
        url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        
        # Try different date ranges for Week 7 (Oct 17-21, 2025)
        week7_dates = ['20251017', '20251018', '20251019', '20251020', '20251021']
        all_games = []
        
        for date in week7_dates:
            try:
                params = {'dates': date, 'limit': 20}
                response = requests.get(url, params=params, timeout=15, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    events = data.get('events', [])
                    print(f"  {date}: Found {len(events)} games")
                    all_games.extend(events)
                else:
                    print(f"  {date}: API error {response.status_code}")
                    
            except Exception as e:
                print(f"  {date}: Error - {e}")
        
        print(f"\n📊 Total games found: {len(all_games)}")
        
        if not all_games:
            print("❌ No games found for Week 7")
            return False
            
        # Connect to database
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Clear existing Week 7 games
        cursor.execute("DELETE FROM nfl_games WHERE week = 7 AND year = 2025")
        print(f"🗑️ Cleared existing Week 7 games")
        
        games_added = 0
        
        for event in all_games:
            try:
                # Extract game information
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) < 2:
                    continue
                    
                # Get teams
                home_team = competitors[0]
                away_team = competitors[1]
                
                # Ensure we have home/away correctly
                if home_team.get('homeAway') == 'away':
                    home_team, away_team = away_team, home_team
                
                home_abbr = home_team.get('team', {}).get('abbreviation', '')
                away_abbr = away_team.get('team', {}).get('abbreviation', '')
                
                if not home_abbr or not away_abbr:
                    continue
                
                # Get game details
                game_date = event.get('date', '')
                game_id = event.get('id', f'manual_w7_{games_added}')
                status = event.get('status', {}).get('type', {}).get('name', 'scheduled')
                
                # Convert date format
                if game_date:
                    try:
                        dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                        game_date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        game_date_str = game_date
                else:
                    game_date_str = '2025-10-19 13:00:00'  # Default
                
                # Insert game
                cursor.execute("""
                    INSERT INTO nfl_games (
                        week, year, game_id, home_team, away_team, 
                        game_date, game_status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    7, 2025, f"espn_{game_id}", home_abbr, away_abbr,
                    game_date_str, status.lower(),
                    datetime.now(), datetime.now()
                ))
                
                games_added += 1
                print(f"  ✅ Added: {away_abbr} @ {home_abbr} - {game_date_str}")
                
            except Exception as e:
                print(f"  ❌ Error processing game: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Successfully added {games_added} Week 7 games!")
        return games_added > 0
        
    except Exception as e:
        print(f"❌ Failed to sync Week 7: {e}")
        return False

if __name__ == "__main__":
    print("=== MANUAL WEEK 7 SYNC ===")
    success = sync_week7_games()
    
    if success:
        print("\n✅ Week 7 games sync completed!")
        print("The app should now show Week 7 games.")
    else:
        print("\n❌ Week 7 sync failed.")
        print("Check network connection and API availability.")