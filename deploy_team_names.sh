#!/bin/bash
# 🚀 NFL Team Names Feature - Quick Deployment Script

echo "🏈 Deploying NFL Team Names Feature..."

# 1. Backup current files
echo "📋 Creating backups..."
cp app.py app.py.backup.$(date +%Y%m%d_%H%M%S)
cp templates/games.html templates/games.html.backup.$(date +%Y%m%d_%H%M%S)

# 2. Upload the modified files (you'll need to transfer these manually or via scp)
echo "📁 Files to upload:"
echo "  - app.py (main backend with team names logic)"
echo "  - templates/games.html (updated template)"
echo "  - static/style.css (if CSS was modified)"

# 3. Restart the Flask service
echo "🔄 Restarting Flask service..."
if command -v systemctl &> /dev/null; then
    # If using systemd service
    sudo systemctl restart casa-nfl-fantasy
    sudo systemctl status casa-nfl-fantasy
else
    # If running manually
    echo "Stop current Flask process and restart with:"
    echo "pkill -f python"
    echo "cd /path/to/your/app && python app.py"
fi

echo "✅ Deployment completed!"
echo "🔍 Verify by visiting your site and checking 'Make Picks' page"
