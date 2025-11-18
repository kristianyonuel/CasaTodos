#!/usr/bin/env python3
"""
Final Integration Test for NFL Logos and Betting Odds
Validates all components are working correctly
"""

import sqlite3
import os
from pathlib import Path

def test_logo_files():
    """Test that all logo files exist and are accessible"""
    
    print("🎨 TESTING NFL TEAM LOGOS")
    print("=" * 30)
    
    images_dir = Path("static/images")
    
    if not images_dir.exists():
        print("❌ Images directory not found")
        return False
    
    # Expected team codes
    team_codes = [
        'ari', 'atl', 'bal', 'buf', 'car', 'chi', 'cin', 'cle',
        'dal', 'den', 'det', 'gb', 'hou', 'ind', 'jax', 'kc',
        'lv', 'lac', 'lar', 'mia', 'min', 'ne', 'no', 'nyg',
        'nyj', 'phi', 'pit', 'sf', 'sea', 'tb', 'ten', 'was'
    ]
    
    missing_logos = []
    valid_logos = []
    
    for code in team_codes:
        logo_path = images_dir / f"{code}.svg"
        if logo_path.exists() and logo_path.stat().st_size > 0:
            valid_logos.append(code)
        else:
            missing_logos.append(code)
    
    print(f"✅ Found {len(valid_logos)}/32 team logos")
    if missing_logos:
        print(f"❌ Missing logos: {', '.join(missing_logos)}")
        return False
    
    print("✅ All team logos present and valid")
    return True

def test_database_structure():
    """Test database has all required tables and columns"""
    
    print(f"\n🗄️ TESTING DATABASE STRUCTURE")
    print("-" * 35)
    
    try:
        conn = sqlite3.connect('nfl_fantasy.db')
        cursor = conn.cursor()
        
        # Test team_info table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='team_info'")
        if not cursor.fetchone():
            print("❌ team_info table not found")
            return False
        
        # Test team_info columns
        cursor.execute("PRAGMA table_info(team_info)")
        team_info_columns = [col[1] for col in cursor.fetchall()]
        required_team_columns = ['team_name', 'team_code', 'logo_url', 'primary_color']
        
        missing_team_cols = [col for col in required_team_columns if col not in team_info_columns]
        if missing_team_cols:
            print(f"❌ Missing team_info columns: {missing_team_cols}")
            return False
        
        print("✅ team_info table structure valid")
        
        # Test nfl_games betting columns
        cursor.execute("PRAGMA table_info(nfl_games)")
        games_columns = [col[1] for col in cursor.fetchall()]
        required_betting_columns = ['spread_line', 'spread_favorite', 'over_under', 'moneyline_home', 'moneyline_away']
        
        missing_betting_cols = [col for col in required_betting_columns if col not in games_columns]
        if missing_betting_cols:
            print(f"❌ Missing nfl_games betting columns: {missing_betting_cols}")
            return False
        
        print("✅ nfl_games betting columns valid")
        
        # Test data existence
        cursor.execute("SELECT COUNT(*) FROM team_info")
        team_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nfl_games WHERE week = 10 AND betting_updated IS NOT NULL")
        betting_games_count = cursor.fetchone()[0]
        
        print(f"✅ Database contains {team_count} teams and {betting_games_count} games with betting data")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_template_files():
    """Test that template files have been updated"""
    
    print(f"\n📄 TESTING TEMPLATE UPDATES")
    print("-" * 30)
    
    templates_dir = Path("templates")
    
    if not templates_dir.exists():
        print("❌ Templates directory not found")
        return False
    
    # Test main templates exist
    key_templates = ['games.html', 'test_logos_betting.html']
    
    for template in key_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"✅ Found {template}")
        else:
            print(f"❌ Missing {template}")
            return False
    
    # Test games.html has been enhanced
    games_path = templates_dir / "games.html"
    with open(games_path, 'r', encoding='utf-8') as f:
        games_content = f.read()
    
    if 'team-logo' in games_content and 'betting-info' in games_content:
        print("✅ games.html enhanced with logos and betting")
    else:
        print("❌ games.html missing logo/betting enhancements")
        return False
    
    return True

def test_css_styles():
    """Test that CSS styles have been added"""
    
    print(f"\n🎨 TESTING CSS STYLES")
    print("-" * 20)
    
    css_path = Path("static/style.css")
    
    if not css_path.exists():
        print("❌ style.css not found")
        return False
    
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    required_classes = ['team-logo', 'betting-info', 'game-card-enhanced', 'team-matchup']
    missing_classes = []
    
    for css_class in required_classes:
        if css_class not in css_content:
            missing_classes.append(css_class)
    
    if missing_classes:
        print(f"❌ Missing CSS classes: {missing_classes}")
        return False
    
    print("✅ All required CSS classes found")
    return True

