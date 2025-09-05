#!/bin/bash

# Quick Ubuntu Service Setup Script for /home/casa/CasaTodos
# La Casa de Todos NFL Fantasy League

echo "🏈 Setting up La Casa de Todos as Ubuntu Service"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from /home/casa/CasaTodos"
    exit 1
fi

echo "📍 Current directory: $(pwd)"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install required packages
echo "📦 Installing required packages..."
sudo apt install python3 python3-pip python3-venv sqlite3 -y

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Setup database
echo "🗄️ Setting up database..."
./venv/bin/python setup_database.py

# Set proper permissions for root service
echo "🔧 Setting permissions..."
chmod +x app.py
# Ensure venv is accessible by root
sudo chown -R root:root venv
# But keep the app directory owned by casa for easier maintenance
chown -R casa:casa /home/casa/CasaTodos
# Except for venv which needs root access for the service
sudo chown -R root:root /home/casa/CasaTodos/venv

# Create systemd service file
echo "⚙️ Creating systemd service file..."
sudo tee /etc/systemd/system/lacasadetodos.service > /dev/null <<EOF
[Unit]
Description=La Casa de Todos NFL Fantasy League
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/casa/CasaTodos
Environment=PATH=/home/casa/CasaTodos/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/home/casa/CasaTodos
ExecStart=/home/casa/CasaTodos/venv/bin/python /home/casa/CasaTodos/app.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lacasadetodos

# Security settings (relaxed for root user)
PrivateTmp=yes
ReadWritePaths=/home/casa/CasaTodos

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service
echo "✅ Enabling service to start on boot..."
sudo systemctl enable lacasadetodos

# Start service
echo "🚀 Starting La Casa de Todos service..."
sudo systemctl start lacasadetodos

# Check service status
echo "📊 Checking service status..."
sleep 2
sudo systemctl status lacasadetodos --no-pager

# Show service info
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo "Service Name: lacasadetodos"
echo "Status: $(sudo systemctl is-active lacasadetodos)"
echo "Enabled: $(sudo systemctl is-enabled lacasadetodos)"
echo ""
echo "📋 Management Commands:"
echo "  sudo systemctl start lacasadetodos    # Start service"
echo "  sudo systemctl stop lacasadetodos     # Stop service"
echo "  sudo systemctl restart lacasadetodos  # Restart service"
echo "  sudo systemctl status lacasadetodos   # Check status"
echo "  sudo journalctl -u lacasadetodos -f   # View logs"
echo ""
echo "🌐 Access your app at: http://localhost:5000"
echo "🌐 From network: http://$(hostname -I | awk '{print $1}'):5000"
echo ""

# Test if service is running
if sudo systemctl is-active --quiet lacasadetodos; then
    echo "✅ Service is running successfully!"
    echo "🏈 Your NFL Fantasy League is now live!"
else
    echo "❌ Service failed to start. Check logs with:"
    echo "   sudo journalctl -u lacasadetodos --since '5 minutes ago'"
fi
