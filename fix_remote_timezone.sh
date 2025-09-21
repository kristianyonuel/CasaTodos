#!/bin/bash
# Remote Server Fix Script
# Run this on your remote server to fix the timezone issues

echo "🔧 Fixing timezone display issues on remote server..."

# 1. Pull latest changes from main branch
echo "📥 Pulling latest changes..."
git fetch origin
git checkout main
git pull origin main

# 2. Check if timezone utilities exist
echo "🔍 Checking timezone utilities..."
if [ -f "utils/timezone_utils.py" ]; then
    echo "✅ utils/timezone_utils.py exists"
else
    echo "❌ utils/timezone_utils.py MISSING - this is the problem!"
    exit 1
fi

# 3. Test timezone import
echo "🧪 Testing timezone import..."
python3 -c "from utils.timezone_utils import convert_to_ast; print('✅ Import successful')" || {
    echo "❌ Import failed - check Python path"
    exit 1
}

# 4. Test timezone conversion
echo "🕒 Testing timezone conversion..."
python3 -c "
from datetime import datetime
from utils.timezone_utils import convert_to_ast
dt = datetime(2025, 9, 21, 17, 0, 0)  # 5 PM UTC
ast_dt = convert_to_ast(dt)
print(f'UTC: {dt}')
print(f'AST: {ast_dt}')
formatted = ast_dt.strftime('%I:%M %p AST')
print(f'Display: {formatted}')
if '01:00 PM AST' in formatted:
    print('✅ Timezone conversion working correctly')
else:
    print('❌ Timezone conversion failed')
    exit 1
"

# 5. Restart the Flask application
echo "🔄 Restarting Flask application..."
# Uncomment the line that applies to your server setup:
# sudo systemctl restart casa-todos-auto-restart
# pkill -f "python.*app.py"
# screen -S casa-todos -X quit; screen -dmS casa-todos python3 app.py

echo "✅ Remote server timezone fix completed!"
echo "🌐 Check your website - games should now show '01:00 PM AST' not '09:00 AM AST'"
