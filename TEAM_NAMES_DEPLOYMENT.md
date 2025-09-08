# 🏈 NFL Team Names Feature - Deployment Guide

## 📋 DEPLOYMENT SUMMARY

**Feature:** Display full NFL team names alongside abbreviations in the "Make Picks" interface

**Status:** ✅ TESTED AND WORKING

---

## 🎯 MODIFIED FILES

### 1. **app.py** (Main Backend Changes)
- Added comprehensive NFL team names mapping (all 32 teams)
- Added `get_team_name()` function to convert abbreviations to full names
- Modified `/games` route to inject team names into game data
- Added template context processor for team name functions

**Key additions:**
```python
# NFL team names mapping (lines ~2640-2680)
NFL_TEAM_NAMES = {
    'ARI': 'Arizona Cardinals',
    'ATL': 'Atlanta Falcons',
    # ... all 32 teams
}

def get_team_name(abbreviation):
    """Get full team name from abbreviation"""
    return NFL_TEAM_NAMES.get(abbreviation, abbreviation)

# In games() route (lines ~365-367):
game_dict['away_team_name'] = get_team_name(game_dict['away_team'])
game_dict['home_team_name'] = get_team_name(game_dict['home_team'])
```

### 2. **templates/games.html** (Frontend Changes)
- Updated game headers to show "Team Name (ABB) @ Team Name (ABB)"
- Enhanced radio button labels to include team names
- Added CSS styling for proper team name display

**Key changes:**
```html
<!-- Game headers -->
<h3>{{ game.away_team_name }} ({{ game.away_team }}) @ {{ game.home_team_name }} ({{ game.home_team }})</h3>

<!-- Radio button labels -->
<label for="away_{{ game.id }}">
    <span class="team-abbrev">{{ game.away_team }}</span>
    <span class="team-name">{{ game.away_team_name }}</span>
</label>
```

### 3. **static/style.css** (Styling)
- Added `.team-name` class styling
- Ensured proper display of team names in pick interface

---

## 🚀 DEPLOYMENT STEPS

### Option 1: Manual File Transfer
1. **Backup production files:**
   ```bash
   cp app.py app.py.backup
   cp templates/games.html templates/games.html.backup
   ```

2. **Upload modified files:**
   - Upload `app.py` to production server
   - Upload `templates/games.html` to production server
   - Upload `static/style.css` if modified

3. **Restart production server:**
   ```bash
   sudo systemctl restart your-flask-service
   # OR
   pkill -f python
   python app.py
   ```

### Option 2: Git Deployment (if using version control)
```bash
git add app.py templates/games.html static/style.css
git commit -m "feat: Add NFL team names display in picks interface"
git push origin main

# On production server:
git pull origin main
sudo systemctl restart your-flask-service
```

---

## ✅ VERIFICATION STEPS

After deployment, verify:

1. **Login to the application**
2. **Navigate to "Make Picks"**
3. **Verify you see:**
   - Game headers: "Washington Commanders (WAS) @ Green Bay Packers (GB)"
   - Radio buttons: Show both abbreviation and full team name
   - All 32 NFL teams display correctly

## 📊 EXPECTED RESULTS

**Before:** WAS @ GB
**After:** Washington Commanders (WAS) @ Green Bay Packers (GB)

---

## 🔧 ROLLBACK PLAN

If issues occur:
```bash
cp app.py.backup app.py
cp templates/games.html.backup templates/games.html
sudo systemctl restart your-flask-service
```

---

## 📞 SUPPORT

Feature tested and working on development environment.
All team names properly mapped and displaying correctly.

**Deployment Date:** September 8, 2025
**Feature Status:** Production Ready ✅
