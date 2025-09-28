#!/bin/bash
# Ubuntu Troubleshooting Commands for Flask Server Issues
# Run this if the Flask server isn't working properly

echo "🔍 Casa Todos Flask Server Troubleshooting"
echo "==========================================="
echo "Timestamp: $(date)"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ ERROR: app.py not found. Please run from CasaTodos directory."
    exit 1
fi

echo "📂 Working directory: $(pwd)"
echo ""

# System Info
echo "🖥️  SYSTEM INFORMATION"
echo "----------------------"
echo "OS: $(lsb_release -d 2>/dev/null | cut -f2 || uname -a)"
echo "Python: $(python3 --version)"
echo "Virtual env active: ${VIRTUAL_ENV:-'Not active'}"
echo ""

# Database Check
echo "🗄️  DATABASE STATUS"
echo "-------------------"
for db in database.db nfl_fantasy.db; do
    if [ -f "$db" ]; then
        size=$(stat -c%s "$db")
        perms=$(stat -c%A "$db")
        echo "✅ $db: ${size} bytes, permissions: $perms"
        
        # Quick DB test
        game_count=$(sqlite3 "$db" "SELECT COUNT(*) FROM nfl_games;" 2>/dev/null || echo "ERROR")
        echo "   Games in DB: $game_count"
    else
        echo "❌ $db: NOT FOUND"
    fi
done
echo ""

# Python Environment Check
echo "🐍 PYTHON ENVIRONMENT"
echo "---------------------"
if [ -d ".venv" ]; then
    echo "✅ Virtual environment exists"
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✅ Virtual environment is active"
    else
        echo "⚠️  Virtual environment not active - activating..."
        source .venv/bin/activate
    fi
else
    echo "❌ Virtual environment not found"
fi

echo "Python executable: $(which python3)"
echo "Pip executable: $(which pip)"
echo ""

# Module Tests
echo "📦 PYTHON MODULES"
echo "-----------------"
modules=("flask" "sqlite3" "werkzeug" "requests" "pytz" "reportlab")
for module in "${modules[@]}"; do
    if python3 -c "import $module" 2>/dev/null; then
        version=$(python3 -c "import $module; print(getattr($module, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "✅ $module: $version"
    else
        echo "❌ $module: NOT FOUND"
    fi
done
echo ""

# Flask App Test
echo "🌶️  FLASK APP TEST"
echo "------------------"
if python3 -c "import app; print('✅ App import successful')" 2>/dev/null; then
    echo "✅ Flask app imports without errors"
    
    # Test app initialization
    if python3 -c "import app; app.initialize_app(); print('✅ App initialization successful')" 2>/dev/null; then
        echo "✅ App initialization successful"
    else
        echo "❌ App initialization failed"
        echo "Error details:"
        python3 -c "import app; app.initialize_app()" 2>&1 | head -10
    fi
else
    echo "❌ Flask app import failed"
    echo "Error details:"
    python3 -c "import app" 2>&1 | head -10
fi
echo ""

# Service Status
echo "🔧 SERVICE STATUS"
echo "-----------------"
if systemctl is-active --quiet casa-todos; then
    echo "✅ Casa-todos service is running"
    echo "Service status:"
    systemctl status casa-todos --no-pager -l
else
    echo "❌ Casa-todos service is not running"
    echo "Last service logs:"
    sudo journalctl -u casa-todos --no-pager -n 10
fi
echo ""

# Port Check
echo "🔌 PORT STATUS"
echo "--------------"
ports=(5000 8000 3000 80)
for port in "${ports[@]}"; do
    if lsof -i :$port >/dev/null 2>&1; then
        process=$(lsof -i :$port | tail -n 1 | awk '{print $1}')
        echo "⚠️  Port $port: IN USE by $process"
    else
        echo "✅ Port $port: Available"
    fi
done
echo ""

# Network Test
echo "🌐 NETWORK TEST"
echo "---------------"
echo "Testing local connectivity..."
if curl -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ Flask app responds to HTTP requests"
else
    echo "❌ Flask app not responding on port 5000"
fi

if curl -s http://127.0.0.1:5000/health >/dev/null 2>&1; then
    echo "✅ App accessible via 127.0.0.1:5000"
else
    echo "❌ App not accessible via 127.0.0.1:5000"
fi
echo ""

# File Permissions
echo "📁 FILE PERMISSIONS"
echo "-------------------"
files=("app.py" "database.db" "nfl_fantasy.db" "requirements.txt" ".venv")
for file in "${files[@]}"; do
    if [ -e "$file" ]; then
        perms=$(stat -c%A "$file")
        owner=$(stat -c%U:%G "$file")
        echo "$file: $perms ($owner)"
    else
        echo "$file: NOT FOUND"
    fi
done
echo ""

# Recent Logs
echo "📝 RECENT LOGS"
echo "--------------"
echo "Last 5 service log entries:"
sudo journalctl -u casa-todos --no-pager -n 5 2>/dev/null || echo "No service logs available"
echo ""

# Suggested Actions
echo "🔧 SUGGESTED TROUBLESHOOTING ACTIONS"
echo "=====================================)"
echo "1. Restart service: sudo systemctl restart casa-todos"
echo "2. Check full logs: sudo journalctl -u casa-todos -f"
echo "3. Manual test: source .venv/bin/activate && python app.py"
echo "4. Kill processes on port 5000: sudo lsof -ti:5000 | sudo xargs kill -9"
echo "5. Check firewall: sudo ufw status"
echo "6. Test database: sqlite3 database.db 'SELECT COUNT(*) FROM nfl_games;'"
echo ""
echo "If issues persist, check FLASK_CRASH_ANALYSIS_FOR_UBUNTU.md for detailed analysis."