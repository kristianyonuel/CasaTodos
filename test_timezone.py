#!/usr/bin/env python3
"""
Test timezone conversion for the early game
"""

from datetime import datetime
import pytz

# Test timezone conversion
est_tz = pytz.timezone('US/Eastern')
ast_tz = pytz.timezone('America/Puerto_Rico')

# Create 9:30 AM EST Sunday
game_time_est = est_tz.localize(datetime(2025, 10, 12, 9, 30))
game_time_ast = game_time_est.astimezone(ast_tz)

print('Timezone Conversion Test:')
print(f'EST: {game_time_est.strftime("%a %m/%d %I:%M %p %Z")}')
print(f'AST: {game_time_ast.strftime("%a %m/%d %I:%M %p %Z")}')

# Check the offset
print(f'EST offset: {game_time_est.strftime("%z")}')
print(f'AST offset: {game_time_ast.strftime("%z")}')

# This should be a London game (international)
print()
print('This is likely the NFL London game!')
print('London games typically start 9:30 AM EST / 6:30 AM AST')

# Check if the database has the wrong timezone
print()
print('Database Check:')
print('If database shows 9:30 AM AST, the timezone is wrong in the database.')
print('It should be stored as UTC or with proper timezone info.')