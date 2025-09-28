#!/bin/bash
# Ubuntu Flask Deployment Script
# Run this on your Ubuntu server after cloning the repository

set -e  # Exit on any error

echo "🚀 Casa Todos Flask App - Ubuntu Deployment Script"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ ERROR: app.py not found. Please run this script from the CasaTodos directory."
    exit 1
fi

echo "📂 Current directory: $(pwd)"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install required system packages
echo "📦 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv sqlite3 git

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "🐍 Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Add gunicorn if not in requirements
echo "📦 Installing Gunicorn for production..."
pip install gunicorn

# Check Flask installation
echo "🔍 Verifying Flask installation..."
if python -c "import flask; print('✅ Flask import: OK')" 2>/dev/null; then
    echo "✅ Flask is properly installed"
else
    echo "❌ Flask import failed, attempting to install..."
    pip install Flask
fi

# Check database files
echo "🗄️  Checking database files..."
for db in "database.db" "nfl_fantasy.db"; do
    if [ -f "$db" ]; then
        size=$(stat -c%s "$db")
        echo "✅ $db: ${size} bytes"
    else
        echo "❌ $db: NOT FOUND"
    fi
done

# Test app import
echo "🧪 Testing Flask app import..."
if python -c "import app; print('✅ App import: OK')" 2>/dev/null; then
    echo "✅ Flask app imports successfully"
else
    echo "❌ Flask app import failed"
    exit 1
fi

# Check available ports
echo "🔌 Checking port availability..."
for port in 5000 8000 3000; do
    if ! lsof -i :$port >/dev/null 2>&1; then
        echo "✅ Port $port: Available"
    else
        echo "⚠️  Port $port: In use"
    fi
done

# Create systemd service file
echo "🔧 Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/casa-todos.service"
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Casa Todos NFL Fantasy App
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/.venv/bin
ExecStart=$CURRENT_DIR/.venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created at $SERVICE_FILE"

# Reload systemd and enable service
echo "🔄 Configuring systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable casa-todos

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 5000/tcp
echo "✅ Firewall configured for port 5000"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "📋 Next Steps:"
echo "1. Start the service: sudo systemctl start casa-todos"
echo "2. Check status: sudo systemctl status casa-todos"
echo "3. View logs: sudo journalctl -u casa-todos -f"
echo "4. Test app: curl http://localhost:5000/health"
echo ""
echo "🔧 Manual Testing (if needed):"
echo "1. Activate environment: source .venv/bin/activate"
echo "2. Run directly: python app.py"
echo "3. Run with Gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "🌐 Access your app at: http://your-server-ip:5000"
echo ""
echo "📝 For troubleshooting, check FLASK_CRASH_ANALYSIS_FOR_UBUNTU.md"

# Pull the latest changes
echo "📥 Pulling latest changes from git..."
git pull origin main

# Check if we're running in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Activating venv..."
    source venv/bin/activate || source env/bin/activate || echo "Please activate your virtual environment manually"
fi

# Install any new dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check database integrity
echo "🔍 Checking database integrity..."
python -c "
import sqlite3
conn = sqlite3.connect('nfl_fantasy.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
user_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM nfl_games WHERE week = 1')
game_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM user_picks WHERE game_id IN (SELECT id FROM nfl_games WHERE week = 1)')
pick_count = cursor.fetchone()[0]
print(f'Database Status:')
print(f'  Users: {user_count}')
print(f'  Week 1 Games: {game_count}')  
print(f'  Week 1 Picks: {pick_count}')
conn.close()
"

# Restart the application service
echo "🔄 Restarting lacasadetodos service..."

# Check if lacasadetodos service exists and restart it
if systemctl is-active --quiet lacasadetodos; then
    echo "Restarting lacasadetodos service..."
    sudo systemctl restart lacasadetodos
    sudo systemctl status lacasadetodos --no-pager
elif systemctl is-active --quiet nfl-fantasy; then
    echo "Restarting nfl-fantasy service..."
    sudo systemctl restart nfl-fantasy
    sudo systemctl status nfl-fantasy --no-pager
elif systemctl is-active --quiet casa-todos; then
    echo "Restarting casa-todos service..."
    sudo systemctl restart casa-todos
    sudo systemctl status casa-todos --no-pager
else
    echo "⚠️  No systemd service found. Setting up lacasadetodos service..."
    
    # Copy service file and start service
    sudo cp lacasadetodos.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable lacasadetodos
    sudo systemctl start lacasadetodos
    sudo systemctl status lacasadetodos --no-pager
    
    echo ""
    echo "📋 Manual restart options if needed:"
    echo "   Option A: Kill existing processes and restart"
    echo "   pkill -f 'python.*app.py' && nohup python app.py > app.log 2>&1 &"
    echo ""
    echo "   Option B: If using PM2"
    echo "   pm2 restart app"
    echo ""
    echo "   Option C: If using screen/tmux"
    echo "   # Kill existing screen session and start new one"
    echo "   screen -S nfl-fantasy -X quit"
    echo "   screen -dmS nfl-fantasy python app.py"
fi

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Your app should now be running with the Monday Night fixes:"
echo "   - Monday Night picks are now visible even when game is in progress"
echo "   - Weekly leaderboard shows accurate standings and all user picks"
echo "   - Expandable pick details with predicted vs actual scores"
echo "   - Proper Monday Night tiebreaker status display"
echo ""
echo "📊 You can verify the fixes by:"
echo "   1. Visiting /weekly_leaderboard/1 in your browser"
echo "   2. Checking that Monday Night picks are displayed"
echo "   3. Expanding user rows to see all pick details"
echo ""
echo "🎯 After tonight's Monday Night game finishes:"
echo "   - Final scores will be automatically updated"
echo "   - Weekly winner will be determined correctly"
echo "   - Leaderboard will show final accurate standings"
