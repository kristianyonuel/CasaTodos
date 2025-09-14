#!/bin/bash
# Server Restart Script for Ubuntu
# Use this to properly restart the La Casa de Todos NFL app

echo "🏈 La Casa de Todos - Server Restart Script"
echo "==========================================="

# Navigate to app directory
cd ~/CasaTodos || { echo "❌ Error: Could not find ~/CasaTodos directory"; exit 1; }

echo "📥 Pulling latest updates from GitHub..."
git pull origin main

echo "🔄 Stopping existing Flask processes..."
# Kill any existing Flask processes
pkill -f "python.*app.py" || echo "No existing Flask processes found"

# Wait a moment for processes to stop
sleep 2

echo "🏗️  Starting new Flask application..."
# Start the Flask app in the background
nohup python3 app.py > app.log 2>&1 &

# Get the process ID
APP_PID=$!
echo "✅ Flask app started with PID: $APP_PID"

# Wait a moment for startup
sleep 3

# Test if the app is responding
echo "🔍 Testing server health..."
if python3 test_server_health.py http://localhost:5000; then
    echo "🎉 Server restart successful!"
    echo "💡 Check logs with: tail -f ~/CasaTodos/app.log"
else
    echo "⚠️  Server may have issues - check logs"
    echo "💡 Check logs with: tail -f ~/CasaTodos/app.log"
fi

echo ""
echo "📊 Server Status:"
echo "  PID: $APP_PID"
echo "  Logs: ~/CasaTodos/app.log" 
echo "  URL: http://your-server-ip:5000"
echo ""
echo "🛑 To stop server: kill $APP_PID"
