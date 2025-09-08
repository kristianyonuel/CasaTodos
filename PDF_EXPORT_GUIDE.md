# PDF Export Feature - La Casa de Todos NFL Fantasy

## Overview
The PDF export feature generates professional weekly dashboard reports for the NFL Fantasy league with tables showing winners, losses, statistics, and game results.

## Features

### 📊 Weekly Dashboard PDF Export
- **Leaderboard Table**: Shows all players ranked by wins, with columns for:
  - Rank (with 🥇🥈🥉 medals for top 3)
  - Player Name
  - Games Won
  - Games Lost  
  - Win Percentage
  - Monday Night Score Prediction

- **Game Status Table**: Shows all games for the week with:
  - Game Type (Thursday Night, Sunday Night, Monday Night, Regular)
  - Matchup (Away @ Home)
  - Score (if final) or "TBD" (if pending)
  - Game Status (FINAL, In Progress, etc.)

- **Summary Statistics**: 
  - Total games scheduled
  - Games completed (final)
  - Games pending
  - Generation timestamp

## How to Use

### Admin Panel Access
1. Log in as an admin user
2. Navigate to the Admin Panel
3. Click the **"📄 Export Weekly Dashboard PDF"** button
4. Enter the week number (1-18) when prompted
5. Enter the year (e.g., 2025) when prompted
6. PDF will automatically download

### Direct URL Access
```
/export_weekly_dashboard_pdf?week=1&year=2025
```

## Technical Implementation

### Dependencies
- `reportlab==4.0.4` - PDF generation library
- `pillow` - Image processing (installed with reportlab)

### Files
- `pdf_generator.py` - Core PDF generation logic
- `app.py` - Web route `/export_weekly_dashboard_pdf`
- `templates/admin.html` - Admin panel button and JavaScript

### Database Queries
The PDF generator queries the following tables:
- `users` - Player information
- `user_picks` - Pick data with correctness
- `nfl_games` - Game schedule and results

## Sample Output

```
🏈 La Casa de Todos - Week 1 Dashboard

Week 1, 2025 Summary
Total Games: 16
Final Games: 8
Pending Games: 8
Generated: 2025-09-07 21:34:15

🏆 Weekly Leaderboard
+------+----------+------+--------+--------+---------------+
| Rank | Player   | Wins | Losses | Win %  | Monday Night  |
+------+----------+------+--------+--------+---------------+
| 🥇 1 | Dad      | 8    | 0      | 100.0% | 45            |
| 🥈 2 | Mom      | 7    | 1      | 87.5%  | 42            |
| 🥉 3 | Son      | 6    | 2      | 75.0%  | 38            |
+------+----------+------+--------+--------+---------------+

🎯 Week Games Status
+---------------+-----------------+-------+--------+
| Game          | Matchup         | Score | Status |
+---------------+-----------------+-------+--------+
| Thursday Night| DAL @ PHI       | 24-21 | FINAL  |
| Regular       | KC @ LAC        | TBD   | 4th Qt |
| Monday Night  | PIT @ NYJ       | TBD   | Pre    |
+---------------+-----------------+-------+--------+
```

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install reportlab==4.0.4
   ```

2. **Verify Setup**:
   ```bash
   python test_pdf_export.py
   ```

3. **Test with Sample Data**:
   ```bash
   python demo_pdf_export.py
   ```

## Error Handling

The system handles various error conditions:
- Missing database file
- No picks data for specified week
- Invalid week/year parameters
- PDF generation failures
- Network/SSL issues during download

## Security

- Admin authentication required for access
- Input validation for week/year parameters
- No-cache headers prevent sensitive data caching
- SSL-compatible download mechanism

## File Naming Convention

Generated PDFs follow the pattern:
```
weekly_dashboard_week_{WEEK}_{YEAR}.pdf
```

Example: `weekly_dashboard_week_1_2025.pdf`

## Customization

The PDF generator supports customization of:
- Page size (currently A4)
- Color schemes
- Table layouts
- Font styles
- Header/footer content

## Backup Integration

PDF exports work alongside the backup system and can be generated for historical weeks as long as the data exists in the database.

## Support

For issues with PDF generation:
1. Check the app logs for error messages
2. Verify reportlab installation
3. Ensure database contains game and pick data
4. Test with the demo script to isolate issues
