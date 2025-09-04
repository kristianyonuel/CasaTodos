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

# Initialize database
echo "Initializing NFL Fantasy League database..."
python3 -c "
import sqlite3
from werkzeug.security import generate_password_hash
import datetime

# Create database connection
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()

# Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# NFL Games table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS nfl_games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week INTEGER NOT NULL,
        year INTEGER NOT NULL,
        game_id TEXT UNIQUE,
        home_team TEXT NOT NULL,
        away_team TEXT NOT NULL,
        game_date TIMESTAMP NOT NULL,
        is_monday_night BOOLEAN DEFAULT FALSE,
        is_thursday_night BOOLEAN DEFAULT FALSE,
        home_score INTEGER,
        away_score INTEGER,
        is_final BOOLEAN DEFAULT FALSE
    )
''')

# User Picks table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_picks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_id INTEGER,
        selected_team TEXT NOT NULL,
        predicted_home_score INTEGER,
        predicted_away_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (game_id) REFERENCES nfl_games(id)
    )
''')

# Weekly Results table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weekly_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        week INTEGER,
        year INTEGER,
        correct_picks INTEGER DEFAULT 0,
        total_picks INTEGER DEFAULT 0,
        monday_score_diff INTEGER,
        is_winner BOOLEAN DEFAULT FALSE,
        points INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create default admin user
admin_hash = generate_password_hash('admin123')
cursor.execute('''
    INSERT OR IGNORE INTO users (username, password_hash, email, is_admin)
    VALUES (?, ?, ?, ?)
''', ('admin', admin_hash, 'admin@localhost.com', 1))

# Create test users
test_users = [
    ('player1', 'password123', 'player1@localhost.com'),
    ('player2', 'password123', 'player2@localhost.com'),
    ('player3', 'password123', 'player3@localhost.com')
]

for username, password, email in test_users:
    user_hash = generate_password_hash(password)
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, email, is_admin)
        VALUES (?, ?, ?, ?)
    ''', (username, user_hash, email, 0))

conn.commit()
conn.close()

print('Database initialized successfully!')
print('Default admin user: admin / admin123')
print('Test users: player1, player2, player3 / password123')
"

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
