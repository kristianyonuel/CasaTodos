-- Fix Week 1 picks with correct game IDs and Monday Night scores
-- First, delete all existing picks to avoid duplicates
DELETE FROM user_picks WHERE game_id IN (
    SELECT id FROM nfl_games WHERE week = 1 AND year = 2025
);

-- Get correct game IDs and insert picks with Monday Night scores
INSERT INTO user_picks (user_id, game_id, selected_team, predicted_home_score, predicted_away_score, created_at)
SELECT 
    u.id as user_id,
    g.id as game_id,
    CASE 
        WHEN g.away_team = 'DAL' AND g.home_team = 'PHI' THEN 
            CASE u.username 
                WHEN 'javier' THEN 'DAL' WHEN 'vizca' THEN 'PHI' WHEN 'robert' THEN 'PHI' 
                WHEN 'coyote' THEN 'PHI' WHEN 'jean' THEN 'PHI' WHEN 'ramfis' THEN 'PHI'
                WHEN 'guillermo' THEN 'PHI' WHEN 'joniel' THEN 'PHI' WHEN 'rada' THEN 'PHI'
                WHEN 'raymond' THEN 'PHI' WHEN 'shorty' THEN 'PHI' WHEN 'kristian' THEN 'DAL'
                WHEN 'fer' THEN 'DAL' 
            END
        WHEN g.away_team = 'KC' AND g.home_team = 'LAC' THEN 
            CASE u.username 
                WHEN 'javier' THEN 'KC' WHEN 'vizca' THEN 'LAC' WHEN 'robert' THEN 'KC' 
                WHEN 'coyote' THEN 'KC' WHEN 'jean' THEN 'KC' WHEN 'ramfis' THEN 'KC'
                WHEN 'guillermo' THEN 'KC' WHEN 'joniel' THEN 'KC' WHEN 'rada' THEN 'KC'
                WHEN 'raymond' THEN 'LAC' WHEN 'shorty' THEN 'LAC' WHEN 'kristian' THEN 'KC'
                WHEN 'fer' THEN 'KC' 
            END
        WHEN g.away_team = 'PIT' AND g.home_team = 'NYJ' THEN 
            CASE u.username 
                WHEN 'javier' THEN 'PIT' WHEN 'vizca' THEN 'PIT' WHEN 'robert' THEN 'PIT' 
                WHEN 'coyote' THEN 'PIT' WHEN 'jean' THEN 'PIT' WHEN 'ramfis' THEN 'PIT'
                WHEN 'guillermo' THEN 'PIT' WHEN 'joniel' THEN 'PIT' WHEN 'rada' THEN 'PIT'
                WHEN 'raymond' THEN 'PIT' WHEN 'shorty' THEN 'PIT' WHEN 'kristian' THEN 'PIT'
                WHEN 'fer' THEN 'PIT' 
            END
        WHEN g.away_team = 'CAR' AND g.home_team = 'JAX' THEN 
            CASE u.username 
                WHEN 'javier' THEN 'JAX' WHEN 'vizca' THEN 'JAX' WHEN 'robert' THEN 'JAX' 
                WHEN 'coyote' THEN 'JAX' WHEN 'jean' THEN 'CAR' WHEN 'ramfis' THEN 'JAX'
                WHEN 'guillermo' THEN 'CAR' WHEN 'joniel' THEN 'JAX' WHEN 'rada' THEN 'JAX'
                WHEN 'raymond' THEN 'JAX' WHEN 'shorty' THEN 'JAX' WHEN 'kristian' THEN 'JAX'
                WHEN 'fer' THEN 'JAX' 
            END
        WHEN g.away_team = 'TB' AND g.home_team = 'ATL' THEN 
            CASE u.username 
                WHEN 'javier' THEN 'TB' WHEN 'vizca' THEN 'ATL' WHEN 'robert' THEN 'TB' 
                WHEN 'coyote' THEN 'ATL' WHEN 'jean' THEN 'TB' WHEN 'ramfis' THEN 'TB'
                WHEN 'guillermo' THEN 'TB' WHEN 'joniel' THEN 'TB' WHEN 'rada' THEN 'TB'
                WHEN 'raymond' THEN 'TB' WHEN 'shorty' THEN 'ATL' WHEN 'kristian' THEN 'TB'
                WHEN 'fer' THEN 'TB' 
            END
        WHEN g.away_team = 'CIN' AND g.home_team = 'CLE' THEN 'CIN'  -- All picked CIN
        WHEN g.away_team = 'MIA' AND g.home_team = 'IND' THEN 
            CASE u.username 
                WHEN 'javier' THEN 'IND' WHEN 'vizca' THEN 'MIA' WHEN 'robert' THEN 'IND' 
                WHEN 'coyote' THEN 'MIA' WHEN 'jean' THEN 'MIA' WHEN 'ramfis' THEN 'MIA'
                WHEN 'guillermo' THEN 'MIA' WHEN 'joniel' THEN 'MIA' WHEN 'rada' THEN 'MIA'
                WHEN 'raymond' THEN 'MIA' WHEN 'shorty' THEN 'MIA' WHEN 'kristian' THEN 'MIA'
                WHEN 'fer' THEN 'MIA' 
            END
        WHEN g.away_team = 'LV' AND g.home_team = 'NE' THEN 
            CASE u.username 
                WHEN 'javier' THEN 'LV' WHEN 'vizca' THEN 'NE' WHEN 'robert' THEN 'NE' 
                WHEN 'coyote' THEN 'LV' WHEN 'jean' THEN 'NE' WHEN 'ramfis' THEN 'NE'
                WHEN 'guillermo' THEN 'NE' WHEN 'joniel' THEN 'NE' WHEN 'rada' THEN 'NE'
                WHEN 'raymond' THEN 'LV' WHEN 'shorty' THEN 'NE' WHEN 'kristian' THEN 'NE'
                WHEN 'fer' THEN 'NE' 
            END
        WHEN g.away_team = 'ARI' AND g.home_team = 'NO' THEN 
            CASE u.username 
                WHEN 'fer' THEN 'NO'
                ELSE 'ARI'  -- All others picked ARI
            END
        WHEN g.away_team = 'NYG' AND g.home_team = 'WSH' THEN 
            CASE u.username 
                WHEN 'fer' THEN 'NYG'
                ELSE 'WSH'  -- All others picked WSH (WAS in data)
            END
        WHEN g.away_team = 'TEN' AND g.home_team = 'DEN' THEN 
            CASE u.username 
                WHEN 'fer' THEN 'TEN'
                ELSE 'DEN'  -- All others picked DEN
            END
        WHEN g.away_team = 'SF' AND g.home_team = 'SEA' THEN 
            CASE u.username 
                WHEN 'robert' THEN 'SEA' WHEN 'raymond' THEN 'SEA' WHEN 'shorty' THEN 'SEA'
                WHEN 'fer' THEN 'SEA'
                ELSE 'SF'  -- Others picked SF
            END
        WHEN g.away_team = 'DET' AND g.home_team = 'GB' THEN 
            CASE u.username 
                WHEN 'vizca' THEN 'GB' WHEN 'robert' THEN 'GB' WHEN 'coyote' THEN 'GB' 
                WHEN 'ramfis' THEN 'GB' WHEN 'rada' THEN 'GB' WHEN 'raymond' THEN 'GB'
                WHEN 'shorty' THEN 'GB' WHEN 'kristian' THEN 'GB'
                ELSE 'DET'  -- jean, guillermo, joniel picked DET
            END
        WHEN g.away_team = 'HOU' AND g.home_team = 'LAR' THEN 
            CASE u.username 
                WHEN 'robert' THEN 'HOU' WHEN 'guillermo' THEN 'HOU' WHEN 'raymond' THEN 'HOU'
                ELSE 'LAR'  -- Others picked LAR
            END
        WHEN g.away_team = 'BAL' AND g.home_team = 'BUF' THEN 
            CASE u.username 
                WHEN 'coyote' THEN 'BUF' WHEN 'ramfis' THEN 'BUF' WHEN 'guillermo' THEN 'BUF'
                WHEN 'vizca' THEN 'BUF' WHEN 'raymond' THEN 'BUF' WHEN 'fer' THEN 'BUF'
                ELSE 'BAL'  -- Others picked BAL
            END
        WHEN g.away_team = 'MIN' AND g.home_team = 'CHI' THEN 
            CASE u.username 
                WHEN 'jean' THEN 'CHI' WHEN 'ramfis' THEN 'CHI' WHEN 'joniel' THEN 'CHI'
                WHEN 'rada' THEN 'CHI' WHEN 'shorty' THEN 'CHI' WHEN 'kristian' THEN 'CHI'
                WHEN 'fer' THEN 'CHI'
                ELSE 'MIN'  -- Others picked MIN
            END
    END as selected_team,
    CASE u.username 
        WHEN 'javier' THEN 24 WHEN 'vizca' THEN 24 WHEN 'robert' THEN 28 WHEN 'coyote' THEN 27
        WHEN 'jean' THEN 24 WHEN 'ramfis' THEN 22 WHEN 'guillermo' THEN 28 WHEN 'joniel' THEN 26
        WHEN 'rada' THEN 20 WHEN 'raymond' THEN 25 WHEN 'shorty' THEN 35 WHEN 'kristian' THEN 20
        WHEN 'fer' THEN 28
    END as predicted_home_score,
    CASE u.username 
        WHEN 'javier' THEN 10 WHEN 'vizca' THEN 17 WHEN 'robert' THEN 21 WHEN 'coyote' THEN 21
        WHEN 'jean' THEN 20 WHEN 'ramfis' THEN 19 WHEN 'guillermo' THEN 10 WHEN 'joniel' THEN 22
        WHEN 'rada' THEN 14 WHEN 'raymond' THEN 21 WHEN 'shorty' THEN 24 WHEN 'kristian' THEN 13
        WHEN 'fer' THEN 24
    END as predicted_away_score,
    datetime('now') as created_at
FROM users u
CROSS JOIN nfl_games g
WHERE u.is_admin = 0 
AND g.week = 1 
AND g.year = 2025;
