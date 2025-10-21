#!/usr/bin/env python3
"""
Test timezone differences for the early Sunday game
"""

from datetime import datetime
import pytz

# Let's check various timezones that might be relevant
timezones = [
    ('US/Eastern', 'Eastern Time'),
    ('America/Puerto_Rico', 'Puerto Rico (AST)'),
    ('UTC', 'UTC'),
]

# 9:30 AM EST on Oct 12, 2025
base_time = datetime(2025, 10, 12, 9, 30)

print('9:30 AM on Sunday Oct 12, 2025 in different timezones:')
print('=' * 55)

for tz_name, tz_desc in timezones:
    tz = pytz.timezone(tz_name)
    if tz_name == 'UTC':
        # For UTC, create UTC time directly
        localized_time = pytz.utc.localize(base_time)
    else:
        # For others, localize to that timezone
        localized_time = tz.localize(base_time)
    
    print(f'{tz_desc:20}: {localized_time.strftime("%I:%M %p %Z")} (offset: {localized_time.strftime("%z")})')

print()
print('Key Points:')
print('- This is likely the NFL London International Series game')
print('- London games start 9:30 AM ET / 2:30 PM London time')
print('- During October, Puerto Rico AST = US Eastern Daylight Time')
print('- Both are UTC-4 in October 2025')
print()

# Check if the user meant standard time vs daylight time
print('If you meant 5:30 AM, that would be:')
print('- 5:30 AM AST = 5:30 AM EDT (no difference in October)')
print('- Maybe the game time in database is wrong?')

# Let's see what time would make it 5:30 AM in your location
print()
print('To have game at 5:30 AM in your timezone:')
if_530_local = datetime(2025, 10, 12, 5, 30)
ast_tz = pytz.timezone('America/Puerto_Rico')
local_530 = ast_tz.localize(if_530_local)
utc_530 = local_530.astimezone(pytz.UTC)
et_530 = local_530.astimezone(pytz.timezone('US/Eastern'))

print(f'5:30 AM AST = {et_530.strftime("%I:%M %p")} ET = {utc_530.strftime("%I:%M %p")} UTC')