import requests

url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
params = {'seasontype': 2, 'week': 3, 'year': 2025}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

try:
    response = requests.get(url, headers=headers, params=params, timeout=15, verify=False)
    data = response.json()
    
    events = data.get('events', [])
    
    for event in events:
        competitions = event.get('competitions', [])
        if competitions:
            competitors = competitions[0].get('competitors', [])
            teams = [c.get('team', {}).get('abbreviation') for c in competitors]
            
            if 'MIA' in teams and 'BUF' in teams:
                print('=== BUFFALO GAME RAW STATUS INFO ===')
                status = competitions[0].get('status', {})
                status_type = status.get('type', {})
                
                print(f'Status object: {status}')
                print(f'Status type: {status_type}')
                
                name = status_type.get('name', '')
                desc = status_type.get('description', '')
                completed = status_type.get('completed', False)
                
                print(f'Name: "{name}"')
                print(f'Description: "{desc}"')
                print(f'Completed: {completed}')
                
                # Test different final detection methods
                method1 = name.lower() in ['final', 'final/ot']
                method2 = desc.lower() == 'final'
                method3 = completed == True
                method4 = 'final' in name.lower()
                
                print(f'\nFinal detection methods:')
                print(f'  Method 1 (name in [final, final/ot]): {method1}')
                print(f'  Method 2 (description == final): {method2}')
                print(f'  Method 3 (completed == True): {method3}')
                print(f'  Method 4 (final in name): {method4}')
                
                break
                
except Exception as e:
    print(f'Error: {e}')
