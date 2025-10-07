#!/bin/bash
"""
Deploy Enhanced Background Updater
Sets up the enhanced updater with weekly auto-sync
"""

echo "🚀 Deploying Enhanced NFL Background Updater..."

# Stop existing services
echo "⏹️ Stopping existing services..."
sudo systemctl stop lacasadetodos.service 2>/dev/null || true
sudo systemctl stop enhanced-nfl-updater.service 2>/dev/null || true

# Kill any running background processes
echo "🔄 Stopping old background processes..."
pkill -f background_updater.py 2>/dev/null || true
pkill -f enhanced_background_updater.py 2>/dev/null || true

# Copy service file
echo "📁 Installing service file..."
sudo cp enhanced-nfl-updater.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable the new service
echo "✅ Enabling enhanced updater service..."
sudo systemctl enable enhanced-nfl-updater.service

# Start the main app service
echo "🌐 Starting main app service..."
sudo systemctl start lacasadetodos.service

# Start the enhanced updater
echo "🏈 Starting enhanced background updater..."
sudo systemctl start enhanced-nfl-updater.service

# Check status
echo "📊 Service Status:"
echo "Main App:"
sudo systemctl status lacasadetodos.service --no-pager -l
echo
echo "Enhanced Updater:"
sudo systemctl status enhanced-nfl-updater.service --no-pager -l

echo
echo "🎉 Deployment complete!"
echo "Features enabled:"
echo "  ✅ Live score updates every 5-30 minutes"
echo "  ✅ Automatic weekly game sync (Tue/Wed mornings)"
echo "  ✅ Missing week detection and sync"
echo "  ✅ API rate limiting protection"
echo
echo "Logs available at:"
echo "  Main app: sudo journalctl -u lacasadetodos.service -f"
echo "  Enhanced updater: sudo journalctl -u enhanced-nfl-updater.service -f"
echo "  File logs: tail -f enhanced_background_updater.log"