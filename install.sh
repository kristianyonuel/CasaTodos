#!/bin/bash
# CasaTodos NFL Fantasy - Ubuntu Quick Install Script
# Usage: curl -sSL https://raw.githubusercontent.com/kristianyonuel/CasaTodos/main/install.sh | bash

set -e  # Exit on any error

echo "🏈 CasaTodos NFL Fantasy - Ubuntu Installation"
echo "=============================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run this script as root"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
sudo apt install -y git python3.13 python3.13-venv python3.13-dev python3-pip curl wget

# Clone repository
echo "📥 Cloning repository..."
cd /home/$USER
if [ -d "CasaTodos" ]; then
    echo "ℹ️ CasaTodos directory exists, updating..."
    cd CasaTodos
    git pull origin main
else
    git clone https://github.com/kristianyonuel/CasaTodos.git
    cd CasaTodos
fi

# Set up Python environment
echo "🐍 Setting up Python environment..."
python3.13 -m venv .venv
source .venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up database
echo "🗃️ Setting up database..."
python3 setup_database.py

# Set permissions
chmod +x setup_ubuntu_service.sh 2>/dev/null || true

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   cd /home/$USER/CasaTodos"
echo "   source .venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "🌐 Then access: http://your-server-ip:5000"
echo ""
echo "👤 Default login:"
echo "   Username: admin"
echo "   Password: family123"
echo ""
echo "📖 For more options, see: UBUNTU_INSTALL_GUIDE.md"
