# Weekly Leaderboard Auto-Update Enhancement

## Overview
Enhanced the background game updater to make the weekly leaderboard update much faster when games end.

## Key Improvements

### 1. Dynamic Update Intervals
- **Game Days** (Mon, Tue, Thu, Sat, Sun) during peak hours (11 AM - 11 PM): **5 minutes**
- **Off-peak times**: **30 minutes**
- Previous system: Fixed 30-minute intervals

### 2. Intelligent Game Day Detection
- Automatically detects game days and peak viewing hours
- Increases update frequency during NFL game times
- Reduces API calls during quiet periods

### 3. Leaderboard Refresh Triggers
- Automatically triggers leaderboard refresh when games are updated
- Ensures pick correctness (`is_correct` field) is immediately recalculated
- Ready for future cache invalidation if needed

## Technical Changes

### File: `background_updater.py`
- Added `_get_dynamic_interval()` method for intelligent scheduling
- Modified update loop to use dynamic intervals
- Enhanced status reporting with interval details

### File: `score_updater.py`
- Added `trigger_leaderboard_refresh()` method
- Integrated leaderboard refresh into update cycle
- Triggers refresh only when games are actually updated

## Expected Behavior

### During Game Days (Thursday/Sunday/Monday)
- Updates every **5 minutes** from 11 AM to 11 PM
- Picks are scored immediately when games end
- Leaderboard reflects changes within 5 minutes

### During Off-Peak Times
- Updates every **30 minutes** to conserve resources
- Maintains system responsiveness

### When Games End
1. Background updater fetches latest scores (every 5 min during games)
2. Game scores and `is_final` status updated in database
3. User pick `is_correct` values recalculated automatically
4. Leaderboard refresh triggered
5. Weekly leaderboard shows updated scores within 5 minutes

## Testing
✅ Dynamic interval calculation tested
✅ Game day detection working
✅ Status reporting enhanced
✅ Ready for deployment

## Deployment
All changes are backward compatible and will take effect when the background updater is restarted with the app.

## Future Enhancements
- Add webhook notifications when leaderboards update
- Implement Redis caching with automatic invalidation
- Add real-time WebSocket updates for instant leaderboard changes
