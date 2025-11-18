#!/usr/bin/env python3
"""
Debug script to test if Thursday pick revelation is working in the actual app
"""

import requests
from bs4 import BeautifulSoup

def test_thursday_revelation():
    """Test if Thursday pick revelation appears in the games page"""
    
    print("🔍 Testing Thursday Pick Revelation in Live App")
    print("=" * 60)
    
    try:
        # Make request to games page
        response = requests.get('http://localhost/games', timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for Thursday pick revelation section
        revelation_section = soup.find('div', class_='picks-revelation-section')
        
        if revelation_section:
            print("✅ Thursday Picks Revelation Section Found!")
            
            # Check for title
            title = revelation_section.find('h3')
            if title:
                print(f"📋 Title: {title.get_text().strip()}")
            
            # Check for subtitle
            subtitle = revelation_section.find('p', class_='revelation-subtitle')
            if subtitle:
                print(f"📝 Subtitle: {subtitle.get_text().strip()}")
            
            # Check for game picks cards
            game_cards = revelation_section.find_all('div', class_='game-picks-card')
            print(f"🎯 Game Cards Found: {len(game_cards)}")
            
            for i, card in enumerate(game_cards, 1):
                game_title = card.find('div', class_='game-title')
                if game_title:
                    title_text = game_title.find('strong')
                    if title_text:
                        print(f"  Game {i}: {title_text.get_text().strip()}")
                
                # Check for picks
                picks_grid = card.find('div', class_='picks-grid')
                if picks_grid:
                    user_picks = picks_grid.find_all('div', class_='user-pick')
                    print(f"    Picks shown: {len(user_picks)}")
                    
                    for pick in user_picks:
                        username = pick.find('span', class_='username')
                        selected_team = pick.find('span', class_='selected-team')
                        if username and selected_team:
                            print(f"      {username.get_text().strip()}: {selected_team.get_text().strip()}")
        else:
            print("❌ Thursday Picks Revelation Section NOT Found")
            
            # Check if the condition variables are present
            print("\n🔍 Checking for condition variables...")
            
            # Look for any mention of "thursday" in the HTML
            if 'thursday' in html_content.lower():
                print("✅ 'thursday' found in HTML content")
            else:
                print("❌ 'thursday' NOT found in HTML content")
            
            # Check if games section exists
            games_section = soup.find('div', class_='games-section')
            if games_section:
                print("✅ Games section found")
                
                # Count total games
                game_cards = games_section.find_all('div', class_='game-card')
                print(f"📊 Total game cards: {len(game_cards)}")
                
                # Look for Thursday games
                thursday_found = False
                for card in game_cards:
                    if 'thursday' in card.get_text().lower():
                        thursday_found = True
                        break
                
                if thursday_found:
                    print("✅ Thursday games found in game cards")
                else:
                    print("❌ No Thursday games found in game cards")
                    
            else:
                print("❌ Games section NOT found")
                
        # Check for any error messages
        error_messages = soup.find_all('div', class_='alert-error')
        if error_messages:
            print(f"\n⚠️ Error messages found: {len(error_messages)}")
            for msg in error_messages:
                print(f"  - {msg.get_text().strip()}")
        
        # Check page title
        title_tag = soup.find('title')
        if title_tag:
            print(f"\n📄 Page Title: {title_tag.get_text().strip()}")
        
        print(f"\n📐 Total HTML Length: {len(html_content)} characters")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_thursday_revelation()
