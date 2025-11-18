#!/usr/bin/env python3
"""
Check ESPN API for current game status to understand the discrepancy
"""
import requests
import json
from datetime import datetime

def check_espn_api():
    print('=== ESPN API STATUS CHECK ===')
    print()
    
    # ESPN API endpoint for NFL games
    # Try to get Week 3 games for 2025
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    
    try:
        print("Checking ESPN API for current NFL games...")
        
        # Get current games
        params = {
            'limit': 50,
            'seasontype': 2,  # Regular season
            'week': 3,
            'year': 2025
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✓ ESPN API Response: {response.status_code}")
            print(f"Found {len(data.get('events', []))} games")
            print()
            
            # Look for Buffalo game specifically
            buffalo_found = False
            for event in data.get('events', []):
                competitions = event.get('competitions', [])
                for competition in competitions:
                    competitors = competition.get('competitors', [])
                    if len(competitors) >= 2:
                        team1 = competitors[0].get('team', {}).get('abbreviation', '')
                        team2 = competitors[1].get('team', {}).get('abbreviation', '')
                        
                        # Check if this is the Buffalo-Miami game
                        if ('BUF' in [team1, team2] and 'MIA' in [team1, team2]):
                            buffalo_found = True
                            
                            # Get game details
                            status = competition.get('status', {})
                            status_type = status.get('type', {})
                            
                            print(f"🏈 FOUND BUFFALO GAME:")
                            print(f"  Teams: {team1} vs {team2}")
                            print(f"  Status: {status_type.get('name', 'Unknown')}")
                            print(f"  State: {status_type.get('state', 'Unknown')}")
                            print(f"  Completed: {status_type.get('completed', False)}")
                            print(f"  Detail: {status_type.get('detail', 'No detail')}")
                            
                            # Get scores
                            for i, competitor in enumerate(competitors):
                                team_name = competitor.get('team', {}).get('abbreviation', f'Team{i+1}')
                                score = competitor.get('score', 'No score')
                                print(f"  {team_name}: {score}")
                            
                            print()
                            break
            
            if not buffalo_found:
                print("❌ Buffalo game not found in ESPN API response")
                print("Available games:")
                for event in data.get('events', [])[:5]:  # Show first 5 games
                    competitions = event.get('competitions', [])
                    for competition in competitions:
                        competitors = competition.get('competitors', [])
                        if len(competitors) >= 2:
                            team1 = competitors[0].get('team', {}).get('abbreviation', '')
                            team2 = competitors[1].get('team', {}).get('abbreviation', '')
                            print(f"  {team1} vs {team2}")
        
        else:
            print(f"❌ ESPN API Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    
    except Exception as e:
        print(f"❌ Error checking ESPN API: {e}")
    
    print()
    print("=== DIAGNOSIS ===")
    print("The remote server database shows Week 3 games are not being updated.")
    print("This means either:")
    print("1. ESPN API is not returning final status for these games yet")
    print("2. Background updater is not running on the remote server")
    print("3. There's an issue with the ESPN API integration on the server")
    print()
    print("Need to check if background updater is running on remote server.")

if __name__ == '__main__':
    check_espn_api()
