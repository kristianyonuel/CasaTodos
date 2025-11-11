import sqlite3

def fix_vizca_mnf_scoring():
    """Fix VIZCA's Monday Night Football scoring - he correctly picked Cardinals"""
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    print("Fixing VIZCA's Monday Night Football scoring...")
    print("=" * 50)
    
    # Find the Cowboys vs Cardinals game
    cursor.execute("""
        SELECT game_id, home_team, away_team, home_score, away_score
        FROM nfl_games 
        WHERE home_team = 'Dallas Cowboys' AND away_team = 'Arizona Cardinals' AND week = 9
    """)
    
    game = cursor.fetchone()
    if game:
        game_id, home_team, away_team, home_score, away_score = game
        winner = away_team if away_score > home_score else home_team
        
        print(f"Game {game_id}: {away_team} @ {home_team} ({away_score}-{home_score})")
        print(f"Winner: {winner}")
        
        # Check VIZCA's current pick
        cursor.execute("""
            SELECT selected_team, is_correct
            FROM user_picks 
            WHERE user_id = 9 AND game_id = ?
        """, (game_id,))
        
        pick = cursor.fetchone()
        if pick:
            selected_team, is_correct = pick
            print(f"VIZCA picked: {selected_team}")
            print(f"Current is_correct: {is_correct}")
            
            # If VIZCA picked the winner but is_correct is wrong, fix it
            if selected_team == winner and not is_correct:
                print("🔧 Updating VIZCA's pick to CORRECT...")
                
                cursor.execute("""
                    UPDATE user_picks 
                    SET is_correct = 1
                    WHERE user_id = 9 AND game_id = ?
                """, (game_id,))
                
                conn.commit()
                print("✅ Fixed! VIZCA now gets credit for picking Arizona Cardinals")
                
            elif selected_team == winner and is_correct:
                print("✅ Already correct - no change needed")
                
            else:
                print(f"❌ VIZCA picked {selected_team}, winner was {winner}")
    
    # Check updated leaderboard
    cursor.execute("""
        SELECT 
            u.username,
            COUNT(CASE WHEN up.is_correct = 1 THEN 1 END) as correct_picks
        FROM users u
        LEFT JOIN user_picks up ON u.id = up.user_id
        LEFT JOIN nfl_games ng ON up.game_id = ng.game_id
        WHERE ng.week = 9 AND u.username IN ('jean', 'vizca')
        GROUP BY u.id, u.username
        ORDER BY correct_picks DESC
    """)
    
    scores = cursor.fetchall()
    print('\nUpdated Week 9 Leaders:')
    print("=" * 25)
    for username, correct in scores:
        print(f'{username.upper()}: {correct}/14')
    
    # Check if they're tied
    if len(scores) == 2 and scores[0][1] == scores[1][1]:
        print(f'\n🎯 JEAN and VIZCA are now TIED at {scores[0][1]}/14!')
    
    conn.close()

if __name__ == '__main__':
    fix_vizca_mnf_scoring()