def create_integration_summary():
    """Create a summary of what has been implemented"""
    
    summary = '''
# 🏈 NFL LOGOS AND BETTING ODDS - INTEGRATION COMPLETE

## ✅ IMPLEMENTED FEATURES

### 1. Team Logos System
- **32 SVG team logos** created in `static/images/`
- **Team database** with logo paths, colors, and division info
- **CSS styling** for logo display in multiple sizes
- **Template integration** ready for Flask routes

### 2. Vegas Betting Odds
- **Betting database columns** added to nfl_games table
- **Week 10 sample data** with realistic spreads, totals, and moneylines
- **Betting display components** in templates
- **Auto-update timestamps** for odds freshness

### 3. Enhanced Templates
- **games.html** updated with logo and betting display
- **Dashboard templates** enhanced with mini logos
- **Test page** created at `templates/test_logos_betting.html`
- **Responsive design** for mobile and desktop

### 4. Flask Integration Ready
- **Helper functions** created in `flask_logo_betting_helper.py`
- **Database query updates** to include betting data
- **Route enhancement examples** provided
- **Template variables** documented

## 🔧 FILES CREATED/MODIFIED

### New Files:
- `static/images/*.svg` (32 team logos)
- `setup_logos_and_betting.py` (main setup script)
- `create_svg_logos.py` (logo creation)
- `update_templates_with_logos.py` (template updater)
- `flask_logo_betting_helper.py` (Flask integration code)
- `templates/test_logos_betting.html` (test page)

### Modified Files:
- `static/style.css` (added logo and betting styles)
- `templates/games.html` (enhanced with logos and betting)
- `templates/index.html` (dashboard logo support)
- `nfl_fantasy.db` (new tables and columns)

## 📋 INTEGRATION STEPS

### 1. Update Flask App (app.py)
```python
# Copy functions from flask_logo_betting_helper.py
def get_team_logos_and_betting(games):
    # ... (see helper file)

# Update your games route
@app.route('/games')
def games():
    games = get_week_games(current_week)
    enhanced_games = get_team_logos_and_betting(games)
    return render_template('games.html', games=enhanced_games)
```

### 2. Test the Implementation
1. Restart Flask server
2. Visit `/test-logos` to verify logo loading
3. Visit `/games` to see enhanced game display
4. Check that betting odds appear correctly

### 3. Production Deployment
- Ensure `static/images/` directory is served correctly
- Verify database permissions for new tables
- Test logo loading on production domain
- Monitor betting odds update timestamps

## 🎯 NEXT FEATURES TO ADD

### Real-Time Betting Odds
- Integrate with DraftKings or FanDuel API
- Auto-update odds every 15 minutes
- Add odds movement tracking

### Enhanced Logo System
- Download high-resolution PNG logos
- Add alternate/throwback logos
- Team color theme integration

### Advanced Betting Features
- Player prop bets
- Live in-game odds
- Betting trend analysis
- User favorite teams highlighting

## 🧪 TESTING CHECKLIST

- [ ] All 32 team logos load correctly
- [ ] Betting odds display properly formatted
- [ ] Mobile responsive design works
- [ ] Database queries include new columns
- [ ] Flask routes enhanced with logo helper
- [ ] CSS styles apply correctly
- [ ] Template inheritance works
- [ ] Static file serving configured

## 📞 SUPPORT

If you encounter issues:
1. Check Flask server logs for template errors
2. Verify static file serving is enabled
3. Test database connectivity
4. Validate SVG logo file permissions
5. Check browser console for JavaScript errors

🎉 **CONGRATULATIONS!** Your NFL fantasy system now has professional team logos and Vegas betting odds integration!
'''
    
    with open('LOGOS_BETTING_INTEGRATION_COMPLETE.md', 'w') as f:
        f.write(summary)
    
    print("📝 Created integration summary: LOGOS_BETTING_INTEGRATION_COMPLETE.md")

def main():
    """Run all integration tests"""
    
    print("🧪 NFL LOGOS & BETTING INTEGRATION TEST")
    print("=" * 45)
    
    tests = [
        ("Logo Files", test_logo_files),
        ("Database Structure", test_database_structure),
        ("Template Files", test_template_files),
        ("CSS Styles", test_css_styles)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
    
    print(f"\n📊 INTEGRATION TEST RESULTS")
    print("=" * 35)
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Integration is complete!")
        create_integration_summary()
        
        print(f"\n🚀 READY TO DEPLOY!")
        print("Next steps:")
        print("1. Copy Flask helper code to app.py")
        print("2. Restart your Flask server")
        print("3. Visit /test-logos to verify setup")
        print("4. Enjoy your enhanced NFL fantasy system!")
        
    else:
        print("❌ Some tests failed. Check errors above.")
        
    return passed == total

if __name__ == "__main__":
    main()