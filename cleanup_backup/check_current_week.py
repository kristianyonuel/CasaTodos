from datetime import datetime

def calculate_current_week():
    try:
        from nfl_week_calculator import get_current_nfl_week
        current_week = get_current_nfl_week(2025)
        print(f'From nfl_week_calculator: Week {current_week}')
        return current_week
    except Exception as e:
        print(f'Error with nfl_week_calculator: {e}')
        # Fallback calculation (same as in app.py)
        current_date = datetime.now()
        season_start = datetime(2025, 9, 5)  # 2025 season start
        days_since_start = (current_date - season_start).days
        fallback_week = max(1, min(18, (days_since_start // 7) + 1))
        print(f'Fallback calculation: Week {fallback_week}')
        print(f'Current date: {current_date}')
        print(f'Days since season start: {days_since_start}')
        return fallback_week

if __name__ == '__main__':
    week = calculate_current_week()
    print(f'\nResult: Application should default to Week {week}')
