-- SQL to help debug and fix weekly leaderboard issues
-- Use this to manually check and update game status if needed

-- 1. Check current games status for week 4, 2025
SELECT 
    game_id,
    away_team || ' @ ' || home_team as matchup,
    game_date,
    is_final,
    CASE 
        WHEN game_date < datetime('now') THEN 'Past Deadline'
        ELSE 'Future'
    END as deadline_status,
    CASE 
        WHEN game_date < datetime('now') OR is_final = 1 THEN 'Available for Leaderboard'
        ELSE 'Not Available'
    END as leaderboard_status,
    home_score || '-' || away_score as final_score
FROM nfl_games 
WHERE week = 4 AND year = 2025
ORDER BY game_date;

-- 2. Check if any picks exist for the week
SELECT COUNT(*) as total_picks
FROM user_picks p
JOIN nfl_games g ON p.game_id = g.id
WHERE g.week = 4 AND g.year = 2025;

-- 3. Check scoring status
SELECT 
    COUNT(*) as total_picks,
    SUM(CASE WHEN is_correct IS NOT NULL THEN 1 ELSE 0 END) as scored_picks,
    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_picks
FROM user_picks p
JOIN nfl_games g ON p.game_id = g.id
WHERE g.week = 4 AND g.year = 2025;

-- 4. MANUAL FIX: If games are completed but not marked as final, use this:
-- (Uncomment and modify as needed)
/*
UPDATE nfl_games 
SET is_final = 1 
WHERE week = 4 AND year = 2025 
  AND home_score IS NOT NULL 
  AND away_score IS NOT NULL;
*/

-- 5. MANUAL FIX: If you need to mark specific games as final:
-- (Replace game_id with actual game ID)
/*
UPDATE nfl_games 
SET is_final = 1, 
    home_score = 24, 
    away_score = 17 
WHERE game_id = 'REPLACE_WITH_ACTUAL_GAME_ID';
*/

-- 6. Check Monday Night Football game specifically
SELECT 
    game_id,
    away_team || ' @ ' || home_team as matchup,
    game_date,
    is_final,
    is_monday_night,
    strftime('%w', game_date) as day_of_week -- 1 = Monday
FROM nfl_games 
WHERE week = 4 AND year = 2025
  AND (is_monday_night = 1 OR strftime('%w', game_date) = '1')
ORDER BY game_date;

-- 7. Force trigger scoring update for completed games:
-- This will recalculate is_correct for all picks where games are final
/*
UPDATE user_picks 
SET is_correct = (
    CASE 
        WHEN g.home_score > g.away_score AND p.selected_team = g.home_team THEN 1
        WHEN g.away_score > g.home_score AND p.selected_team = g.away_team THEN 1
        ELSE 0
    END
)
FROM nfl_games g 
WHERE user_picks.game_id = g.game_id 
  AND g.is_final = 1 
  AND g.week = 4 
  AND g.year = 2025;
*/