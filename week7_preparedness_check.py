#!/usr/bin/env python3
"""
Check Week 7 Preparedness
Verify that Week 7 will be automatically available on Tuesday
"""

from datetime import datetime, timedelta
import pytz
from nfl_week_calculator import get_current_nfl_week, get_calendar_week_with_boundaries
import sqlite3

print("🏈 Week 7 Preparedness Check")
print("=" * 40)

# Current status
est_tz = pytz.timezone('US/Eastern')
now = datetime.now(est_tz)
current_week = get_current_nfl_week()

print(f"Current time: {now}")
print(f"Current NFL week: {current_week}")
print()

# Test key dates
test_dates = [
    ("Monday Oct 14 (after MNF)", datetime(2025, 10, 14, 1, 0, 0, tzinfo=est_tz)),
    ("Tuesday Oct 15 6AM", datetime(2025, 10, 15, 6, 0, 0, tzinfo=est_tz)),
    ("Tuesday Oct 15 10AM", datetime(2025, 10, 15, 10, 0, 0, tzinfo=est_tz)),
    ("Wednesday Oct 15 2PM", datetime(2025, 10, 15, 14, 0, 0, tzinfo=est_tz)),
    ("Thursday Oct 16", datetime(2025, 10, 16, 10, 0, 0, tzinfo=est_tz)),
]

print("📅 Week Calculator Tests:")
for desc, test_date in test_dates:
    week = get_calendar_week_with_boundaries(test_date)
    print(f"  {desc}: Week {week}")
print()

# Check database status
print("💾 Database Status:")
try:
    conn = sqlite3.connect('nfl_fantasy.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT week, COUNT(*) as games FROM nfl_games WHERE year = 2025 GROUP BY week ORDER BY week')
    weeks = cursor.fetchall()
    
    for week, count in weeks:
        status = "✅" if count > 0 else "❌"
        print(f"  Week {week}: {status} {count} games")
    
    # Check if Week 7 exists
    week_7_exists = any(week == 7 for week, _ in weeks)
    print()
    if week_7_exists:
        print("✅ Week 7 games already in database")
    else:
        print("⚠️  Week 7 games NOT in database yet")
        print("   Will be auto-synced on Tuesday morning by enhanced updater")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error checking database: {e}")

print()
print("🔧 Auto-Sync Status:")
print("Enhanced background updater should:")
print("  1. ✅ Detect Week 7 on Tuesday Oct 15")
print("  2. ✅ Auto-sync Week 7 games from API")
print("  3. ✅ Make them available to users")
print()
print("📋 Action Items:")
print("  - Deploy enhanced updater to server if not already done")
print("  - Monitor logs on Tuesday morning for auto-sync")
print("  - Fallback: Manual sync if needed")
print()
print("🎯 Expected Result:")
print("  Users should see Week 7 games on Tuesday Oct 15, 6AM+")