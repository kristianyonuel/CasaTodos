#!/bin/bash
# Remote server fix for pick correctness calculation
# This script applies the critical bug fix to the remote server

echo "🏈 Casa Todos - Remote Server Fix Script"
echo "========================================"

# Navigate to application directory
cd /home/casa/CasaTodos || { echo "❌ Application directory not found"; exit 1; }

# Pull latest changes from git (includes our fix)
echo "📥 Pulling latest changes from repository..."
git pull origin main

# Run the pick correctness fix
echo "🔧 Fixing pick correctness calculation..."
python3 fix_pick_correctness.py

# Restart the application
echo "🔄 Restarting application..."
sudo systemctl restart casa-todos-auto-restart.service

# Check service status
echo "✅ Checking service status..."
sudo systemctl status casa-todos-auto-restart.service --no-pager -l

# Verify application is running
echo "🔍 Verifying application health..."
sleep 5
curl -f http://localhost:5000/health || echo "⚠️  Health check failed - check application logs"

echo "🎉 Remote server fix completed!"
echo "📊 Users should now see accurate scoring in leaderboards"
