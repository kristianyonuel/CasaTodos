import pytz
from datetime import datetime

print('=== DAYLIGHT SAVING TIME ANALYSIS ===')

# Test dates before and after DST ends
before_dst = datetime(2025, 10, 20, 20, 15)  # Week 7 (October)
after_dst = datetime(2025, 11, 10, 20, 15)   # Week 10 (November)

et_tz = pytz.timezone('US/Eastern')

# Before DST ends (EDT)
edt_time = et_tz.localize(before_dst)
print(f'Before DST ends (October 20):')
print(f'  {edt_time}')
print(f'  UTC offset: {edt_time.strftime("%z")}')
print(f'  AST equivalent: UTC-4 = SAME TIME as EDT')

# After DST ends (EST)  
est_time = et_tz.localize(after_dst)
print(f'\nAfter DST ends (November 10):')
print(f'  {est_time}')
print(f'  UTC offset: {est_time.strftime("%z")}')
print(f'  AST equivalent: UTC-4 = 1 HOUR AHEAD of EST')

# Convert to AST
from datetime import timezone, timedelta
ast_tz = timezone(timedelta(hours=-4))

edt_to_ast = edt_time.astimezone(ast_tz)
est_to_ast = est_time.astimezone(ast_tz)

print(f'\n=== TIME CONVERSIONS ===')
print(f'October (EDT): {edt_time.strftime("%I:%M %p")} EDT → {edt_to_ast.strftime("%I:%M %p")} AST')
print(f'November (EST): {est_time.strftime("%I:%M %p")} EST → {est_to_ast.strftime("%I:%M %p")} AST')

print(f'\n📅 DST ends: November 3, 2025 (first Sunday)')
print(f'💡 Current MNF games (Week 7) show same time: 8:15 PM EDT = 8:15 PM AST')
print(f'🔄 Later season MNF games: 8:15 PM EST = 9:15 PM AST')