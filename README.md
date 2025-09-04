# 🏠 La Casa de Todos - NFL Fantasy League 2025

Welcome to **La Casa de Todos**, a professional-grade NFL fantasy league web application designed for family fun and serious competition! 🏈

## 🎯 Overview

La Casa de Todos is a comprehensive NFL fantasy league platform featuring modern web technologies, dynamic deadline management, and sophisticated scoring systems. Completely refactored for Python 3.13 with enhanced features including Monday Night Football tiebreakers, admin overrides, CSV import/export, and multi-port SSL support.

## 🚀 **Project Status: COMPLETE & READY FOR 2025 SEASON** ✅

**All major features have been implemented, tested, and verified:**
- ✅ Python 3.13 compatibility confirmed
- ✅ Dynamic deadline system fully operational
- ✅ Simplified 1-point scoring system implemented
- ✅ Monday Night tiebreakers working correctly
- ✅ Admin features and overrides functional
- ✅ Navigation and templates updated and error-free
- ✅ Database schema optimized and tested
- ✅ Leaderboard calculations verified
- ✅ Multi-port server options available
- ✅ Comprehensive test suite included

## 🆕 What's New in 2025

### ✨ Major Updates (✅ **COMPLETED & VERIFIED**)
- **🐍 Python 3.13 Compatibility**: Full upgrade with modern type hints and performance improvements
- **⚡ Dynamic Deadline System**: Real-time deadline tracking with visual urgency indicators
- **🔧 Admin Override System**: Flexible deadline extensions for individual users or entire league
- **📊 CSV Import/Export**: Bulk pick management and data portability
- **🏆 Enhanced Scoring**: Simplified 1-point-per-win system with Monday Night tiebreakers
- **🔒 Multi-Port SSL Support**: Production-ready HTTPS deployment options
- **📱 Responsive Design**: Optimized for all devices with modern UI/UX
- **🧭 Navigation Fixes**: All template navigation updated and verified (no broken 'dashboard' references)
- **📊 Leaderboard System**: Weekly and season leaderboards fully implemented and tested
- **👥 Post-Deadline Pick Visibility**: Users can see everyone's picks after deadlines pass for transparency

## 🏈 Game Rules & Scoring

### 📝 Simple Scoring System
- **1 point per game won** (including Monday Night Football)
- **No bonus points** - all games worth equal value
- **Thursday, Sunday, and Monday games** all worth 1 point each

### 🏆 Tiebreaker System
When users have the same number of games won:
1. **Closest to Monday Night Home Team Score**
2. **Closest to Monday Night Away Team Score**
3. **Closest to Monday Night Total Combined Score**
4. **Alphabetical Order** (final tiebreaker)

### ⏰ Dynamic Deadlines
- **Thursday Night Football**: Individual deadlines 30 minutes before each game
- **Friday/Saturday Games**: Individual deadlines, NOT included in Sunday deadline
- **Sunday/Monday Games**: Shared deadline 30 minutes before first Sunday game
- **Admin Overrides**: Flexible extensions for emergencies or special circumstances
- **Post-Deadline Transparency**: After deadlines pass, all users can see everyone's picks for that game

## 🚀 Quick Start

### 🖥️ Multiple Server Options

#### Option 1: Simple Local Server
```bash
python app.py
```

#### Option 2: Network Access
```bash
python run-network.py
```

#### Option 3: Multi-Port Production
```bash
python run-externally-managed.py
```

#### Option 4: HTTPS/SSL Support
```bash
python run-port-443.py  # Requires SSL certificates
```

### 🌐 Access URLs
- **Local**: http://127.0.0.1:5000
- **Network**: http://[YOUR-IP]:5000
- **HTTPS**: https://[YOUR-DOMAIN]:443 (with SSL setup)

## 🎮 How to Play

### 👤 For Players
1. **Register/Login**: Create your account or use existing credentials
2. **View Dashboard**: See deadline countdown, pick progress, and quick stats
3. **Make Picks**: 
   - Select winning teams for each NFL game
   - Predict Monday Night Football scores for tiebreakers
4. **Monitor Deadlines**: Real-time countdown with urgency indicators
5. **Track Performance**: View weekly and season leaderboards
6. **Post-Deadline Viewing**: See all players' picks after deadlines pass for transparency and strategy analysis

### 👑 For Administrators
1. **User Management**: Create, edit, delete user accounts
2. **Pick Management**: View, modify, or set picks for any user
3. **Deadline Overrides**: Extend deadlines for individuals or entire league
4. **CSV Operations**: Import/export picks for data management
5. **Game Management**: Update scores, add games, manage schedule
6. **Emergency Controls**: Quick deadline extensions for technical issues

## 🛠️ Advanced Features

