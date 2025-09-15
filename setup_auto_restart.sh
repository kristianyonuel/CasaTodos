#!/bin/bash
# Auto-Restart Setup Script for La Casa de Todos
# Run this script on your Ubuntu server to set up auto-restart functionality

SERVICE_NAME="lacasadetodos"
APP_DIR="/home/casa/CasaTodos"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
MONITOR_SCRIPT="${APP_DIR}/monitor_lacasadetodos.sh"

echo "🔄 Setting up auto-restart for La Casa de Todos NFL Fantasy App"
echo "=============================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Step 1: Stop existing service if running
echo "🛑 Stopping existing service..."
systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# Step 2: Copy service file
echo "📄 Installing systemd service..."
cp "${APP_DIR}/lacasadetodos.service" "$SERVICE_FILE"

# Verify service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Failed to copy service file"
    exit 1
fi

# Step 3: Reload systemd and enable service
echo "🔄 Configuring systemd..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

# Step 4: Set up monitoring script
echo "📊 Setting up health monitoring..."
chmod +x "$MONITOR_SCRIPT"

# Create log directory
mkdir -p /var/log
touch /var/log/lacasadetodos-monitor.log
chown casa:casa /var/log/lacasadetodos-monitor.log

# Step 5: Add cron job for monitoring (every 2 minutes)
echo "⏰ Setting up cron job for monitoring..."
CRON_JOB="*/2 * * * * $MONITOR_SCRIPT"

# Check if cron job already exists
if ! crontab -l 2>/dev/null | grep -q "$MONITOR_SCRIPT"; then
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job added: Monitor every 2 minutes"
else
    echo "✅ Cron job already exists"
fi

# Step 6: Start the service
echo "🚀 Starting $SERVICE_NAME service..."
systemctl start "$SERVICE_NAME"

# Step 7: Check service status
echo "📊 Service Status:"
systemctl status "$SERVICE_NAME" --no-pager

# Step 8: Verify service is running
sleep 5
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo ""
    echo "✅ SUCCESS! Auto-restart setup completed!"
    echo "🔄 Service will automatically restart if it crashes"
    echo "📊 Health monitoring runs every 2 minutes"
    echo ""
    echo "📋 Service Management Commands:"
    echo "   sudo systemctl status $SERVICE_NAME     # Check status"
    echo "   sudo systemctl restart $SERVICE_NAME    # Manual restart"
    echo "   sudo systemctl stop $SERVICE_NAME       # Stop service"
    echo "   sudo systemctl start $SERVICE_NAME      # Start service"
    echo ""
    echo "📊 Monitoring Commands:"
    echo "   sudo tail -f /var/log/lacasadetodos-monitor.log  # View monitor logs"
    echo "   sudo journalctl -u $SERVICE_NAME -f             # View service logs"
    echo ""
else
    echo ""
    echo "❌ Service failed to start. Check logs:"
    echo "   sudo journalctl -u $SERVICE_NAME -n 50"
    echo "   sudo systemctl status $SERVICE_NAME"
    exit 1
fi
