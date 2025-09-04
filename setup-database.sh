#!/bin/bash

echo "La Casa de Todos - Database Setup Script for Ubuntu"
echo "==================================================="

# Update system packages
echo "Updating system packages..."
sudo apt update

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3 python3-pip sqlite3

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user Flask==2.3.3 Werkzeug==2.3.7 requests==2.31.0

# Create database directory if it doesn't exist
echo "Setting up database directory..."
mkdir -p /opt/lacasadetodos
cd /opt/lacasadetodos

# Copy application files
echo "Copying application files..."
cp -r ~/CasaTodos/* .

# Set permissions
echo "Setting permissions..."
chmod +x *.py
chmod +x *.sh

# Initialize enhanced database with new features
echo "Initializing enhanced NFL Fantasy League database..."
python3 -c "
import sqlite3
from werkzeug.security import generate_password_hash
import datetime

# Initialize enhanced database
from database import init_database
init_database()

print('Enhanced database initialized successfully!')
print('New features added:')
print('- User statistics tracking')
print('- Confidence point scoring')
print('- Social commenting system')
print('- Enhanced notifications')
print('- League season management')
print('- Performance optimizations')
"

# Create database backup
echo "Creating database backup..."
if [ -f "nfl_fantasy.db" ]; then
    cp nfl_fantasy.db "nfl_fantasy_backup_$(date +%Y%m%d_%H%M%S).db"
    echo "✓ Database backup created"
fi

# Set up database permissions
chmod 664 nfl_fantasy.db
echo "✓ Database permissions set"

# Check database creation
if [ -f "nfl_fantasy.db" ]; then
    echo "✓ Database created successfully"
    
    # Show database info
    echo "Database tables:"
    sqlite3 nfl_fantasy.db ".tables"
    
    echo "User accounts:"
    sqlite3 nfl_fantasy.db "SELECT username, is_admin FROM users;"
    
else
    echo "❌ Database creation failed"
    exit 1
fi

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/lacasadetodos.service > /dev/null <<EOF
[Unit]
Description=La Casa de Todos NFL Fantasy League
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/lacasadetodos
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable lacasadetodos

# Set up firewall
echo "Configuring firewall..."
sudo ufw allow 5000/tcp
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

echo ""
echo "Enhanced Setup completed successfully!"
echo "======================================"
echo "New Features Available:"
echo "- Confidence Point Scoring"
echo "- User Statistics Dashboard"  
echo "- Social Game Comments"
echo "- Advanced Notifications"
echo "- Season Management"
echo "- Performance Optimizations"
echo ""
echo "Database: /opt/lacasadetodos/nfl_fantasy.db"
echo "Backup: nfl_fantasy_backup_*.db"
echo ""

# ...existing code...

echo "To start the application:"
echo "  sudo systemctl start lacasadetodos"
echo ""
echo "To check status:"
echo "  sudo systemctl status lacasadetodos"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u lacasadetodos -f"
echo ""
echo "Access the application at:"
echo "  http://localhost:5000"
echo ""
echo "Default login:"
echo "  Username: admin"
echo "  Password: admin123"
    
else
    echo "❌ Database creation failed"
    exit 1
fi

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/lacasadetodos.service > /dev/null <<EOF
[Unit]
Description=La Casa de Todos NFL Fantasy League
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/lacasadetodos
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable lacasadetodos

# Set up firewall
echo "Configuring firewall..."
sudo ufw allow 5000/tcp
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

echo ""
echo "Setup completed successfully!"
echo "=============================="
echo "Database: /opt/lacasadetodos/nfl_fantasy.db"
echo "Service: lacasadetodos"
echo ""
echo "To start the application:"
echo "  sudo systemctl start lacasadetodos"
echo ""
echo "To check status:"
echo "  sudo systemctl status lacasadetodos"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u lacasadetodos -f"
echo ""
echo "Access the application at:"
echo "  http://localhost:5000"
echo ""
echo "Default login:"
echo "  Username: admin"
echo "  Password: admin123"