### 🔧 Admin Dashboard
- **User Management**: Complete CRUD operations for user accounts
- **Pick Management**: View and modify any user's picks
- **Game Management**: Update scores, manage NFL schedule
- **Deadline Overrides**: Flexible deadline extension system
- **CSV Import/Export**: Bulk data operations
- **Emergency Extensions**: Quick fixes for technical issues

### 📊 Deadline Management
- **Real-Time Tracking**: Live countdown timers
- **Visual Urgency**: Color-coded warning system
  - 🔴 Critical: 0-2 hours remaining (pulsing red)
  - 🟡 Warning: 2-24 hours remaining (yellow)
  - ⚪ Normal: 24+ hours remaining (gray)
- **Individual Overrides**: Per-user deadline extensions
- **Global Overrides**: League-wide deadline changes

### 📈 Enhanced Reporting
- **Weekly Leaderboards**: Detailed Monday Night tiebreaker analysis
- **Season Standings**: Total wins, weekly wins, average performance
- **Pick History**: Complete audit trail of all selections
- **CSV Exports**: Data portability for external analysis

## 🗂️ Project Structure

```
La Casa de Todos/
├── app.py                      # Main Flask application (Python 3.13)
├── models.py                   # Database models and repositories
├── config.py                   # Application configuration
├── deadline_manager.py         # Dynamic deadline system
├── deadline_override_manager.py # Admin override functionality
├── scoring_manager.py          # Scoring and tiebreaker logic
├── requirements.txt            # Python 3.13 dependencies
├── setup_database.py          # Database initialization
├── 
├── services/
│   ├── game_service.py         # Game management logic
│   └── nfl_service.py          # NFL API integration
├── 
├── templates/
│   ├── index.html              # Enhanced dashboard
│   ├── login.html              # User authentication
│   ├── register.html           # User registration
│   ├── games.html              # Pick selection interface
│   ├── admin.html              # Comprehensive admin panel
│   ├── leaderboard.html        # Season standings
│   ├── weekly_leaderboard.html # Weekly results with tiebreakers
│   ├── rules.html              # Official rules
│   └── error.html              # Error handling
├── 
├── static/
│   ├── style.css               # Modern responsive CSS
│   ├── login.css               # Login page styling
│   └── images/
│       └── logo.png            # La Casa de Todos logo
├── 
├── utils/
│   ├── logging_utils.py        # Centralized logging
│   └── timezone_utils.py       # AST timezone handling
├── 
├── tests/                      # Comprehensive test suite
│   ├── test_deadline_system.py
│   ├── test_csv_functionality.py
│   ├── test_weekly_leaderboard.py
│   └── verify_app_running.py
├── 
└── documentation/              # Complete documentation
    ├── ADMIN_FIXES_COMPLETE.md
    ├── CSV_IMPORT_EXPORT_GUIDE.md
    ├── DEADLINE_SYSTEM_GUIDE.md
    └── MULTI_PORT_SETUP.md
```

## 💾 Database Schema

Enhanced SQLite database with new tables and optimized structure:

### Core Tables
- **users**: User accounts with admin privileges and metadata
- **nfl_games**: Complete NFL schedule with game types and status
- **user_picks**: Pick selections with score predictions and correctness
- **weekly_results**: Calculated weekly standings and statistics

### New Tables
- **deadline_overrides**: Admin deadline extensions with audit trail
- **game_types**: Standardized game type definitions
- **user_sessions**: Enhanced session management

## 🔧 Configuration & Setup

### 🐍 Python 3.13 Requirements
```bash
# Check Python version
python --version  # Should be 3.11+ (3.13 recommended)

# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_database.py
```

### 🌐 Network Configuration
```python
# Multiple deployment options available
HOST = "0.0.0.0"          # All network interfaces
PORTS = [5000, 8080, 443] # Multiple port support
SSL_ENABLED = True        # HTTPS support
```

### 🔒 Security Features
- **Enhanced Password Hashing**: Werkzeug security with salt
- **Session Management**: Secure session handling
- **Admin Access Controls**: Multi-level authorization
- **SQL Injection Protection**: Parameterized queries
- **XSS Prevention**: Template auto-escaping

### 🌐 API Integration
- **Primary**: ESPN NFL Scoreboard API
- **Backup**: MySportsFeeds API
- **Tertiary**: BallDontLie NFL API
- **Fallback**: Manual game management

## 📊 Enhanced Analytics

### 📈 Weekly Performance
- Games won vs. total games
- Win percentage and trends
- Monday Night tiebreaker accuracy
- Pick submission timing

### 🏆 Season Statistics
- Total wins and ranking
- Weekly win consistency
- Head-to-head comparisons
- Performance by game type

### 📋 Admin Insights
- User engagement metrics
- Pick submission patterns
- Deadline extension usage
- System performance data

