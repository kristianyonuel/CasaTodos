#!/usr/bin/env python3
"""
FIX MONDAY NIGHT FOOTBALL SCORING
Forces score updates for Monday games and fixes missing scores
"""

import sqlite3
import requests
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect('database.db')
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def check_database_structure():
    """Check and display database structure"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        logger.info(f"Available tables: {tables}")
        
        # Check games table structure if it exists
        if 'games' in tables:
            cursor.execute("PRAGMA table_info(games)")
            columns = cursor.fetchall()
            logger.info("Games table columns:")
            for col in columns:
                logger.info(f"  {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error checking database structure: {e}")
        return False

def get_week10_games():
    """Get Week 10 games from database"""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # Try different possible table names and column structures
        possible_queries = [
            "SELECT * FROM games WHERE week = 10",
            "SELECT * FROM games WHERE week = '10'",
            "SELECT * FROM nfl_games WHERE week = 10",
            "SELECT * FROM game_data WHERE week = 10"
        ]
        
        for query in possible_queries:
            try:
                cursor.execute(query)
                games = cursor.fetchall()
                if games:
                    # Get column names
                    cursor.execute(query + " LIMIT 1")
                    columns = [description[0] for description in cursor.description]
                    logger.info(f"Found {len(games)} Week 10 games using query: {query}")
                    logger.info(f"Columns: {columns}")
                    
                    # Display first few games
                    for i, game in enumerate(games[:3]):
                        logger.info(f"Game {i+1}: {dict(zip(columns, game))}")
                    
                    conn.close()
                    return games
                    
            except sqlite3.OperationalError as e:
                logger.debug(f"Query failed: {query} - {e}")
                continue
        
        logger.warning("No Week 10 games found with any query")
        conn.close()
        return []
        
    except Exception as e:
        logger.error(f"Error getting Week 10 games: {e}")
        return []

def force_score_update():
    """Force a score update using the score_updater module"""
    try:
        # Try to import and run the score updater
        import sys
        sys.path.append('.')
        
        logger.info("Attempting to force score update...")
        
        # Try different approaches
        try:
            from score_updater import update_scores
            result = update_scores()
            logger.info(f"Score update result: {result}")
        except ImportError:
            logger.info("score_updater module not found, trying alternative...")
            
        # Alternative: trigger the background updater
        try:
            from background_updater import BackgroundUpdater
            updater = BackgroundUpdater()
            updater.update_games()
            logger.info("Background updater triggered successfully")
        except ImportError:
            logger.info("background_updater module not found")
            
        return True
        
    except Exception as e:
        logger.error(f"Error forcing score update: {e}")
        return False

def get_espn_scores_directly():
    """Get scores directly from ESPN API"""
    try:
        logger.info("Fetching scores directly from ESPN API...")
        
        # ESPN API endpoints for Week 10, 2025
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        
        # Try current week
        response = requests.get(espn_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            games = data.get('events', [])
            logger.info(f"Found {len(games)} games from ESPN API")
            
            # Display game info
            for i, game in enumerate(games[:5]):
                try:
                    competitions = game.get('competitions', [])
                    if competitions:
                        comp = competitions[0]
                        competitors = comp.get('competitors', [])
                        if len(competitors) >= 2:
                            away_team = competitors[0].get('team', {}).get('displayName', 'Unknown')
                            home_team = competitors[1].get('team', {}).get('displayName', 'Unknown')
                            away_score = competitors[0].get('score', '0')
                            home_score = competitors[1].get('score', '0')
                            status = comp.get('status', {}).get('type', {}).get('name', 'Unknown')
                            
                            logger.info(f"ESPN Game {i+1}: {away_team} @ {home_team} | {away_score}-{home_score} | {status}")
                            
                except Exception as e:
                    logger.error(f"Error parsing ESPN game {i+1}: {e}")
            
            return games
            
    except Exception as e:
        logger.error(f"Error getting ESPN scores: {e}")
        return []

def main():
    """Main function to diagnose and fix Monday scoring issues"""
    logger.info("🏈 MONDAY NIGHT FOOTBALL SCORE FIX")
    logger.info("=" * 50)
    
    # 1. Check database structure
    logger.info("1. Checking database structure...")
    if not check_database_structure():
        logger.error("Failed to check database structure")
        return
    
    # 2. Get Week 10 games from database
    logger.info("\n2. Getting Week 10 games from database...")
    games = get_week10_games()
    
    # 3. Force score update
    logger.info("\n3. Forcing score update...")
    force_score_update()
    
    # 4. Get ESPN scores directly
    logger.info("\n4. Getting ESPN scores directly...")
    espn_games = get_espn_scores_directly()
    
    # 5. Summary
    logger.info("\n🎯 DIAGNOSIS SUMMARY:")
    logger.info(f"✅ Database games found: {len(games)}")
    logger.info(f"✅ ESPN games retrieved: {len(espn_games)}")
    
    if len(games) == 0:
        logger.warning("⚠️ No games found in database - check database structure")
    
    if len(espn_games) == 0:
        logger.warning("⚠️ No ESPN games retrieved - check API connection")
    
    logger.info("\n📋 NEXT STEPS:")
    logger.info("1. Restart Flask server to see updated scores")
    logger.info("2. Check games page for Monday Night Football scores")
    logger.info("3. Verify team logos and betting odds display")

if __name__ == "__main__":
    main()