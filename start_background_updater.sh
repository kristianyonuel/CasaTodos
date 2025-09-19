#!/bin/bash
# Ubuntu Background Updater Startup Script
# Run this to fix the API issues

echo "🏈 Starting Background Updater Fix..."
echo "=========================================="

# 1. Check if background_updater.py exists
if [ ! -f "background_updater.py" ]; then
    echo "❌ background_updater.py not found!"
    echo "   Make sure you're in the correct directory"
    exit 1
fi

echo "✅ background_updater.py found"

# 2. Kill any existing processes (just in case)
echo "🔄 Killing any existing background processes..."
pkill -f background_updater.py
sleep 2

# 3. Make sure it's executable
echo "🔧 Setting executable permissions..."
chmod +x background_updater.py

# 4. Start the background updater with logging
echo "🚀 Starting background updater..."
nohup python3 background_updater.py > updater.log 2>&1 &

# Wait a moment for it to start
sleep 3

# 5. Check if it's running
echo "🔍 Checking if process started..."
if ps aux | grep -v grep | grep background_updater > /dev/null; then
    echo "✅ Background updater is now running!"
    
    # Show the process
    echo "📋 Process details:"
    ps aux | grep -v grep | grep background_updater
    
    # Check initial log output
    echo ""
    echo "📝 Initial log output:"
    if [ -f "updater.log" ]; then
        tail -10 updater.log
    else
        echo "   Log file not created yet (this is normal)"
    fi
    
    echo ""
    echo "🎯 SUCCESS! Background updater is now running."
    echo "   - Check logs with: tail -f updater.log"
    echo "   - Verify with: ps aux | grep background_updater"
    echo "   - Run monitor: python3 weekly_auto_monitor.py"
    
else
    echo "❌ Failed to start background updater"
    echo "   Check for errors in the log:"
    if [ -f "updater.log" ]; then
        cat updater.log
    fi
    exit 1
fi
