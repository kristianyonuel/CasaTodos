#!/usr/bin/env python3
"""
Comprehensive Pro Football Reference (PFR) Score Integration System

This system provides:
1. PFR as primary score source with ESPN API as backup fallback
2. Historical week backfill for weeks 1-18
3. Continuous monitoring of ongoing weeks  
4. Complete team mapping and error handling
5. Integration with existing NFL Fantasy database

Per user request: "now do it for every week to update all rest of the weeks to integrate 
into the database and keep updating from this page moving forward first.. do not remove 
the api for espn but keep this priority from now on"
"""

import sqlite3
import re
import requests
import json
import logging
import time
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensivePFRIntegration:
    def __init__(self, db_path='nfl_fantasy.db'):
        """Initialize the comprehensive PFR integration system"""
        self.db_path = db_path
        self.year = 2025
        
        # Team name mappings for PFR data
        self.team_mappings = {
            # PFR names -> database abbreviations
            'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL',
            'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
            'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
            'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
            'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX',
            'Kansas City Chiefs': 'KC', 'Las Vegas Raiders': 'LV', 'Los Angeles Chargers': 'LAC',
            'Los Angeles Rams': 'LAR', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN',
            'New England Patriots': 'NE', 'New Orleans Saints': 'NO', 'New York Giants': 'NYG',
            'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
            'San Francisco 49ers': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB',
            'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS'
        }
        
        # Reverse mapping for ESPN fallback
        self.abbrev_to_full = {v: k for k, v in self.team_mappings.items()}

    def fetch_pfr_week_data(self, week):
        """Fetch PFR data for a specific week using the fetch_webpage approach"""
        try:
            # Import the fetch_webpage function from the MCP tools
            # This will work in the VS Code environment
            from antml.function_calls import fetch_webpage
            
            url = f"https://www.pro-football-reference.com/years/2025/week_{week}.htm"
            
            logger.info(f"📡 Fetching PFR data for Week {week}")
            result = fetch_webpage(
                urls=[url], 
                query=f"NFL Week {week} game scores and results"
            )
            
            if result and len(result) > 0:
                return result[0].get('content', '')
            else:
                logger.warning(f"❌ No data received from PFR for Week {week}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching PFR data for Week {week}: {e}")
            return None
    
    def parse_pfr_scores(self, html_content):
        """Parse PFR HTML content to extract game scores"""
        games = []
        
        if not html_content:
            return games
            
        try:
            # Look for completed games with final scores
            # PFR format: "Team 24, Team 17" or "Team beat Team, 24-17"
            
            # Pattern 1: "Team1 24, Team2 17" format
            pattern1 = r'([A-Za-z\s]+?)\s+(\d+),\s+([A-Za-z\s]+?)\s+(\d+)'
            matches1 = re.findall(pattern1, html_content)
            
            for match in matches1:
                team1, score1, team2, score2 = match
                team1 = team1.strip()
                team2 = team2.strip()
                
                # Convert team names to abbreviations
                team1_abbr = self.team_mappings.get(team1)
                team2_abbr = self.team_mappings.get(team2)
                
                if team1_abbr and team2_abbr:
                    games.append({
                        'team1': team1_abbr,
                        'score1': int(score1),
                        'team2': team2_abbr, 
                        'score2': int(score2)
                    })
                    
            # Pattern 2: "Team1 beat Team2, 24-17" format
            pattern2 = r'([A-Za-z\s]+?)\s+beat\s+([A-Za-z\s]+?),\s+(\d+)-(\d+)'
            matches2 = re.findall(pattern2, html_content)
            
            for match in matches2:
                winner, loser, winner_score, loser_score = match
                winner = winner.strip()
                loser = loser.strip()
                
                # Convert team names to abbreviations
                winner_abbr = self.team_mappings.get(winner)
                loser_abbr = self.team_mappings.get(loser)
                
                if winner_abbr and loser_abbr:
                    games.append({
                        'team1': winner_abbr,
                        'score1': int(winner_score),
                        'team2': loser_abbr,
                        'score2': int(loser_score)
                    })
                    
            # Pattern 3: Direct team abbreviation extraction from tables/scores
            # This handles cases where team names are abbreviated in the HTML
            pattern3 = r'([A-Z]{2,3})\s+(\d+)\s+([A-Z]{2,3})\s+(\d+)'
            matches3 = re.findall(pattern3, html_content)
            
            for match in matches3:
                team1_abbr, score1, team2_abbr, score2 = match
                
                # Validate abbreviations
                if (team1_abbr in self.abbrev_to_full.keys() and 
                    team2_abbr in self.abbrev_to_full.keys()):
                    games.append({
                        'team1': team1_abbr,
                        'score1': int(score1),
                        'team2': team2_abbr,
                        'score2': int(score2)
                    })
                    
            logger.info(f"✅ Parsed {len(games)} games from PFR data")
            return games
            
        except Exception as e:
            logger.error(f"❌ Error parsing PFR scores: {e}")
            return games
    
    def update_database_scores(self, week, games):
        """Update database with parsed game scores"""
        if not games:
            logger.info(f"📊 No games to update for Week {week}")
            return 0
            
        updated = 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for game in games:
                # Find the game in database by matching teams and week
                cursor.execute("""
                    SELECT id, away_team, home_team FROM games 
                    WHERE week = ? AND year = ?
                """, (week, self.year))
                
                db_games = cursor.fetchall()
                
                for game_id, away_team, home_team in db_games:
                    # Match games by team combinations
                    if ((game['team1'] == away_team and game['team2'] == home_team) or
                        (game['team1'] == home_team and game['team2'] == away_team)):
                        
                        # Determine away/home scores based on team order
                        if game['team1'] == away_team:
                            away_score = game['score1']
                            home_score = game['score2']
                        else:
                            away_score = game['score2'] 
                            home_score = game['score1']
                            
                        # Update game with scores
                        cursor.execute("""
                            UPDATE games SET 
                                away_score = ?, 
                                home_score = ?,
                                is_final = 1,
                                last_updated = datetime('now')
                            WHERE id = ?
                        """, (away_score, home_score, game_id))
                        
                        updated += 1
                        logger.info(f"   ✅ Updated: {away_team} {away_score} - {home_team} {home_score}")
                        break
                        
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Updated {updated} games in Week {week}")
            return updated
            
        except Exception as e:
            logger.error(f"❌ Database update error for Week {week}: {e}")
            return 0
    
    def espn_fallback_update(self, week):
        """Use ESPN API as fallback when PFR fails"""
        try:
            logger.info(f"🔄 Using ESPN API fallback for Week {week}")
            
            url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week={week}&seasontype=2&year={self.year}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            if not events:
                logger.warning(f"❌ No ESPN events found for Week {week}")
                return 0
                
            updated = 0
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for event in events:
                try:
                    competitions = event.get('competitions', [])
                    if not competitions:
                        continue
                        
                    competition = competitions[0]
                    competitors = competition.get('competitors', [])
                    
                    if len(competitors) != 2:
                        continue
                        
                    # Extract team data
                    away_team = None
                    home_team = None
                    away_score = 0
                    home_score = 0
                    
                    for competitor in competitors:
                        team_abbr = competitor.get('team', {}).get('abbreviation', '')
                        score = int(competitor.get('score', 0))
                        is_home = competitor.get('homeAway') == 'home'
                        
                        if is_home:
                            home_team = team_abbr
                            home_score = score
                        else:
                            away_team = team_abbr
                            away_score = score
                    
                    # Check if game is final
                    status = competition.get('status', {})
                    state = status.get('type', {}).get('state', '')
                    is_final = state == 'post'
                    
                    if is_final and away_team and home_team:
                        # Update database
                        cursor.execute("""
                            UPDATE games SET 
                                away_score = ?, 
                                home_score = ?,
                                is_final = 1,
                                last_updated = datetime('now')
                            WHERE week = ? AND year = ? AND away_team = ? AND home_team = ?
                        """, (away_score, home_score, week, self.year, away_team, home_team))
                        
                        if cursor.rowcount > 0:
                            updated += 1
                            logger.info(f"   ✅ ESPN: {away_team} {away_score} - {home_team} {home_score}")
                            
                except Exception as e:
                    logger.error(f"❌ Error processing ESPN event: {e}")
                    continue
            
            conn.commit() 
            conn.close()
            
            logger.info(f"📊 ESPN fallback updated {updated} games in Week {week}")
            return updated
            
        except Exception as e:
            logger.error(f"❌ ESPN fallback failed for Week {week}: {e}")
            return 0
    
    def update_week_scores(self, week):
        """Update scores for a specific week using PFR primary + ESPN fallback"""
        logger.info(f"🏈 Starting score update for Week {week}")
        
        # Try PFR first
        pfr_data = self.fetch_pfr_week_data(week)
        
        if pfr_data:
            games = self.parse_pfr_scores(pfr_data)
            updated = self.update_database_scores(week, games)
            
            if updated > 0:
                logger.info(f"✅ PFR updated {updated} games for Week {week}")
                return updated
        
        # Fall back to ESPN if PFR fails or returns no updates
        logger.info(f"🔄 PFR didn't update games, trying ESPN fallback...")
        espn_updated = self.espn_fallback_update(week)
        
        if espn_updated > 0:
            logger.info(f"✅ ESPN fallback updated {espn_updated} games for Week {week}")
            return espn_updated
        
        logger.warning(f"⚠️  No updates applied for Week {week} from either source")
        return 0
    
    def update_all_weeks(self, weeks=None):
        """Update multiple weeks - historical backfill or current monitoring"""
        if weeks is None:
            weeks = list(range(1, 19))  # Weeks 1-18
            
        logger.info(f"🏈 Starting comprehensive score update for weeks: {weeks}")
        
        total_updated = 0
        results = {}
        
        for week in weeks:
            logger.info(f"\n{'='*50}")
            logger.info(f"🏈 Processing Week {week}")
            logger.info(f"{'='*50}")
            
            updated = self.update_week_scores(week)
            total_updated += updated
            results[week] = updated
            
            # Brief pause between weeks to be respectful to APIs
            time.sleep(1)
            
        logger.info(f"\n🎯 COMPREHENSIVE UPDATE COMPLETE")
        logger.info(f"📊 Total games updated: {total_updated}")
        
        for week, count in results.items():
            if count > 0:
                logger.info(f"   Week {week}: {count} games")
                
        return results
    
    def get_current_week(self):
        """Determine current NFL week for monitoring"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find the week with games that are not final
            cursor.execute("""
                SELECT week FROM games 
                WHERE year = ? AND is_final = 0 
                ORDER BY week LIMIT 1
            """, (self.year,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                # If all games are final, check for next week
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MAX(week) FROM games WHERE year = ?
                """, (self.year,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    return min(result[0] + 1, 18)  # Cap at week 18
                else:
                    return 1  # Default to week 1
                    
        except Exception as e:
            logger.error(f"❌ Error determining current week: {e}")
            return 11  # Conservative default
    
    def monitor_current_week(self):
        """Monitor and update the current week continuously"""
        current_week = self.get_current_week()
        logger.info(f"🔄 Monitoring current Week {current_week}")
        
        updated = self.update_week_scores(current_week)
        
        if updated > 0:
            logger.info(f"✅ Live monitoring updated {updated} games in Week {current_week}")
        else:
            logger.info(f"📊 No new updates for Week {current_week}")
            
        return updated

def main():
    """Main execution for comprehensive PFR integration"""
    print("🏈 COMPREHENSIVE PRO FOOTBALL REFERENCE INTEGRATION")
    print("=" * 60)
    
    system = ComprehensivePFRIntegration()
    
    # Option 1: Update all weeks (historical backfill)
    print("\n1. Historical backfill for all weeks")
    print("2. Update current week only") 
    print("3. Update specific weeks")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        # Full historical update
        results = system.update_all_weeks()
        print("\n📊 Historical backfill completed")
        
    elif choice == "2":
        # Current week monitoring
        system.monitor_current_week()
        
    elif choice == "3":
        # Specific weeks
        weeks_input = input("Enter weeks (e.g., 1,2,3 or 10-12): ").strip()
        
        try:
            if '-' in weeks_input:
                start, end = map(int, weeks_input.split('-'))
                weeks = list(range(start, end + 1))
            else:
                weeks = [int(w.strip()) for w in weeks_input.split(',')]
                
            results = system.update_all_weeks(weeks)
            print(f"\n📊 Updated weeks {weeks}")
            
        except ValueError:
            print("❌ Invalid week format")
            
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()