# Dynamic Deadline System & Admin Override Features

## Overview
Enhanced the NFL Fantasy app with a comprehensive deadline management system that shows users exactly how much time they have left to make picks, and provides administrators with the ability to extend or modify deadlines as needed.

## New Features

### 1. Enhanced Dashboard Deadline Display
- **Hours Remaining**: Users can now see exactly how many hours they have left until each deadline
- **Visual Urgency Indicators**: 
  - Critical (red): Less than 2 hours remaining with pulsing animation
  - Warning (yellow): Less than 24 hours remaining
  - Normal (gray): More than 24 hours remaining
- **Next Deadline Card**: Prominently displays the most urgent upcoming deadline
- **Game Matchup Info**: Shows which specific games are affected by each deadline

### 2. Admin Deadline Override System
- **Individual User Overrides**: Admins can extend deadlines for specific users
- **Global Overrides**: Admins can extend deadlines for all users
- **Override Management**: View, create, and remove deadline overrides through the admin panel
- **Audit Trail**: All overrides are logged with admin user, timestamp, and reason

### 3. Dynamic Deadline Enforcement
- **Real-time Validation**: Pick submissions are validated against current deadlines (including overrides)
- **Game-specific Deadlines**: Different deadline rules for Thursday Night, Sunday, and Monday Night games
- **Timezone Handling**: All deadlines displayed and enforced in Atlantic Standard Time (AST)

## Technical Implementation

### New Files Created
1. **`deadline_manager.py`**: Core deadline calculation and management system
2. **`deadline_override_manager.py`**: Admin override functionality and database management
3. **`test_deadline_system.py`**: Test script to verify deadline system functionality

### Database Changes
- **`deadline_overrides` table**: Stores admin deadline modifications
  - Supports both user-specific and global overrides
  - Tracks who created the override and when
  - Includes reason field for documentation

### Enhanced Features
1. **Dashboard**: Now shows real-time deadline countdown with visual indicators
2. **Admin Panel**: New "Deadline Overrides" section for managing exceptions
3. **Pick Submission**: Enhanced validation that respects override deadlines
4. **CSS Animations**: Pulsing effects for critical deadlines to draw attention

## Usage Instructions

### For Users
1. **View Deadlines**: Check the dashboard for current deadline status with hours remaining
2. **Urgency Indicators**: Pay attention to color coding and animations for urgent deadlines
3. **Override Notifications**: Look for "⚠️ Modified by Admin" indicators when admins have extended your deadlines

### For Administrators
1. **Access Override Panel**: Go to Admin Panel → "Deadline Overrides"
2. **Create Override**: 
   - Select deadline type (Thursday/Sunday/Monday)
   - Choose specific user or global override
   - Set new deadline time
   - Add reason for documentation
3. **Manage Overrides**: View active overrides and remove them when no longer needed

## Configuration

### Deadline Offsets (configurable in `deadline_manager.py`)
- **Thursday Night Football**: 30 minutes before game start
- **Sunday Games**: 60 minutes before first Sunday game
- **Monday Night Football**: 30 minutes before game start

### Urgency Thresholds
- **Critical**: 0-2 hours remaining (red, pulsing)
- **Warning**: 2-24 hours remaining (yellow)
- **Normal**: 24+ hours remaining (gray)

## Error Handling
- Graceful fallback to default deadlines if database issues occur
- User-friendly error messages for failed override operations
- Comprehensive logging for troubleshooting

## Future Enhancements
- Email notifications for approaching deadlines
- Mobile-friendly deadline widgets
- Bulk override operations for multiple users
- Historical deadline override reporting

This system provides a professional, user-friendly approach to deadline management while giving administrators the flexibility they need to handle exceptions and special circumstances.
