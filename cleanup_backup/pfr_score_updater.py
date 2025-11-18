import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import json

class ProFootballReferenceUpdater:
    def __init__(self, db_path='nfl_fantasy.db'):
        self.db_path = db_path
        self.base_url = "https://www.pro-football-reference.com/years/2025/week_{}.htm"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_team_mapping(self):
        """Map Pro Football Reference team names to our database team names"""
        return {
            # AFC East
            'New England Patriots': 'New England Patriots',
            'Buffalo Bills': 'Buffalo Bills', 
            'Miami Dolphins': 'Miami Dolphins',
            'New York Jets': 'New York Jets',
            
            # AFC North
            'Pittsburgh Steelers': 'Pittsburgh Steelers',
            'Baltimore Ravens': 'Baltimore Ravens',
            'Cincinnati Bengals': 'Cincinnati Bengals',
            'Cleveland Browns': 'Cleveland Browns',
            
            # AFC South
            'Indianapolis Colts': 'Indianapolis Colts',
            'Jacksonville Jaguars': 'Jacksonville Jaguars',
            'Houston Texans': 'Houston Texans',
            'Tennessee Titans': 'Tennessee Titans',
            
            # AFC West
            'Denver Broncos': 'Denver Broncos',
            'Los Angeles Chargers': 'Los Angeles Chargers',
            'Kansas City Chiefs': 'Kansas City Chiefs',
            'Las Vegas Raiders': 'Las Vegas Raiders',
            
            # NFC East
            'Philadelphia Eagles': 'Philadelphia Eagles',
            'Dallas Cowboys': 'Dallas Cowboys',
            'Washington Commanders': 'Washington Commanders',
            'New York Giants': 'New York Giants',
            
            # NFC North
            'Green Bay Packers': 'Green Bay Packers',
            'Detroit Lions': 'Detroit Lions',
            'Chicago Bears': 'Chicago Bears',
            'Minnesota Vikings': 'Minnesota Vikings',
            
            # NFC South
            'Tampa Bay Buccaneers': 'Tampa Bay Buccaneers',
            'Carolina Panthers': 'Carolina Panthers',
            'Atlanta Falcons': 'Atlanta Falcons',
            'New Orleans Saints': 'New Orleans Saints',
            
            # NFC West
            'Los Angeles Rams': 'Los Angeles Rams',
            'Seattle Seahawks': 'Seattle Seahawks',
            'San Francisco 49ers': 'San Francisco 49ers',
            'Arizona Cardinals': 'Arizona Cardinals'
        }

    def fetch_week_scores(self, week_number):
        """Fetch scores for a specific week from Pro Football Reference"""
        url = self.base_url.format(week_number)
        
        try:
            print(f"🔍 Fetching Week {week_number} from: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the scores table
            scores_table = soup.find('table', {'id': 'games'})
            if not scores_table:
                print(f"❌ No games table found for Week {week_number}")
                return []
                
            games = []
            
            # Parse each game row
            rows = scores_table.find('tbody').find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 8:
                    continue
                    
                try:
                    # Extract game data
                    date_cell = cells[0].get_text().strip()
                    away_team = cells[3].get_text().strip() 
                    away_score_text = cells[4].get_text().strip()
                    home_team = cells[6].get_text().strip()
                    home_score_text = cells[7].get_text().strip()
                    
                    # Skip if scores are empty (game not played yet)
                    if not away_score_text or not home_score_text:
                        continue
                        
                    away_score = int(away_score_text)
                    home_score = int(home_score_text)
                    
                    # Determine winner
                    if away_score > home_score:
                        winner = away_team
                    elif home_score > away_score:
                        winner = home_team
                    else:
                        winner = "TIE"  # Rare but possible
                    
                    # Check for overtime
                    overtime = "OT" in row.get_text()
                    
                    games.append({
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_score': away_score,
                        'home_score': home_score,
                        'winner': winner,
                        'overtime': overtime,
                        'date': date_cell
                    })
                    
                except (ValueError, IndexError) as e:
                    print(f"⚠️  Error parsing row: {e}")
                    continue
                    
            print(f"✅ Found {len(games)} completed games for Week {week_number}")
            return games
            
        except requests.RequestException as e:
            print(f"❌ Error fetching Week {week_number}: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error parsing Week {week_number}: {e}")
            return []

    def update_database_scores(self, week_number, games):
        """Update database with scores for a specific week"""
        if not games:
            return 0
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updated_count = 0
        team_mapping = self.get_team_mapping()
        
        try:
            # Get all games for this week
            cursor.execute("""
                SELECT id, away_team, home_team, away_score, home_score
                FROM nfl_games 
                WHERE week = ?
            """, (week_number,))
            
            db_games = {(row[1], row[2]): row for row in cursor.fetchall()}
            
            for game in games:
                away_team = team_mapping.get(game['away_team'], game['away_team'])
                home_team = team_mapping.get(game['home_team'], game['home_team'])
                
                # Find matching game in database
                db_key = (away_team, home_team)
                if db_key in db_games:
                    game_id, db_away, db_home, db_away_score, db_home_score = db_games[db_key]
                    
                    # Only update if scores have changed
                    if (db_away_score != game['away_score'] or 
                        db_home_score != game['home_score']):
                        
                        # Update game scores
                        cursor.execute("""
                            UPDATE nfl_games 
                            SET away_score = ?, home_score = ?, 
                                game_status = 'Final', is_final = 1,
                                overtime = ?, updated_at = datetime('now')
                            WHERE id = ?
                        """, (game['away_score'], game['home_score'], 
                              game['overtime'], game_id))
                        
                        # Update user picks
                        winning_team = team_mapping.get(game['winner'], game['winner'])
                        cursor.execute("""
                            UPDATE user_picks 
                            SET is_correct = CASE 
                                WHEN selected_team = ? THEN 1 
                                ELSE 0 
                            END,
                            points_earned = CASE 
                                WHEN selected_team = ? THEN 1 
                                ELSE 0 
                            END
                            WHERE game_id = ?
                        """, (winning_team, winning_team, game_id))
                        
                        updated_count += 1
                        print(f"✅ Updated: {away_team} @ {home_team}: {game['away_score']}-{game['home_score']}")
                else:
                    print(f"⚠️  Game not found in DB: {away_team} @ {home_team}")
            
            conn.commit()
            print(f"📊 Week {week_number}: Updated {updated_count} games")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Database error for Week {week_number}: {e}")
        finally:
            conn.close()
            
        return updated_count

    def update_all_weeks(self, start_week=1, end_week=18):
        """Update scores for all weeks in the season"""
        print(f"🏈 UPDATING ALL WEEKS {start_week}-{end_week} FROM PRO FOOTBALL REFERENCE")
        print("=" * 70)
        
        total_updated = 0
        successful_weeks = []
        failed_weeks = []
        
        for week in range(start_week, end_week + 1):
            try:
                games = self.fetch_week_scores(week)
                updated = self.update_database_scores(week, games)
                
                total_updated += updated
                successful_weeks.append(week)
                
                # Be respectful to the server
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Failed to update Week {week}: {e}")
                failed_weeks.append(week)
        
        print(f"\n📈 SUMMARY:")
        print(f"✅ Successfully updated {len(successful_weeks)} weeks")
        print(f"❌ Failed to update {len(failed_weeks)} weeks: {failed_weeks}")
        print(f"📊 Total games updated: {total_updated}")
        
        return {
            'total_updated': total_updated,
            'successful_weeks': successful_weeks,
            'failed_weeks': failed_weeks
        }

    def update_current_week(self):
        """Update scores for the current week only"""
        # Determine current week (could be enhanced with actual NFL schedule logic)
        current_week = 10  # For now, assume week 10
        
        print(f"🔄 Updating current Week {current_week}")
        games = self.fetch_week_scores(current_week)
        return self.update_database_scores(current_week, games)

if __name__ == "__main__":
    updater = ProFootballReferenceUpdater()
    
    # Update all weeks 1-18
    result = updater.update_all_weeks(1, 18)
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Updated {result['total_updated']} games across {len(result['successful_weeks'])} weeks")