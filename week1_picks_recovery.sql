-- NFL Fantasy Week 1 Picks Recovery Script
-- This script restores all user picks for Week 1, 2025

-- First, let's get the game IDs and user IDs we need
-- Games in order (from your data):
-- 1. DAL @ PHI
-- 2. KC @ LAC  
-- 3. TB @ ATL
-- 4. CIN @ CLE
-- 5. MIA @ IND
-- 6. CAR @ JAX (Note: JEAN picked CAR, others JAX)
-- 7. LV @ NE
-- 8. ARI @ NO (Note: FER picked NO)
-- 9. PIT @ NYJ
-- 10. NYG @ WAS (Note: WAS should be WSH in database)
-- 11. TEN @ DEN
-- 12. SF @ SEA
-- 13. DET @ GB
-- 14. HOU @ LAR
-- 15. BAL @ BUF
-- 16. MIN @ CHI

-- Delete any existing picks for Week 1 to avoid duplicates
DELETE FROM user_picks WHERE game_id IN (
    SELECT id FROM nfl_games WHERE week = 1 AND year = 2025
);

-- Insert picks for each user
-- JAVIER picks
INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, created_at)
SELECT 
    (SELECT id FROM users WHERE LOWER(username) = 'javier'),
    g.id,
    CASE 
        WHEN g.away_team = 'DAL' AND g.home_team = 'PHI' THEN 'DAL'
        WHEN g.away_team = 'KC' AND g.home_team = 'LAC' THEN 'KC'
        WHEN g.away_team = 'TB' AND g.home_team = 'ATL' THEN 'TB'
        WHEN g.away_team = 'CIN' AND g.home_team = 'CLE' THEN 'CIN'
        WHEN g.away_team = 'MIA' AND g.home_team = 'IND' THEN 'IND'
        WHEN g.away_team = 'CAR' AND g.home_team = 'JAX' THEN 'JAX'
        WHEN g.away_team = 'LV' AND g.home_team = 'NE' THEN 'LV'
        WHEN g.away_team = 'ARI' AND g.home_team = 'NO' THEN 'ARI'
        WHEN g.away_team = 'PIT' AND g.home_team = 'NYJ' THEN 'PIT'
        WHEN g.away_team = 'NYG' AND (g.home_team = 'WAS' OR g.home_team = 'WSH') THEN COALESCE(NULLIF(g.home_team, 'WAS'), 'WSH')
        WHEN g.away_team = 'TEN' AND g.home_team = 'DEN' THEN 'DEN'
        WHEN g.away_team = 'SF' AND g.home_team = 'SEA' THEN 'SF'
        WHEN g.away_team = 'DET' AND g.home_team = 'GB' THEN 'DET'
        WHEN g.away_team = 'HOU' AND g.home_team = 'LAR' THEN 'LAR'
        WHEN g.away_team = 'BAL' AND g.home_team = 'BUF' THEN 'BAL'
        WHEN g.away_team = 'MIN' AND g.home_team = 'CHI' THEN 'MIN'
    END,
    24, 10, -- Monday Night prediction 24-10
    datetime('now')
FROM nfl_games g
WHERE g.week = 1 AND g.year = 2025 AND g.is_monday_night = 1
UNION ALL
SELECT 
    (SELECT id FROM users WHERE LOWER(username) = 'javier'),
    g.id,
    CASE 
        WHEN g.away_team = 'DAL' AND g.home_team = 'PHI' THEN 'DAL'
        WHEN g.away_team = 'KC' AND g.home_team = 'LAC' THEN 'KC'
        WHEN g.away_team = 'TB' AND g.home_team = 'ATL' THEN 'TB'
        WHEN g.away_team = 'CIN' AND g.home_team = 'CLE' THEN 'CIN'
        WHEN g.away_team = 'MIA' AND g.home_team = 'IND' THEN 'IND'
        WHEN g.away_team = 'CAR' AND g.home_team = 'JAX' THEN 'JAX'
        WHEN g.away_team = 'LV' AND g.home_team = 'NE' THEN 'LV'
        WHEN g.away_team = 'ARI' AND g.home_team = 'NO' THEN 'ARI'
        WHEN g.away_team = 'PIT' AND g.home_team = 'NYJ' THEN 'PIT'
        WHEN g.away_team = 'NYG' AND (g.home_team = 'WAS' OR g.home_team = 'WSH') THEN COALESCE(NULLIF(g.home_team, 'WAS'), 'WSH')
        WHEN g.away_team = 'TEN' AND g.home_team = 'DEN' THEN 'DEN'
        WHEN g.away_team = 'SF' AND g.home_team = 'SEA' THEN 'SF'
        WHEN g.away_team = 'DET' AND g.home_team = 'GB' THEN 'DET'
        WHEN g.away_team = 'HOU' AND g.home_team = 'LAR' THEN 'LAR'
        WHEN g.away_team = 'BAL' AND g.home_team = 'BUF' THEN 'BAL'
        WHEN g.away_team = 'MIN' AND g.home_team = 'CHI' THEN 'MIN'
    END,
    NULL, NULL, -- Regular games don't need score predictions
    datetime('now')
FROM nfl_games g
WHERE g.week = 1 AND g.year = 2025 AND (g.is_monday_night = 0 OR g.is_monday_night IS NULL);