## 📱 Mobile & Responsive Design

### 📱 Device Support
- **📱 Mobile**: iPhone, Android phones
- **📟 Tablets**: iPad, Android tablets
- **💻 Desktop**: Windows, macOS, Linux
- **🌐 Browsers**: Chrome, Safari, Firefox, Edge

### 🎨 UI/UX Features
- **Responsive Grid**: Adaptive layout for all screen sizes
- **Touch Optimization**: Mobile-first design approach
- **Fast Loading**: Optimized assets and caching
- **Accessibility**: WCAG 2.1 compliance

## 🚨 Troubleshooting & Support

### 🔧 Common Issues

**Python 3.13 Compatibility**
```bash
# Run compatibility check
python test_app_startup.py

# Upgrade packages if needed
pip install --upgrade -r requirements.txt
```

**Database Issues**
```bash
# Reset database
python setup_database.py --reset

# Verify database integrity
python verify_app_running.py
```

**Network Access Problems**
```bash
# Check firewall settings
# Ensure port 5000 is open
# Use network launcher
python run-network.py
```

### 📞 Support Resources
- **Documentation**: `/documentation/` folder
- **Test Scripts**: `/tests/` folder for diagnostics (including `test_weekly_leaderboard.py`)
- **Debug Routes**: `/debug_leaderboard` for troubleshooting leaderboard issues
- **Logs**: Comprehensive logging for issue tracking (`app.log`)
- **Verification Tools**: Run `verify_app_running.py` to check system status

## 🎉 Family Fun Features

### 🏠 Family-Focused Design
- **Simple Interface**: Easy for all family members
- **Weekly Excitement**: New games every week
- **Tiebreaker Drama**: Monday Night Football suspense
- **Season Competition**: Long-term family engagement
- **Fair Play**: Transparent scoring and deadline system
- **Post-Game Strategy**: See everyone's picks after deadlines for friendly analysis and discussion

### 💰 Financial Management
- **Flexible Entry**: Customizable weekly/season fees
- **Automatic Tracking**: Win/loss records
- **Fair Distribution**: Clear winner determination
- **Season Payouts**: Comprehensive statistics for prizes

## 🔮 Future Enhancements

### 🚀 Planned Features
- **Mobile App**: Native iOS/Android applications
- **Email Notifications**: Deadline reminders and results
- **Push Notifications**: Real-time game updates
- **Advanced Analytics**: Detailed performance insights
- **Social Features**: Comments and family chat
- **Historical Data**: Multi-season tracking

### 🛠️ Technical Roadmap
- **Docker Support**: Containerized deployment
- **Cloud Deployment**: AWS/Azure integration
- **Real-time Updates**: WebSocket implementation
- **API Expansion**: RESTful API for third-party integrations
- **Performance**: Caching and optimization

## 📄 License & Contributing

### 📜 License
This project is designed for family use and entertainment. Open source under MIT License.

### 🤝 Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 🆘 Support & Community

### 💬 Getting Help
- **Documentation**: Comprehensive guides in `/documentation/`
- **Test Scripts**: Diagnostic tools in `/tests/`
- **Debug Tools**: Built-in debugging routes
- **Issue Tracking**: GitHub issues for bug reports

### 🔧 Maintenance
- **Regular Updates**: Seasonal NFL schedule updates
- **Security Patches**: Ongoing security maintenance
- **Feature Updates**: Community-driven enhancements
- **Performance**: Continuous optimization

---

**¡Que gane el mejor! (May the best win!)** 🏆

*La Casa de Todos 2025 - Where family competition meets professional-grade NFL fantasy technology!*

## 🎯 Quick Reference

### 🔑 Default Admin Access
- **Username**: `admin`
- **Password**: `admin123`
- **⚠️ IMPORTANT**: Change password after first login!

### 🌐 URLs to Remember
- **Dashboard**: `/` (main page)
- **Make Picks**: `/games`
- **Leaderboard**: `/leaderboard` (season standings)
- **Weekly Results**: `/weekly_leaderboard` (weekly results with Monday Night tiebreakers)
- **Admin Panel**: `/admin` (admin only)
- **Rules**: `/rules`
- **Debug Tools**: `/debug_leaderboard` (troubleshooting - admin only)

### ⚡ Emergency Commands
```bash
# Quick start (Python 3.13 recommended)
python app.py

# Network access for family play
python run-network.py

# Multi-port production setup
python run-externally-managed.py

# Reset everything (if issues occur)
python setup_database.py --reset

# Test system health
python verify_app_running.py

# Test weekly leaderboard specifically
python test_weekly_leaderboard.py

# Check app startup
python test_app_startup.py
```

### 📞 Need Help?
Check the `/documentation/` folder for detailed guides on every feature!
