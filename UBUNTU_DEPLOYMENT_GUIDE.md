# Ubuntu Server Deployment Guide

## SSL Certificate Issues Fix

The recent Windows SSL fix has been updated to be production-safe. The system now:

1. **Uses proper SSL verification by default** (secure for Ubuntu/production)
2. **Only disables SSL verification when explicitly configured** (for development)

### For Ubuntu/Production (Recommended):
```bash
# SSL verification is enabled by default - no action needed
# The system will use proper SSL certificates
```

### For Development Only (if SSL issues persist):
```bash
# Only use this in development environments
export DISABLE_SSL_VERIFY=true
```

## Deployment Steps

### 1. Update the Server
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python 3.13 (if not already installed)
```bash
sudo apt install python3.13 python3.13-venv python3.13-dev -y
```

### 3. Clone/Update Repository
```bash
cd /path/to/your/app
git pull origin main
```

### 4. Create Virtual Environment
```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. SSL Certificate Verification Test
```bash
# Test API connectivity (should work with SSL verification enabled)
python3 -c "
from nfl_api_service import get_week_games
print('Testing API with SSL verification...')
games = get_week_games(1, 2025)
print(f'Success: Retrieved {len(games)} games')
"
```

### 7. Database Setup (if needed)
```bash
# If starting fresh or migrating
python3 setup_database.py
```

### 8. Test the Application
```bash
python3 app.py
```

## Key Changes Made for Ubuntu Compatibility

### 1. SSL Configuration
- ✅ **Secure by default**: Uses proper SSL verification
- ✅ **Configurable**: Can disable for development via environment variable
- ✅ **Production-ready**: No security warnings in production

### 2. Cross-Platform Compatibility
- ✅ **File paths**: Uses `os.path` for cross-platform compatibility
- ✅ **Dependencies**: All packages work on both Windows and Ubuntu
- ✅ **Database**: SQLite works identically on both platforms

## Environment Variables (Optional)

Create a `.env` file for production settings:

```bash
# .env file (production)
FLASK_ENV=production
DISABLE_SSL_VERIFY=false  # Default, can be omitted
```

For development troubleshooting only:
```bash
# .env file (development only)
FLASK_ENV=development
DISABLE_SSL_VERIFY=true   # Only if SSL issues persist
```

## Verification Checklist

After deployment, verify:

- [ ] ✅ API calls work with SSL verification enabled
- [ ] ✅ Database operations function correctly
- [ ] ✅ Game score updates work automatically
- [ ] ✅ User interface loads properly
- [ ] ✅ No SSL warnings in logs
- [ ] ✅ All features work as expected

## Troubleshooting

### If SSL Issues Persist on Ubuntu:
```bash
# Update CA certificates
sudo apt update
sudo apt install ca-certificates -y
sudo update-ca-certificates

# Install additional SSL packages
pip install certifi
```

### If API Calls Fail:
```bash
# Check API status manually
curl -H "Authorization: Bearer 900cc1d2-bf47-4ff8-a88c-92000ddeaa5e" \
     "https://api.balldontlie.io/nfl/v1/games?seasons[]=2025&weeks[]=1"
```

The deployment should work seamlessly on Ubuntu with proper SSL security enabled.
