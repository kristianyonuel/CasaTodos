import sqlite3

def update_week_1_pfr_scores():
    """Update Week 1 with scores extracted from Pro Football Reference data"""
    
    # Week 1 scores from PFR data with correct abbreviations
    week_1_scores = [
        # Sep 4, 2025: Dallas Cowboys @ Philadelphia Eagles (DAL 20, PHI 24)
        {"away_team": "DAL", "home_team": "PHI", "away_score": 20, "home_score": 24},
        
        # Sep 5, 2025: Kansas City Chiefs @ Los Angeles Chargers (KC 21, LAC 27)
        {"away_team": "KC", "home_team": "LAC", "away_score": 21, "home_score": 27},
        
        # Sep 7, 2025: Pittsburgh Steelers @ New York Jets (PIT 34, NYJ 32)
        {"away_team": "PIT", "home_team": "NYJ", "away_score": 34, "home_score": 32},
        
        # Sep 7, 2025: Carolina Panthers @ Jacksonville Jaguars (CAR 10, JAX 26)
        {"away_team": "CAR", "home_team": "JAX", "away_score": 10, "home_score": 26},
        
        # Sep 7, 2025: Tampa Bay Buccaneers @ Atlanta Falcons (Need to determine)
        # Let's check what games we have vs what scores we extracted...
        
        # Sep 7, 2025: Cincinnati Bengals @ Cleveland Browns (CIN 17, CLE 16)
        {"away_team": "CIN", "home_team": "CLE", "away_score": 17, "home_score": 16},
        
        # Sep 7, 2025: Miami Dolphins @ Indianapolis Colts (MIA 8, IND 33)
        {"away_team": "MIA", "home_team": "IND", "away_score": 8, "home_score": 33},
        
        # Sep 7, 2025: Las Vegas Raiders @ New England Patriots (LV 20, NE 13)
        {"away_team": "LV", "home_team": "NE", "away_score": 20, "home_score": 13},
    ]
    
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    updated_count = 0
    
    try:
        print("🏈 UPDATING WEEK 1 SCORES FROM PRO FOOTBALL REFERENCE")
        print("=" * 55)
        
        for game in week_1_scores:
            # Find the game in database
            cursor.execute("""
                SELECT id FROM nfl_games 
                WHERE week = 1 AND away_team = ? AND home_team = ?
            """, (game['away_team'], game['home_team']))
            
            game_result = cursor.fetchone()
            if game_result:
                game_id = game_result[0]
                
                # Update game scores
                cursor.execute("""
                    UPDATE nfl_games 
                    SET away_score = ?, home_score = ?, 
                        game_status = 'Final', is_final = 1,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (game['away_score'], game['home_score'], game_id))
                
                # Determine winner
                if game['away_score'] > game['home_score']:
                    winning_team = game['away_team']
                elif game['home_score'] > game['away_score']:
                    winning_team = game['home_team']
                else:
                    winning_team = "TIE"
                
                # Update user picks - need to map abbreviations to full names for picks
                team_map = {
                    'DAL': 'Dallas Cowboys', 'PHI': 'Philadelphia Eagles',
                    'KC': 'Kansas City Chiefs', 'LAC': 'Los Angeles Chargers',
                    'PIT': 'Pittsburgh Steelers', 'NYJ': 'New York Jets',
                    'CAR': 'Carolina Panthers', 'JAX': 'Jacksonville Jaguars',
                    'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns',
                    'MIA': 'Miami Dolphins', 'IND': 'Indianapolis Colts',
                    'LV': 'Las Vegas Raiders', 'NE': 'New England Patriots'
                }
                
                winning_team_full = team_map.get(winning_team, winning_team)
                
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
                """, (winning_team_full, winning_team_full, game_id))
                
                updated_count += 1
                print(f"✅ {game['away_team']} @ {game['home_team']}: {game['away_score']}-{game['home_score']} (Winner: {winning_team_full})")
                
                # Show how many users picked correctly
                cursor.execute('SELECT COUNT(*) FROM user_picks WHERE game_id = ? AND is_correct = 1', (game_id,))
                correct_picks = cursor.fetchone()[0]
                print(f"   {correct_picks} users picked correctly")
            else:
                print(f"❌ Game not found: {game['away_team']} @ {game['home_team']}")
        
        conn.commit()
        
        # Show Week 1 leaderboard
        print(f"\n📊 WEEK 1 LEADERBOARD AFTER UPDATE:")
        print("=" * 35)
        
        cursor.execute("""
            SELECT u.username, 
                   SUM(CASE WHEN up.is_correct = 1 THEN 1 ELSE 0 END) as correct_picks,
                   COUNT(up.id) as total_picks
            FROM users u 
            LEFT JOIN user_picks up ON u.id = up.user_id 
                AND up.game_id IN (SELECT id FROM nfl_games WHERE week = 1 AND is_final = 1)
            GROUP BY u.id, u.username 
            ORDER BY correct_picks DESC, u.username
        """)
        
        leaderboard = cursor.fetchall()
        for username, correct, total in leaderboard:
            if total > 0:
                percentage = (correct / total) * 100
                print(f"{username:12}: {correct}/{total} correct ({percentage:.1f}%)")
            else:
                print(f"{username:12}: No picks in completed games")
        
        print(f"\n✅ Updated {updated_count} Week 1 games from Pro Football Reference!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error updating Week 1: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_week_1_pfr_scores()