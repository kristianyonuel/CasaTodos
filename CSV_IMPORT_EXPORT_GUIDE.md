# CSV Import/Export Feature Guide

## Overview
The CSV import/export feature allows administrators to manage picks for users who don't use the web application directly. This is particularly useful for handling picks from family members or friends who prefer to submit their picks via text, email, or other offline methods.

## CSV Export

### How to Export
1. Go to **Admin Panel**
2. Select the desired **Week** and **Year**
3. Click **"Export Picks CSV"**
4. The file `picks_week_X_YYYY.csv` will automatically download

### Export Contents
The exported CSV contains:
- **All users** in the system
- **All games** for the selected week
- **Existing picks** (if any)
- **Empty rows** for users who haven't made picks yet

### CSV Format
```csv
username,game_id,away_team,home_team,selected_team,predicted_home_score,predicted_away_score
john_doe,1,Bills,Chiefs,Chiefs,,
john_doe,2,Cowboys,Giants,,
jane_smith,1,Bills,Chiefs,Bills,,
jane_smith,5,Packers,Bears,Packers,24,17
```

## CSV Import

### Preparing the CSV File
1. **Use the exported format** as a template, or
2. **Create a new CSV** with the required columns:
   - `username` (required)
   - `game_id` (required)
   - `away_team` (for reference)
   - `home_team` (for reference)
   - `selected_team` (leave empty for no pick)
   - `predicted_home_score` (optional, for Monday Night games)
   - `predicted_away_score` (optional, for Monday Night games)

### Import Process
1. Go to **Admin Panel**
2. Select the desired **Week** and **Year**
3. Click **"Import Picks CSV"**
4. **Select your CSV file**
5. **Configure options**:
   - ✅ **Overwrite existing picks**: Replace picks that users already made
   - ✅ **Create missing users**: Automatically create accounts for unknown usernames
6. Click **"Validate CSV"** to check for errors
7. Click **"Import Picks"** to process the file

### Import Options

#### Overwrite Existing Picks
- **Checked**: Replaces any picks that users already made through the web app
- **Unchecked**: Skips rows where users already have picks (preserves user choices)

#### Create Missing Users
- **Checked**: Creates new user accounts for usernames not in the system
  - Default password: `changeme123` (users should change this)
  - Users will need to log in and set a proper password
- **Unchecked**: Skips rows with unknown usernames

## Common Use Cases

### 1. Family Member Picks via Text
```
Uncle Bob texts: "I want Chiefs, Cowboys, and Packers this week"
```
1. Export CSV for current week
2. Find Uncle Bob's rows in the CSV
3. Fill in his `selected_team` choices
4. Import the CSV back

### 2. Group Email Submission
```
Multiple people email their picks for the week
```
1. Export CSV template
2. Fill in picks for each person
3. Import all picks at once

### 3. Phone Call Picks
```
Grandma calls with her picks
```
1. Export CSV
2. Update Grandma's rows while on the call
3. Import immediately

## Data Validation

The system validates:
- **Username exists** (or can be created)
- **Game ID is valid** for the selected week
- **Selected team** must be one of the two teams playing
- **Score predictions** must be numbers (if provided)

## Error Handling

### Validation Errors
- Invalid game IDs
- Team names that don't match the game
- Missing required fields
- Invalid score formats

### Import Warnings
- Missing users (when creation is disabled)
- Invalid score predictions (will be ignored)
- Skipped existing picks (when overwrite is disabled)

## Security Considerations

### User Account Creation
- New users get a default password: `changeme123`
- **Important**: New users should log in and change their password immediately
- Consider creating users manually with secure passwords instead

### Data Protection
- Only administrators can export/import picks
- All import actions are logged
- CSV files contain user data - handle securely

## Best Practices

### 1. Regular Backups
- Export CSV files regularly as backups
- Store in secure location

### 2. User Communication
- Inform users when you've imported picks for them
- Remind new users to change their default passwords
- Let users know they can still modify picks through the web app

### 3. Deadline Management
- Import picks well before deadlines
- Use the admin deadline override feature if needed
- Validate CSV files before importing to catch errors early

### 4. Quality Control
- Always validate before importing
- Review warnings and errors carefully
- Test with a small CSV first if unsure

## Troubleshooting

### Common Issues

**"Game ID not found"**
- Make sure you're importing for the correct week/year
- Check that games have been created for that week

**"User not found"**
- Enable "Create missing users" option, or
- Create user accounts manually first

**"Invalid team name"**
- Use exact team names from the database
- Check the exported CSV for correct spelling

**"CSV format error"**
- Ensure CSV has all required columns
- Check for extra commas or quotes in data
- Save as CSV (not Excel format)

### File Format Tips
- Use UTF-8 encoding
- Avoid special characters in usernames
- Keep team names exactly as they appear in exports
- Leave empty cells blank (don't use "N/A" or similar)

## Example Workflow

1. **Monday**: Export CSV template for upcoming week
2. **Throughout week**: Collect picks via text/email/calls
3. **Thursday before deadline**: Fill in CSV with collected picks
4. **Thursday**: Validate and import CSV
5. **Verify**: Check that all picks were imported correctly

This system provides flexibility for handling picks from users who prefer offline communication while maintaining data integrity and security.
