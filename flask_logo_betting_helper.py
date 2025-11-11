
# ADD THIS TO YOUR FLASK APP.PY FILE

def get_team_logos_and_betting(games):
    """
    Enhance games list with team logos and betting information
    Call this function before rendering templates
    """
    import sqlite3
    
    enhanced_games = []
    
    # Get team logo mapping
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    # Get all team info for logos
    cursor.execute('SELECT team_name, team_code, logo_url FROM team_info')
    team_logos = {}
    for team_name, team_code, logo_url in cursor.fetchall():
        team_logos[team_name] = logo_url
    
    conn.close()
    
    for game in games:
        # Add logo URLs to game object
        game.away_team_logo = team_logos.get(game.away_team)
        game.home_team_logo = team_logos.get(game.home_team)
        enhanced_games.append(game)
    
    return enhanced_games

# EXAMPLE USAGE IN YOUR FLASK ROUTES:

@app.route('/games')
def games():
    # ... your existing game query logic ...
    games = get_week_games(current_week)  # Your existing function
    
    # Enhance with logos and betting
    enhanced_games = get_team_logos_and_betting(games)
    
    return render_template('games.html', 
                         games=enhanced_games, 
                         current_week=current_week)

# UPDATE YOUR DATABASE QUERY TO INCLUDE BETTING FIELDS:

def get_week_games(week):
    """Updated to include betting information"""
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    query = """
    SELECT g.*, 
           g.spread_line, g.spread_favorite, g.over_under,
           g.moneyline_home, g.moneyline_away, g.betting_updated,
           p.team_picked as user_pick
    FROM nfl_games g
    LEFT JOIN user_picks p ON g.game_id = p.game_id 
                           AND p.user_id = %s
    WHERE g.week = ? AND g.year = 2025
    ORDER BY g.game_date, g.game_time
    """
    
    user_id = session.get('user_id') if 'session' in globals() else None
    cursor.execute(query, (user_id, week))
    
    games = cursor.fetchall()
    conn.close()
    
    return games
