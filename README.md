# 🏠 La Casa de Todos - NFL Fantasy League

Welcome to **La Casa de Todos**, a family-friendly NFL fantasy league web application! 🏈

## 🎯 Overview

La Casa de Todos is a custom NFL fantasy league designed for family fun and competition. Each week, participants select winning teams for NFL games from Thursday to Monday, with Monday Night Football serving as the tiebreaker through score predictions.

## 🏈 Game Rules

### 📝 Official Rules

1. **Weekly Competition**: Select picks for every NFL game each week
2. **Submission Deadlines**:
   - **Thursday**: Deadline for Thursday Night Football picks
   - **Sunday**: Deadline for weekend games (before first Sunday game)
3. **Monday Night Tiebreaker**: Score prediction for Monday Night Football determines weekly winner
4. **Rule Changes**: All rule modifications require participant voting
5. **Game Formats**:
   - **Weekly Pool**: $5 per week per participant
   - **Full Season**: $10 per week per participant
   - **Elimination**: Special format with 7-day advance submission requirement

### 🏆 Winning System
- **One winner per week**
- Closest Monday Night Football score prediction (high or low) wins
- Elimination format available for special weeks

## 🚀 Quick Start

### Running on All Network Interfaces

#### Method 1: Network launcher (Recommended)
```bash
python run-network.py
```

#### Method 2: Direct execution
```bash
python app.py
```

### Access the Application
- **Local Access**: http://127.0.0.1:5000
- **Network Access**: http://[YOUR-IP]:5000
- **Find Your IP**: 
  - Windows: `ipconfig`
  - Linux/Mac: `ip addr` or `ifconfig`

### Network Configuration
The application runs on:
- **Host**: 0.0.0.0 (all network interfaces)
- **Port**: 5000
- **Protocol**: HTTP
- **Threading**: Enabled for multiple connections

## 🎮 How to Play

1. **Register/Login**: Create your family member account
2. **Make Picks**: 
   - Select winning teams for each NFL game
   - Predict Monday Night Football score for tiebreaker
3. **Submit on Time**: 
   - Thursday deadline for Thursday Night Football
   - Sunday deadline for weekend games
4. **Win Weekly**: Closest Monday Night prediction wins the week
5. **Track Progress**: View leaderboard and family standings

## 🛠️ Features

- ✅ **User Authentication**: Secure login system for family members
- ✅ **NFL Game Integration**: Real-time game data from ESPN API
- ✅ **Weekly Picks**: Easy-to-use interface for game selections
- ✅ **Monday Night Tiebreaker**: Score prediction system
- ✅ **Admin Panel**: League management and oversight (admin only)
- ✅ **Leaderboard**: Track wins and statistics
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Family-Friendly**: Designed for fun family competition

## 👥 User Roles

### Regular Users
- Make weekly picks
- View their own selections
- Access leaderboard
- Read rules

### Administrator
- View all user selections
- Manage league settings
- Access admin panel
- Oversee weekly results

## 🗂️ Project Structure

```
La Casa de Todos/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── index.html        # Dashboard
│   ├── login.html        # Login page
│   ├── register.html     # Registration
│   ├── games.html        # Make picks
│   ├── admin.html        # Admin panel
│   ├── leaderboard.html  # Standings
│   └── rules.html        # Official rules
├── static/
│   ├── style.css         # CSS styling
│   ├── script.js         # JavaScript functionality
│   └── games.js          # Game selection logic
└── nfl_fantasy.db        # SQLite database (auto-created)
```

## 💾 Database

The application uses SQLite database with the following tables:
- **users**: Family member accounts and admin settings
- **nfl_games**: NFL game data from ESPN API
- **user_picks**: Weekly selections and score predictions
- **weekly_results**: Win/loss records and statistics

## 🔧 Configuration

### Free API Setup

#### MySportsFeeds (Recommended)
1. Sign up at [MySportsFeeds.com](https://www.mysportsfeeds.com/)
2. Get your free account credentials
3. Edit `nfl_api_service.py`:
   ```python
   self.msf_username = "your_username"
   self.msf_password = "your_password"
   ```

#### BallDontLie NFL API
- No signup required
- Rate limited to 60 requests per minute
- Automatically used as secondary source

#### ESPN API
- No signup required
- Used as backup source
- May have occasional outages

### API Rate Limits
- **MySportsFeeds Free**: 250 requests/day
- **BallDontLie**: 60 requests/minute
- **ESPN**: No documented limits

### Network Access
- **Local Network**: Accessible from any device on same network
- **Port Forwarding**: Configure router to allow external access
- **Firewall**: Ensure port 5000 is allowed
- **Mobile Access**: Use network IP to access from phones/tablets

### Security Notes
- Application runs without HTTPS for simplicity
- Suitable for home/family network use
- For public deployment, consider adding SSL/HTTPS

### Common Issues
- **Externally-managed error**: Use the provided launcher scripts
- **Module not found**: Run the dependency installer
- **Permission errors**: Run as administrator or use `--user` flag

### Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- ⚠️ **Change this password after first login!**

### NFL Data Source
- **API**: BallDontLie NFL API (Free with API key)
- **Coverage**: Live scores, schedules, team information
- **Update**: Real-time during games
- **Backup**: Local database storage

## 🎨 Customization

### Entry Fees
- Weekly Pool: $20 per participant
- Initial Joining Fee: $20 (one-time payment)
- Modify in database or application settings

### Game Rules
- Deadline adjustments in application logic
- Scoring system modifications
- Additional game formats

## 🤝 Family League Setup

1. **Create Admin Account**: Use default or create new admin
2. **Add Family Members**: Each person registers their account
3. **Collect Entry Fees**: $20 initial joining fee + $20 per week
4. **Set Weekly Schedule**: Ensure everyone knows deadlines
5. **Monitor Picks**: Admin can view all selections
6. **Declare Winners**: Based on Monday Night tiebreaker

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern web browsers

## 🔒 Security

- Password hashing using Werkzeug
- Session-based authentication
- Admin-only access controls
- Secure database storage

## 🐛 Troubleshooting

### Common Issues

**Application won't start**
```bash
# Check Python version
python --version

# Install dependencies
pip install --user -r requirements.txt

# Run with verbose output
python app.py
```

**NFL games not loading**
- Check internet connection
- ESPN API may be temporarily unavailable
- Games load automatically when available

**Can't log in**
- Use default admin credentials: admin/admin123
- Register new account if needed
- Check password requirements (minimum 6 characters)

## 🤖 API Integration

### ESPN NFL API
- **Endpoint**: ESPN Scoreboard API
- **Data**: Game schedules, scores, team information
- **Update Frequency**: Real-time during games
- **Backup**: Local database storage

## 📊 Statistics Tracking

- Weekly wins per user
- Average correct picks
- Total points/wins
- Monday Night prediction accuracy
- Season-long performance

## 🎉 Family Fun Features

- **Friendly Competition**: Family-focused design
- **Weekly Prizes**: $20 per week pool
- **Initial Buy-in**: $20 to join the league
- **Easy Interface**: Simple pick selection
- **Weekly Excitement**: New games every week
- **Tiebreaker Drama**: Monday Night excitement
- **Season-Long**: Ongoing family engagement

## 📄 License

This project is designed for family use and entertainment. Feel free to fork and modify for your own family league!

## 🤝 Contributing

While this is primarily a family project, suggestions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🆘 Support

For family league support or technical issues:
- Check the troubleshooting section
- Review the official rules
- Contact the league administrator

---

**¡Que gane el mejor! (May the best win!)** 🏆

*La Casa de Todos - Where family competition meets NFL excitement!*
