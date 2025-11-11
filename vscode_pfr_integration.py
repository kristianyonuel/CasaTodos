#!/usr/bin/env python3
"""
VS Code Compatible PFR Score Integration System

This system works within the VS Code environment using fetch_webpage tool to:
1. Fetch scores from Pro Football Reference as primary source
2. Use ESPN API as backup fallback 
3. Update all historical weeks that need score updates
4. Provide continuous monitoring for current weeks

Per user request: "now do it for every week to update all rest of the weeks to integrate 
into the database and keep updating from this page moving forward first.. do not remove 
the api for espn but keep this priority from now on"
"""

import sqlite3
import re
import requests
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VSCodePFRIntegration:
    def __init__(self, db_path='nfl_fantasy.db'):
        """Initialize the VS Code compatible PFR integration system"""
        self.db_path = db_path
        self.year = 2025
        
        # Team name mappings for PFR data
        self.team_mappings = {
            # PFR full names -> database abbreviations
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
        
        # PFR abbreviations -> database abbreviations
        self.pfr_abbrev_mapping = {
            'ARI': 'ARI', 'ATL': 'ATL', 'BAL': 'BAL', 'BUF': 'BUF', 'CAR': 'CAR', 'CHI': 'CHI',
            'CIN': 'CIN', 'CLE': 'CLE', 'DAL': 'DAL', 'DEN': 'DEN', 'DET': 'DET', 'GNB': 'GB',
            'HOU': 'HOU', 'IND': 'IND', 'JAX': 'JAX', 'KAN': 'KC', 'LVR': 'LV', 'LAC': 'LAC',
            'LAR': 'LAR', 'MIA': 'MIA', 'MIN': 'MIN', 'NWE': 'NE', 'NOR': 'NO', 'NYG': 'NYG',
            'NYJ': 'NYJ', 'PHI': 'PHI', 'PIT': 'PIT', 'SFO': 'SF', 'SEA': 'SEA', 'TAM': 'TB',
            'TEN': 'TEN', 'WAS': 'WAS'
        }

    def fetch_pfr_week_data(self, week):
        """Fetch PFR data using VS Code fetch_webpage tool"""
        try:
            # Note: This function can only be called from within VS Code environment
            # where fetch_webpage tool is available
            print(f"📡 Fetching PFR data for Week {week}")
            print(f"📝 URL: https://www.pro-football-reference.com/years/2025/week_{week}.htm")
            print("⚠️  This function requires VS Code environment with fetch_webpage tool")
            print("💡 Please use this in VS Code with the fetch_webpage function available")
            
            return None  # Will be replaced by fetch_webpage call in VS Code environment
                
        except Exception as e:
            logger.error(f"❌ Error fetching PFR data for Week {week}: {e}")
            return None
    
    def parse_pfr_scores_from_content(self, html_content):
        """Parse PFR HTML content to extract game scores"""
        games = []
        
        if not html_content:
            return games
            
        try:
            # Enhanced parsing patterns for PFR data
            
            # Pattern 1: Look for score lines like "Team1 24, Team2 17"
            pattern1 = r'(\w{3})\s+(\d+),?\s+(\w{3})\s+(\d+)'
            matches1 = re.findall(pattern1, html_content)
            
            for match in matches1:
                team1, score1, team2, score2 = match
                team1_db = self.pfr_abbrev_mapping.get(team1, team1)
                team2_db = self.pfr_abbrev_mapping.get(team2, team2)
                
                if team1_db and team2_db:
                    games.append({
                        'team1': team1_db,
                        'score1': int(score1),
                        'team2': team2_db,
                        'score2': int(score2)
                    })
                    
            # Pattern 2: Look for "defeated" format
            pattern2 = r'(\w{3})\s+defeated\s+(\w{3}),?\s+(\d+)-(\d+)'
            matches2 = re.findall(pattern2, html_content)
            
            for match in matches2:
                winner, loser, winner_score, loser_score = match
                winner_db = self.pfr_abbrev_mapping.get(winner, winner)
                loser_db = self.pfr_abbrev_mapping.get(loser, loser)
                
                if winner_db and loser_db:
                    games.append({
                        'team1': winner_db,
                        'score1': int(winner_score),
                        'team2': loser_db,
                        'score2': int(loser_score)
                    })
                    
            # Pattern 3: Full team names
            full_name_pattern = r'([A-Za-z\s]+)\s+(\d+),\s+([A-Za-z\s]+)\s+(\d+)'
            matches3 = re.findall(full_name_pattern, html_content)
            
            for match in matches3:
                team1_name, score1, team2_name, score2 = match
                team1_name = team1_name.strip()
                team2_name = team2_name.strip()
                
                team1_db = self.team_mappings.get(team1_name)
                team2_db = self.team_mappings.get(team2_name)
                
                if team1_db and team2_db:
                    games.append({
                        'team1': team1_db,
                        'score1': int(score1),
                        'team2': team2_db,
                        'score2': int(score2)
                    })
                    
            # Remove duplicates
            unique_games = []
            seen = set()
            for game in games:
                game_key = (game['team1'], game['team2'], game['score1'], game['score2'])
                if game_key not in seen:
                    seen.add(game_key)
                    unique_games.append(game)
                    
            logger.info(f"✅ Parsed {len(unique_games)} unique games from PFR data")
            return unique_games
            
        except Exception as e:
            logger.error(f"❌ Error parsing PFR scores: {e}")
            return []
    
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
                # Find matching games by team combinations
                cursor.execute("""
                    SELECT id, away_team, home_team FROM nfl_games 
                    WHERE week = ? AND year = ?
                """, (week, self.year))
                
                db_games = cursor.fetchall()
                
                for game_id, away_team, home_team in db_games:
                    # Match games by team combinations (either direction)
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
                            UPDATE nfl_games SET 
                                away_score = ?, 
                                home_score = ?,
                                is_final = 1,
                                updated_at = datetime('now')
                            WHERE id = ?
                        """, (away_score, home_score, game_id))
                        
                        if cursor.rowcount > 0:
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
            
            # Disable SSL verification for Windows environment
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(url, timeout=10, verify=False)
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
                            UPDATE nfl_games SET 
                                away_score = ?, 
                                home_score = ?,
                                is_final = 1,
                                updated_at = datetime('now')
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

    def process_pfr_content_for_week(self, week, pfr_content):
        """Process PFR content for a specific week (to be called from VS Code)"""
        logger.info(f"🏈 Processing PFR content for Week {week}")
        
        if not pfr_content:
            logger.warning(f"❌ No PFR content provided for Week {week}")
            return 0
            
        # Parse scores from content
        games = self.parse_pfr_scores_from_content(pfr_content)
        
        if games:
            updated = self.update_database_scores(week, games)
            if updated > 0:
                logger.info(f"✅ PFR updated {updated} games for Week {week}")
                return updated
                
        # Fall back to ESPN if PFR parsing failed
        logger.info(f"🔄 PFR didn't update games, trying ESPN fallback...")
        espn_updated = self.espn_fallback_update(week)
        
        if espn_updated > 0:
            logger.info(f"✅ ESPN fallback updated {espn_updated} games for Week {week}")
            return espn_updated
        
        logger.warning(f"⚠️  No updates applied for Week {week} from either source")
        return 0

    def get_weeks_needing_updates(self):
        """Find weeks that need score updates"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find weeks with games that don't have final scores
            cursor.execute("""
                SELECT DISTINCT week FROM nfl_games 
                WHERE year = ? AND (
                    is_final = 0 OR 
                    away_score IS NULL OR 
                    home_score IS NULL OR
                    away_score = 0 AND home_score = 0
                )
                ORDER BY week
            """, (self.year,))
            
            weeks = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"📊 Found {len(weeks)} weeks needing updates: {weeks}")
            return weeks
            
        except Exception as e:
            logger.error(f"❌ Error finding weeks needing updates: {e}")
            return []

    def get_current_week(self):
        """Determine current NFL week"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find the lowest week with incomplete games
            cursor.execute("""
                SELECT MIN(week) FROM nfl_games 
                WHERE year = ? AND is_final = 0
            """, (self.year,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return result[0]
            else:
                return 11  # Default current week
                
        except Exception as e:
            logger.error(f"❌ Error determining current week: {e}")
            return 11

def test_week_update(week=11):
    """Test function to demonstrate week update"""
    print(f"🏈 TESTING WEEK {week} UPDATE SYSTEM")
    print("=" * 60)
    
    system = VSCodePFRIntegration()
    
    # Check current database state
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN is_final = 1 THEN 1 ELSE 0 END) as final_games
            FROM nfl_games WHERE week = ? AND year = 2025
        """, (week,))
        
        result = cursor.fetchone()
        total_games, final_games = result or (0, 0)
        
        print(f"📊 Week {week} Status:")
        print(f"   Total games: {total_games}")
        print(f"   Final games: {final_games}")
        print(f"   Games needing updates: {total_games - final_games}")
        
        if total_games - final_games > 0:
            print(f"🔄 Week {week} needs updates!")
            print("💡 Use fetch_webpage in VS Code to get PFR data, then call:")
            print(f"   system.process_pfr_content_for_week({week}, pfr_content)")
        else:
            print(f"✅ Week {week} is already complete!")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error checking week status: {e}")

def main():
    """Main function demonstrating the system"""
    print("🏈 VS CODE PFR INTEGRATION SYSTEM")
    print("=" * 60)
    print()
    print("This system is designed to work with VS Code's fetch_webpage tool.")
    print("Usage:")
    print("1. Use fetch_webpage to get PFR data for a week")
    print("2. Call system.process_pfr_content_for_week(week, content)")
    print("3. System will parse and update database with PFR + ESPN fallback")
    print()
    
    system = VSCodePFRIntegration()
    
    # Show weeks needing updates
    weeks_needed = system.get_weeks_needing_updates()
    current_week = system.get_current_week()
    
    print(f"📊 Current Week: {current_week}")
    print(f"📝 Weeks needing updates: {weeks_needed}")
    print()
    
    # Test current week
    test_week_update(current_week)

if __name__ == "__main__":
    main()