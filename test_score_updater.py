#!/usr/bin/env python3
"""Test the NFL Score Updater"""

from score_updater import NFLScoreUpdater

print('🏈 Testing NFL Score Updater')
print('=' * 50)

updater = NFLScoreUpdater()

# Test fetching current scores
print('📡 Fetching current week scores...')
scores = updater.fetch_current_week_scores(year=2025, week=2)

print(f'📊 Found {len(scores)} games:')
for game_key, game_data in scores.items():
    status = 'Final' if game_data['is_final'] else game_data['game_status']
    print(f'  {game_key}: {game_data["away_score"]}-{game_data["home_score"]} ({status})')

if scores:
    # Test updating database
    print('\n🔄 Testing database update...')
    updated_count = updater.update_game_scores(scores)
    print(f'✅ Updated {updated_count} games in database')

    # Get summary
    print('\n📋 Current scores summary:')
    summary = updater.get_latest_scores_summary()
    if 'error' not in summary:
        print(f'📊 Recent games: {summary["total_recent_games"]}')
        print(f'✅ Completed: {summary["completed_games"]}')
        print(f'⏳ Pending: {summary["pending_games"]}')
        
        print('\n🎯 Latest games:')
        for game in summary['games'][:5]:
            status = '✅' if game['is_final'] else '⏳'
            print(f'  {status} Week {game["week"]}: {game["matchup"]} - {game["score"]} ({game["status"]})')
    else:
        print(f'❌ Error: {summary["error"]}')
else:
    print('❌ No scores data retrieved from ESPN API')
