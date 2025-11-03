#!/usr/bin/env python3
"""
Manual fix for the background updater score update issue
The enhanced_background_updater.py is calling update_live_scores_espn() without the required 'week' parameter
"""

import sqlite3
import requests
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_week():
    """Determine the current NFL week based on games"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get the week that has recent games (last 3 days)
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT DISTINCT week 
        FROM nfl_games 
        WHERE game_date >= ? 
        ORDER BY week DESC 
        LIMIT 1
    """, (three_days_ago,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 9  # Default to week 9

def update_live_scores_espn(week):
    """Updated version with week parameter"""
    logger.info(f"🏈 Updating live scores for Week {week}")
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    try:
        # ESPN API endpoint for NFL scores
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week={week}&seasontype=2&year=2025"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        games_updated = 0
        
        if 'events' not in data:
            logger.warning("No events found in ESPN response")
            return 0
        
        for event in data['events']:
            if 'competitions' not in event or not event['competitions']:
                continue
                
            competition = event['competitions'][0]
            
            # Get team names and scores
            if 'competitors' not in competition or len(competition['competitors']) != 2:
                continue
            
            home_team = competition['competitors'][0]
            away_team = competition['competitors'][1]
            
            home_name = home_team['team']['displayName']
            away_name = away_team['team']['displayName']
            
            # Get scores
            home_score = int(home_team['score']) if home_team['score'].isdigit() else 0
            away_score = int(away_team['score']) if away_team['score'].isdigit() else 0
            
            # Get game status
            status = competition['status']['type']['name']
            is_final = status.lower() in ['final', 'final/ot']
            
            # Update database
            cursor.execute("""
                UPDATE nfl_games 
                SET home_score = ?, away_score = ?, game_status = ?, is_final = ?
                WHERE week = ? AND (
                    (home_team LIKE ? OR home_team LIKE ?) AND 
                    (away_team LIKE ? OR away_team LIKE ?)
                )
            """, (
                home_score, away_score, status, is_final, week,
                f'%{home_name.split()[-1]}%', f'%{home_name}%',
                f'%{away_name.split()[-1]}%', f'%{away_name}%'
            ))
            
            if cursor.rowcount > 0:
                games_updated += 1
                logger.info(f"✅ Updated: {away_name} @ {home_name} ({away_score}-{home_score}) - {status}")
        
        conn.commit()
        logger.info(f"🎯 Updated {games_updated} games for Week {week}")
        
        # Score picks for completed games
        if games_updated > 0:
            score_completed_picks(week)
        
        return games_updated
        
    except Exception as e:
        logger.error(f"❌ Error updating ESPN scores: {e}")
        return 0
    finally:
        conn.close()

def score_completed_picks(week):
    """Score picks for completed games"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    try:
        # Get completed games that haven't been scored
        cursor.execute("""
            SELECT game_id, home_team, away_team, home_score, away_score
            FROM nfl_games
            WHERE week = ? AND is_final = 1 AND home_score IS NOT NULL AND away_score IS NOT NULL
        """, (week,))
        
        completed_games = cursor.fetchall()
        picks_scored = 0
        
        for game_id, home_team, away_team, home_score, away_score in completed_games:
            # Determine winner
            if home_score > away_score:
                winner = home_team
            elif away_score > home_score:
                winner = away_team
            else:
                winner = None  # Tie
            
            # Update picks for this game
            if winner:
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
                """, (winner, winner, game_id))
                
                picks_scored += cursor.rowcount
                logger.info(f"🎯 Scored picks for {away_team} @ {home_team} (Winner: {winner})")
        
        conn.commit()
        logger.info(f"✅ Scored {picks_scored} picks for Week {week}")
        
    except Exception as e:
        logger.error(f"❌ Error scoring picks: {e}")
    finally:
        conn.close()

def main():
    """Main function to run the score update"""
    print("🔧 MANUAL SCORE UPDATE FIX")
    print("=" * 40)
    
    # Get current week
    current_week = get_current_week()
    print(f"📅 Current week: {current_week}")
    
    # Update scores
    games_updated = update_live_scores_espn(current_week)
    
    if games_updated > 0:
        print(f"✅ Successfully updated {games_updated} games")
        
        # Check leaderboard after updates
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.username, 
                   COUNT(up.id) as picks,
                   SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                   SUM(up.points_earned) as points
            FROM users u
            JOIN user_picks up ON u.id = up.user_id
            JOIN nfl_games g ON up.game_id = g.game_id
            WHERE g.week = ?
            GROUP BY u.username
            ORDER BY points DESC, correct DESC
            LIMIT 5
        """, (current_week,))
        
        results = cursor.fetchall()
        print(f"\n🏆 TOP 5 LEADERBOARD (Week {current_week}):")
        for i, (username, picks, correct, points) in enumerate(results, 1):
            print(f"   {i}. {username}: {correct}/{picks} correct ({points} pts)")
        
        conn.close()
    else:
        print("❌ No games were updated")

if __name__ == "__main__":
    main()