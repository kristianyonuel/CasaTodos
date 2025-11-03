#!/bin/bash
"""
Azure VM Flask App Restart Commands
Copy and paste these commands into your Azure VM SSH session
"""

echo "🔄 RESTARTING FLASK APP TO LOAD WEEK 9 DATA"
echo "=" * 50

# Stop the service
echo "1. Stopping Flask service..."
sudo systemctl stop lacasadetodos.service

# Wait a moment
echo "2. Waiting 3 seconds..."
sleep 3

# Start the service
echo "3. Starting Flask service..."
sudo systemctl start lacasadetodos.service

# Wait for startup
echo "4. Waiting for startup..."
sleep 5

# Check status
echo "5. Checking service status..."
sudo systemctl status lacasadetodos.service --no-pager

# Check if app is running
echo "6. Checking if app process is running..."
ps aux | grep "python.*app.py" | grep -v grep

echo ""
echo "🎯 After restart, refresh your website!"
echo "✅ Week 9 leaderboard should show JEAN with 9 points"
echo "✅ COYOTE should show Miami pick (lost to Ravens)"
echo "✅ All game scores should display correctly"