#!/bin/bash
# Deployment script with auto-restart setup for lacasadetodos service

SERVICE_NAME="lacasadetodos"
APP_DIR="/home/casa/CasaTodos"

echo "🚀 Deploying La Casa de Todos with Auto-Restart"
echo "================================================"

# Update the app code
echo "📥 Pulling latest changes..."
cd "$APP_DIR"
git pull origin main

# Set up auto-restart if not already configured
if ! systemctl is-enabled "$SERVICE_NAME" >/dev/null 2>&1; then
    echo "🔧 Setting up auto-restart for the first time..."
    sudo "$APP_DIR/setup_auto_restart.sh"
else
    echo "🔄 Auto-restart already configured, restarting service..."
    sudo systemctl restart "$SERVICE_NAME"
    
    # Wait and verify
    sleep 10
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✅ Service restarted successfully"
    else
        echo "❌ Service failed to restart, checking logs..."
        sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    fi
fi

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🔍 Current Status:"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "📊 Quick Commands:"
echo "   sudo systemctl status $SERVICE_NAME      # Check status"
echo "   sudo $APP_DIR/service_manager.sh health  # Health check"
echo "   sudo $APP_DIR/service_manager.sh logs    # View logs"
