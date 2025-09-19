from espn_api_service import ESPNAPIService

espn = ESPNAPIService()
games = espn.get_week_games(3, 2025)

for game in games:
    teams = [game.get('away_team'), game.get('home_team')]
    if 'MIA' in teams or 'BUF' in teams:
        print('Buffalo game after ESPN fix:')
        away = game.get('away_team')
        home = game.get('home_team')
        away_score = game.get('away_score')
        home_score = game.get('home_score')
        status = game.get('game_status')
        is_final = game.get('is_final')
        
        print(f'  {away} {away_score} - {home} {home_score}')
        print(f'  Status: {status}')
        print(f'  Is Final: {is_final}')
        break
